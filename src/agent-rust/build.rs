//! Build script: embed the "P" icon as a PE resource on Windows.
//!
//! The PyInstaller spec added installer/assets/protocol0.ico as a "data" so the exe carried
//! the badge (Explorer, Add-Remove Programs) and the systray could load it. Here we bake it
//! straight into the executable's resources via winres — no _MEIPASS unpacking. The systray
//! loads the same .ico at runtime via include_bytes! (see tray.rs), so the icon ships once in
//! the binary and shows everywhere.
//!
//! The icon lives at repo-root: installer/assets/protocol0.ico. This crate is at
//! src/agent-rust/, so the path back to it is ../../installer/assets/protocol0.ico.

fn main() {
    // Inject the repo-root VERSION as a compile-time env var (P0_VERSION) that version.rs reads
    // via env!. We do it through build.rs (not include_str! in the source) so the rerun-if-changed
    // trigger actually forces a rebuild when /commit bumps VERSION — otherwise cargo wouldn't
    // track a file outside the crate dir and the exe would report a stale version.
    println!("cargo:rerun-if-changed=../../VERSION");
    let version = std::fs::read_to_string("../../VERSION")
        .map(|s| s.trim().to_string())
        .unwrap_or_else(|_| "0.0.0".to_string());
    println!("cargo:rustc-env=P0_VERSION={version}");

    #[cfg(windows)]
    {
        let ico = "../../installer/assets/protocol0.ico";
        // Rebuild if the icon changes (generate_icon.py regenerates it each build).
        println!("cargo:rerun-if-changed={ico}");

        let mut res = winres::WindowsResource::new();

        // PE metadata: this is the friendly name Task Manager, Explorer's Details tab, and the
        // installer's Add-Remove entry show. Without these, winres derives them from the crate
        // name ("protocol0-agent") and stamps version 0.0.0. We pin the user-facing name to
        // "Protocol 0" and the real version, so the process reads "Protocol 0", not the crate id.
        res.set("FileDescription", "Protocol 0");
        res.set("ProductName", "Protocol 0");
        res.set("OriginalFilename", "Protocol0.exe");
        res.set("InternalName", "Protocol0");
        res.set("CompanyName", "Thibault Lebrun");
        res.set("LegalCopyright", "Thibault Lebrun");
        res.set("FileVersion", &version);
        res.set("ProductVersion", &version);

        if std::path::Path::new(ico).exists() {
            res.set_icon(ico);
        } else {
            println!("cargo:warning=icon not found at {ico}; building without embedded badge");
        }

        if let Err(e) = res.compile() {
            // Don't fail the build over a resource issue; warn and continue (the exe still works,
            // just without the embedded badge/metadata as PE resources — the systray still loads
            // the .ico via include_bytes!).
            println!("cargo:warning=failed to embed PE resources: {e}");
        }
    }
}
