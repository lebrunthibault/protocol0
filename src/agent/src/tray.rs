//! Agent systray icon (the visible surface "this tool is running, here's Quit") — mirror of
//! agent/tray.py.
//!
//! Why a tray: the agent is a global-keyboard-hook background process — exactly the silhouette
//! of a keylogger. A visible icon + a one-click Quit turns the read "spyware" -> "a tool I run".
//! It's UI, not behaviour: it does not change the antivirus profile.
//!
//!   - left-click (default action) -> opens the config page in the browser;
//!   - right-click (menu)          -> status line (/status) + Open config + Open releases + Quit.
//!
//! tray-icon needs native messages pumped on the main thread (NSStatusItem on macOS, the
//! message loop on Windows), so the tray lives on the main thread's winit event loop (see
//! main.rs); this module just builds the icon + menu and exposes the menu item ids.

use tray_icon::menu::{Menu, MenuItem, PredefinedMenuItem};
use tray_icon::{Icon, TrayIcon, TrayIconBuilder};

use crate::settings::WEB_PORT;
use crate::web::status;

/// Config page opened on left-click and from the menu.
pub fn config_url() -> String {
    format!("http://127.0.0.1:{WEB_PORT}/shortcuts")
}

/// Releases page: a LINK opened in the browser, never a download+exec (keeps the AV profile
/// clean; updating stays a manual act).
pub const RELEASES_URL: &str = "https://www.protocol0.live/";

/// Labels for the 3 states status::compute() returns, for the non-clickable menu line.
fn state_label(state: Option<&str>) -> &'static str {
    match state {
        Some("ready") => "Connected to Ableton",
        Some("script_inactive") => "Ableton open - activate the remote script",
        Some("no_ableton") => "Ableton not running",
        _ => "Status unavailable",
    }
}

/// The menu item ids we match on when a MenuEvent fires (main.rs dispatches by id).
pub struct TrayHandles {
    pub _tray: TrayIcon,
    pub open_config_id: tray_icon::menu::MenuId,
    pub open_releases_id: tray_icon::menu::MenuId,
    pub quit_id: tray_icon::menu::MenuId,
}

/// Builds the systray icon + menu. Called on the main thread once the event loop is running.
pub fn build() -> Option<TrayHandles> {
    let menu = Menu::new();

    let open_config = MenuItem::new("Open config", true, None);
    // Status line: informative, disabled. Computed fresh at build; refreshed when the menu is
    // about to show (main.rs updates it on the MenuEvent loop tick).
    let status_state = status::compute();
    let status_item = MenuItem::new(
        state_label(status_state.get("state").and_then(|v| v.as_str())),
        false,
        None,
    );
    let open_releases = MenuItem::new("Open releases page", true, None);
    let quit = MenuItem::new("Quit", true, None);

    menu.append_items(&[
        &open_config,
        &status_item,
        &PredefinedMenuItem::separator(),
        &open_releases,
        &quit,
    ])
    .ok()?;

    let icon = load_icon();
    let tray = TrayIconBuilder::new()
        .with_tooltip("Protocol 0")
        .with_menu(Box::new(menu))
        .with_icon(icon)
        .build()
        .ok()?;

    tracing::info!("systray icon started");
    Some(TrayHandles {
        _tray: tray,
        open_config_id: open_config.id().clone(),
        open_releases_id: open_releases.id().clone(),
        quit_id: quit.id().clone(),
    })
}

/// Loads the "P" icon embedded in the binary (installer/assets/protocol0.ico, baked via
/// include_bytes!). Falls back to a solid square rather than crashing the tray (hence the
/// agent), like the Python tray.
fn load_icon() -> Icon {
    const ICO: &[u8] = include_bytes!("../../../installer/assets/protocol0.ico");
    match image_from_ico(ICO) {
        Some(icon) => icon,
        None => {
            tracing::warn!("tray icon could not be decoded; using a fallback square");
            let size = 64u32;
            let rgba = vec![40u8; (size * size * 4) as usize];
            Icon::from_rgba(rgba, size, size).expect("fallback icon")
        }
    }
}

/// Decodes the .ico bytes into a tray Icon (largest frame), via the `image` crate path
/// tray-icon exposes through from_rgba.
fn image_from_ico(bytes: &[u8]) -> Option<Icon> {
    // tray-icon doesn't decode .ico itself; use the `image` crate to get RGBA. We pull `image`
    // transitively is not guaranteed, so decode the ICO header minimally is overkill — instead
    // rely on the `image` crate which we add as a dependency for this.
    let img = image::load_from_memory(bytes).ok()?.to_rgba8();
    let (w, h) = img.dimensions();
    Icon::from_rgba(img.into_raw(), w, h).ok()
}

/// Opens a URL in the system browser (replaces webbrowser.open).
pub fn open_url(url: &str) {
    if let Err(e) = open::that(url) {
        tracing::warn!("failed to open {url}: {e}");
    }
}
