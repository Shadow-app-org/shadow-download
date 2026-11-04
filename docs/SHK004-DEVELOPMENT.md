# SHK-004 dev.1 - controlled Xbox test release

Founder authorised preparation and publication of the existing 0.1.0 candidate
on 4 November 2026. Development only; Stable remains 0.0.57. All previous
installers, historical archives and original hosting remain available.

Runtime SHA-256:
`7e537c3b67196282bee93d72d2e3e9dd1ae55f9cbb61af8837e016e888393605`

Publishing manifest SHA-256 (delivery/site/deployment-manifest.json):
`39cbd432f1d3832c11c1baf3f24f5d99a3cf7b42a5641a9afcc029c583310da7`

The 106-file runtime passed 48 offline application tests. Distribution checks
separately verify exact payloads, channel isolation, cached directory listings,
preservation and security gates. Native Xbox acceptance remains pending.
Private engineering bundles, Android source/signing material and user profiles
are excluded. The runtime ZIP contains the executable Python/XML add-on.

## Publication

Merge through the protected PR process only after verify-production passes at
the exact current, up-to-date head. Merge never publishes automatically.
Dispatch publish-pages.yml on main as the authorised operator account, not the
Founder reviewer. Enter the publishing manifest hash above and exactly:
`PUBLISH REVIEWED SHADOW CANDIDATE`.
The workflow validates HTTPS, Actions Pages, Founder-only environment approval,
self-review prevention, disabled bypass and main-only deployment policy.
The Founder then reviews the waiting github-pages deployment. Keep all gates.

## Controller-only test installation after publication succeeds

1. In Kodi, My add-ons > Program add-ons > Shadow: turn Auto-update off.
2. Back up personal lists/progress using existing Shadow Settings if available.
3. Add-ons > Install from zip file > your existing Shadow source.
4. Open development/ > script.shadow/ > script.shadow-0.1.0.zip.
5. Wait for the updated notification. Confirm 0.1.0, then launch Shadow.

Source: https://shadow-app-org.github.io/shadow-download/kodi/

Direct test folder:
https://shadow-app-org.github.io/shadow-download/kodi/development/script.shadow/

This is the same script.shadow add-on ID and profile: it replaces local .57,
not a side-by-side installation. Initial testing uses the exact ZIP with automatic
updates off. The Stable repository's normal update check should remain on .57.
Development repository metadata also offers 0.1.0 for explicitly selected testing.

Check Home cards, five-icon navigation, empty lists, Live TV categories/favourites,
saved-provider restoration/cancellation, 10-minute playback, movie/episode resume,
search, privacy shortcut, Stop/Back, restart persistence and account isolation.
Android animation, recovery-policy parity and licensing are outside this increment.

## Rollback

Quit the test build; keep automatic updates off. Install the original ZIP through
stable/ > script.shadow/ > script.shadow-0.0.57.zip. This is an explicit downgrade:
0.1.0 sorts above 0.0.57. Do not delete add-on data or clear Kodi data. Restore
personal backup only if needed. Stop and capture any downgrade refusal.
Future unattended updates must account for the higher test version number.

If publication fails, leave Stable and old hosting untouched and diagnose first.
Correct or withdraw only Development through the protected workflow if live test
files are wrong. Retain old hosting until physical install/update/rollback pass.
