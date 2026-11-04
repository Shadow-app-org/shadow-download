# SHK-005 dev.1 — controlled Xbox visual acceptance

Founder authorised publication to the existing Development folder on 4 November 2026.
Application: 0.2.0. Same script.shadow ID and local profile; this is an in-place
update, not a separate installation. Stable remains 0.0.57; original 0.1.0,
repository installers, historical files and fallback hosting are preserved.

Runtime SHA-256: `9262896a78320b2f0e74e93bdf95bce1a224cac6bf4c47c927021018bf1fa51d`
Publishing manifest SHA-256: `64e97d50968e751b5041e907e5478566c7d371a82d75979b799f55eca26d2893`

75 offline application tests passed. Native Kodi/Xbox execution, exact visual
fidelity, controller timing and playback-overlay handoffs still need acceptance.
This release introduces artwork-responsive glass, custom dialogs/keyboard/PIN,
TV Guide/Favourites, movie shelves including New Releases, Series details and
persistent dock. Privacy is Coming soon. Startup service is optional; the
2.7-second native intro follows the approved Android white eclipse reference.
Kodi startup/system screens and file pickers remain platform boundaries.
No Android source, signing material, user profile or engineering archive ships.

## Protected publication
Merge only after verify-production passes at the current PR head. Dispatch
publish-pages.yml from main as the authorised operator with the manifest above
and `PUBLISH REVIEWED SHADOW CANDIDATE`. Founder approval remains required at
github-pages, with self-review prevention and administrator bypass disabled.

## Controller-only installation
1. Back up personal data; keep Shadow Auto-update off for this controlled test.
2. Exit Shadow. Kodi > Add-ons > Install from zip file > existing Shadow source.
3. Open development/ > script.shadow/ > script.shadow-0.2.0.zip.
4. Wait for the updated notification and confirm version 0.2.0.
5. Fully Quit Kodi via Xbox, reopen, and check one Shadow launch and one intro.

Source: https://shadow-app-org.github.io/shadow-download/kodi/
Folder: https://shadow-app-org.github.io/shadow-download/kodi/development/script.shadow/
The Stable repository update check intentionally still advertises .57.

## Acceptance
Compare every approved screen on Xbox: glass, typography, artwork, focus and dock.
Check TV Guide scrolling beyond five channels, correct live selection, long
collections, filters, Series seasons/episodes, and preserved favourites/history.
Create and verify the four-digit Connection PIN; test cancel, failures and lockout.
Test startup Off/On, intro skip/Off, repeated opening, restart/quick resume,
playback-to-Home, audio/subtitles, Stop/Back and Xbox Home. Watch for Kodi OSD
flashes. Verify provider restoration and sustained playback. Missing artwork
must degrade safely. No automated test substitutes for this hardware acceptance.

## Rollback
Disable automatic opening if needed, exit Shadow, and explicitly install retained
0.1.0 from this folder, or stable/script.shadow/script.shadow-0.0.57.zip. Do not
uninstall/clear add-on data. Keep old hosting until installation/update/rollback
passes. Do not promote this candidate to Stable before Founder acceptance.
