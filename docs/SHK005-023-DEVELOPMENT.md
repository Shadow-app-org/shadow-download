# Shadow 0.2.3 development hotfix

The reported PIN keypad displayed Kodi menu names instead of digits, because
bare numeric XML labels are localisation IDs. All 20 numeric labels across the
PIN pad and connection keyboard now use $NUMBER[].

Modal surfaces now have an opaque rounded backing below their artwork, blocking
underlying page text even when artwork or Pillow is unavailable. The surrounding
scrim is darker, and the silver border is drawn above the artwork.

Validation: 95 offline application tests passed. Five new regression tests cover
literal digit labels, backing alpha, layer order, digit actions/delete, PIN length
and cancellation. These are XML/assets/behaviour tests, not native rendering.
Kodi/Xbox appearance, controller focus and update acceptance remain unverified.
No claim of completed Android visual parity is made.

Runtime changes relative to 0.2.2: LucentDialog.xml plus the two version fields.
EN/UK catalogue selection, provider preferences, licensing and playback unchanged.

Xbox acceptance: fully quit Kodi; install 0.2.3; wait for update notification;
fully quit/reopen. Confirm version, create/confirm/unlock PIN, enter/delete 0-9,
check masked input, check background text no longer bleeds into modal panel,
check Back cancels and returns focus, and verify connection keyboard digits.
Check both artwork-loaded and fallback appearances.

Founder authorised publishing this fix in this conversation on 2026-11-04.
Stable .57 and previous Development packages retained without overwriting.

Publishing manifest SHA256: 6e83b8fb7af014c15b7d2cf21e24f706b11f98371f2ba5a034484dee78a85672
Application SHA256: a6ff21646c597558a38577c9ad2166d035da551667fe971cc332fd86cee299c0
