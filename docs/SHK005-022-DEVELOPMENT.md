PROJECT SHADOW — SHK-005 dev.2-r1 / Shadow 0.2.2
4 November 2026
Revision 1: Founder-requested UK category inclusion. Explicit UK labels now qualify
alongside EN / ENG / English; US and mixed-language exclusions remain unchanged.

STATUS
Development publication authorised; live status must be verified after deployment.
GO for controlled Development testing after distribution preparation.
NO-GO for Stable promotion or claims of completed Android visual parity.
No repository settings, deployment gates or release feeds were changed.

VISUAL CORRECTIONS
* Bundled images use Kodi's normal texture loader rather than background loading
  of relative paths. Namespaced textures and masks avoid skin-name collisions and
  previous cache entries. This addresses a source-supported likely cause of the
  missing icons; confirmation in native Kodi on Xbox remains required.
* Generated Lucent screens replace unsupported font20/font30 aliases with
  font13/font37, available in Estuary 21.2, and use font12 for compact navigation.
  Text shadows are disabled. Other skins may render these aliases differently.
* Empty Continue Watching has one concise panel and a complete Browse movies
  label. Empty cards/progress bars are hidden. Real progress is below captions.
  Controller links cover zero, one and two history entries.
* Reduced glass-edge brightness, button opacity and focus fill. Default backdrop
  is charcoal/silver. Guide cells have modest corners rather than pill shapes.
  Missing programme artwork has a neutral fallback, not invented programme art.
* Appearance reports when optional Pillow processing is unavailable. In that
  case selected artwork can still drive the backdrop, but it is NOT blurred.
  This does not reproduce Android's real-time glass shader.

ENGLISH MOVIES AND SERIES
The previous session downloaded the complete title feed before filtering.
The Lucent session now reads the small provider category listing first, then
requests explicitly labelled EN / ENG / English / UK categories using category_id for
both get_vod_streams and get_series. Search and favourites use this same session.
* Whole-token, case-insensitive labels; no substring matches such as French.
* US / unlabelled groups are not inferred to be English. Recognised mixed
  categories are excluded. There is NO automatic full-feed fallback.
* No English categories: stops with an explanation. Manual mapping UI is not
  included; ambiguous provider labels need a specific mapping once available.
* Sequential requests, cancellation and existing overall deadline. Progress
  displays the current English category and category count.
* Deduplication and atomic acceptance after all categories succeed. Failed or
  cancelled refreshes keep previous loaded data; account-switched results are
  rejected. Existing 30-minute in-session freshness is retained.
* If returned category IDs prove the provider ignored the filter, sync stops.
  The first oversized response cannot be prevented if the provider ignores API
  parameters. Rows without category IDs cannot independently confirm filtering.
* Provider English labels are NOT verified audio languages. English titles in
  unlabelled/mixed groups may be excluded.
* No new persistent offline cache or delta-sync protocol is included.
* Live TV, original account storage, permissions, credentials, PIN and playback
  are preserved. The real Xtream adapter's Series sync now follows the Founder's
  English-only request, superseding its previous all-language fetch behavior.

VERIFICATION
90 / 90 offline automated tests passed; see TEST-RESULTS.txt.
Checks include actual provider-adapter query construction with mocked transport,
English request scope, no full-feed fallback, duplicates, cancellation, partial
failure, account switching, invalid responses and a large foreign-category fixture.
No real provider credentials or streams were used.
Baseline fingerprints, Python 3.8 syntax, XML/asset validity, native-font aliases,
controller route graph, PIN/startup/playback regressions, history visibility and
missing-image-library fallback are covered.
Ten offline XML geometry proofs generated; Home empty/populated and Guide reviewed.
These use synthetic artwork and a substitute font. They are NOT Kodi screenshots
or proof of native rendering fidelity, animation smoothness or Xbox performance.
No Kodi executable or Xbox hardware was available in this environment.

PRESERVATION
Rehashed 37 files in the local pre-correction release snapshot.
Shadow .57 SHA-256:
581aa60e3c3b3b702b006829140f43567eb24ee83472e6722342de08b5d9700f
Published 0.2.0 rollback ZIP SHA-256:
9262896a78320b2f0e74e93bdf95bce1a224cac6bf4c47c927021018bf1fa51d
See BASELINE-PRESERVATION.json. Live hosting was not reverified or modified.
Historical artifacts and original hosting remain intact.

XBOX ACCEPTANCE AFTER DEVELOPMENT PUBLICATION
1. Confirm Shadow 0.2.2, close and reopen it.
2. Empty Home: no false progress, caption overlap or truncated Browse movies.
   Confirm five navigation icons and Search/Settings icons.
3. Populated Home: real resume position, separate captions/progress; navigate
   with zero, one and two history entries and with empty/populated favourites.
4. Check Guide readability, focus contrast, tabs and artwork fallback.
5. Open Movies and Series: confirm English-category progress and relevant titles;
   measure initial loading time. Check search/favourites, cancellation and refresh.
   No real-provider speedup or completeness is claimed until this test passes.
6. Test film/episode/live playback, restore, PIN, preferences, Back and repeated
   launches. Check missing-blur status in Appearance and artwork transitions.
7. Confirm startup animation remains optional, bounded and does not repeat when
   returning from playback. Check duplicate-launch prevention.

LOG DIAGNOSIS
Founder-provided traceback identifies service.xbmc.versioncheck calling
platform.uname, then subprocess and unavailable _winapi.CreateProcess on Xbox.
Disable that optional Kodi service as a workaround and confirm after restart.
Shadow source has no direct calls to that chain. Separate pvr.iptvsimple HTTP 403
responses remain unresolved; no provider access or credential validation performed.

REFERENCES
Kodi 21.2 source: WindowXML.cpp, GUITexture.cpp, TextureManager.cpp,
TextureCacheJob.cpp and addons/skin.estuary/xml/Font.xml.
https://github.com/xbmc/xbmc/tree/21.2-Omega
https://kodi.wiki/view/Texture_Attributes

DELIVERY
script.shadow-0.2.2.zip — application, not repository installer.
candidate-manifest.json — hash for every packaged application file.
SHA256SUMS.txt — application, manifest and source-delivery ZIP hashes.
Source-and-Delivery ZIP — source, tests, tools, report, results and labelled proofs.

Publishing manifest SHA256: e936229722f806214158095b5ea56f3f2e8c80d13fd1e13eac1311163bcd394a
Application SHA256: c8e8315a82d18e26b09030859f090649ec34371205af9f087dcbe51abf94871f
Install via existing Kodi source > development > script.shadow > script.shadow-0.2.2.zip.
Wait for update notification, fully quit/reopen Kodi, confirm 0.2.2.
Rollback: explicitly install retained 0.2.0, 0.1.0 or Stable .57 without clearing add-on data.
