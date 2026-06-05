//! Agent entry point — mirror of agent/main.py.
//!
//! Loads config, starts keyboard capture, serves the web page, shows the systray icon, and
//! runs until interrupted. Runs as a standalone native binary (no bundled Python), outside
//! Ableton.
//!
//! Threading model: the systray needs native messages pumped on the MAIN thread (a hard
//! constraint on Windows and macOS), so the main thread runs the winit event loop that owns
//! the tray. The keyboard listener (its own hook + worker threads) and the web server (its own
//! tokio runtime thread) run in the background. Tray "Quit" exits the event loop, which tears
//! everything down.

// No console window: this is a resident background agent launched at logon (Startup shortcut)
// and on-click; a console flash every session would be wrong. Mirror of the PyInstaller
// no-console exe. Logging goes to the rotating file + (when attached) the parent console.
#![windows_subsystem = "windows"]

mod ableton_shortcuts;
mod action_catalog;
mod config;
mod foreground;
mod key_emitter;
mod keymap;
mod listener;
mod paths;
mod process_check;
mod runtime_state;
mod script_client;
mod settings;
mod shortcut_store;
mod single_instance;
mod tray;
mod version;
mod web;

use std::sync::Arc;

use config::{Binding, ShortcutConfig};
use script_client::ScriptClient;
use settings::{Settings, WEB_PORT};

fn main() {
    configure_logging();
    tracing::info!("agent version: {}", version::version());

    if !cfg!(windows) {
        tracing::error!("agent is Windows-only (foreground check is Win32)");
        return;
    }

    // `--open`: passed by the Start Menu / desktop shortcut ("click to launch", AHK style). We
    // open the config page in the browser; then the normal flow below starts the agent if it
    // isn't running yet, or exits via the mutex if it is (the resident keeps control). The
    // Startup shortcut at logon launches WITHOUT --open: no stray browser tab every session.
    if std::env::args().skip(1).any(|a| a == "--open") {
        tray::open_url(&format!("http://127.0.0.1:{WEB_PORT}/shortcuts"));
    }

    // One agent at a time: two instances = two keyboard hooks = doubled shortcut.
    if !single_instance::acquire() {
        tracing::info!("another agent instance is already running, exiting");
        return;
    }

    let settings = Settings::load();
    let client = Arc::new(ScriptClient::new(settings));
    let config = ShortcutConfig::new();

    tracing::info!("config: {}", paths::config_path().display());

    // Dispatch: `send_keys` is replayed locally (native Live shortcut, no HTTP); everything
    // else goes through the script's HTTP API unchanged. `held` is the modifier snapshot the
    // listener took at decision time.
    let dispatch = move |binding: &Binding, held: &std::collections::HashSet<String>| {
        if binding.action == "send_keys" {
            match binding.params.get("keys") {
                Some(keys) if !keys.is_empty() => key_emitter::send(keys, held),
                _ => tracing::warn!("send_keys binding without 'keys' param"),
            }
        } else {
            client.execute(binding);
        }
    };

    let mut listener = listener::ShortcutListener::start(config, dispatch);

    // Web server (SPA + /api + /status) on its own thread: blocks neither the event loop below
    // nor the listener.
    let mut web_server = web::WebServer::start();

    // Run the systray on the main thread's event loop. Blocks until Quit.
    run_event_loop();

    // Teardown after the event loop exits (Quit).
    tracing::info!("stopping");
    web_server.stop();
    listener.stop();
}

/// Logs to a rotating file (%APPDATA%\Protocol0\logs\agent.log) AND the console.
///
/// The file is the only diagnostic when the agent runs at logon (Startup shortcut) with no
/// console (no-console exe). The console layer is useful in a dev terminal and is a silent
/// no-op under the windowed exe with no console attached.
fn configure_logging() {
    use tracing_subscriber::layer::SubscriberExt;
    use tracing_subscriber::util::SubscriberInitExt;
    use tracing_subscriber::EnvFilter;

    let dir = paths::log_dir();
    let _ = std::fs::create_dir_all(&dir);

    // Rotating file: tracing-appender rotates daily; we keep it simple (the Python used a
    // size-based RotatingFileHandler, daily is an acceptable equivalent for an agent log).
    let file_appender = tracing_appender::rolling::daily(&dir, "agent.log");

    let filter = EnvFilter::try_from_default_env().unwrap_or_else(|_| EnvFilter::new("info"));

    tracing_subscriber::registry()
        .with(filter)
        .with(
            tracing_subscriber::fmt::layer()
                .with_writer(file_appender)
                .with_ansi(false),
        )
        .with(tracing_subscriber::fmt::layer().with_writer(std::io::stderr))
        .init();
}

/// Builds the winit event loop, the tray, and pumps until Quit. The tray menu events are
/// polled each iteration; Open config / Open releases open the browser, Quit exits.
#[cfg(windows)]
fn run_event_loop() {
    use tray_icon::menu::MenuEvent;
    use winit::application::ApplicationHandler;
    use winit::event_loop::{ActiveEventLoop, ControlFlow, EventLoop};

    struct App {
        tray: Option<tray::TrayHandles>,
    }

    impl ApplicationHandler for App {
        fn resumed(&mut self, _event_loop: &ActiveEventLoop) {}

        fn window_event(
            &mut self,
            _event_loop: &ActiveEventLoop,
            _id: winit::window::WindowId,
            _event: winit::event::WindowEvent,
        ) {
        }

        fn new_events(
            &mut self,
            event_loop: &ActiveEventLoop,
            cause: winit::event::StartCause,
        ) {
            // Build the tray once, on the first poll, when the loop is live (so the native
            // message target exists).
            if self.tray.is_none() && matches!(cause, winit::event::StartCause::Init) {
                self.tray = tray::build();
            }

            // Drain tray menu events.
            while let Ok(event) = MenuEvent::receiver().try_recv() {
                if let Some(tray) = &self.tray {
                    if event.id == tray.open_config_id {
                        tray::open_url(&tray::config_url());
                    } else if event.id == tray.open_releases_id {
                        tray::open_url(tray::RELEASES_URL);
                    } else if event.id == tray.quit_id {
                        tracing::info!("quit requested from tray");
                        event_loop.exit();
                    }
                }
            }
        }
    }

    let event_loop = match EventLoop::new() {
        Ok(el) => el,
        Err(e) => {
            tracing::error!("event loop init failed: {e}");
            return;
        }
    };
    // Poll so we keep draining MenuEvent::receiver() even with no window events.
    event_loop.set_control_flow(ControlFlow::Wait);

    let mut app = App { tray: None };
    if let Err(e) = event_loop.run_app(&mut app) {
        tracing::error!("event loop error: {e}");
    }
}

#[cfg(not(windows))]
fn run_event_loop() {}
