# SHK-003 corrected candidate - final preparation

## Authority and status

On 4 November 2026 the Founder authorised integrating PR #4 into PR #3's preparation branch and adopted a solo-founder policy with zero required PR approvals. This supersedes the earlier independent-review requirement. Required PRs, checks, branch currency, blocked force pushes/deletion, no bypass and Founder environment approval remain required.

PR #4 was integrated into `deployment/shk-003-ready` by merge commit `cd8f20c74a6b12a1dfc382c6141e415654907dc0`. This is not a merge of PR #3 into main. No publication is authorised. The final PR #3 head and its successful `verify-production` run must be checked before separate Founder merge approval.

## Immutable distribution

- Candidate manifest SHA256: `0f900e33e81d9477ade16078830f16f0a2d2d9028a7625cbcd632102a7b57f7e`.
- .57 runtime SHA256: `581aa60e3c3b3b702b006829140f43567eb24ee83472e6722342de08b5d9700f`.
- Full staged-site manifest SHA256: `0029064a968b2fc5e9a48ea0761d642938a411742b12ecb95a9afc2f6f199af5`.
- All ten historical archive/checksum files and five legacy root files remain unchanged. The exported public site still contains 35 files.
- Stable / Tester is one combined feed advertising .57. Development has no application release. Both current repository installers are 0.1.1 and use the organisation URL.
- Historical 0.1.0 installers retain their original URLs; they are not the current bootstrap. The .53 archive and its historical engineering/account references remain unchanged.
- Production uses committed organisation files only; it does not download the personal source repository or an expiring migration artifact. Application functionality, licensing and Android parity are unchanged.

## Corrected publishing preparation

PR #4 replaces the Pages-upload composite's mutable nested action with a local checked tar packager and full-SHA `actions/upload-artifact`. The existing publication job remains full-SHA pinned. The installation guide now correctly selects the Stable installer directly from the `/kodi/` listing.

The settings checker now matches the existing Founder reviewer by stable GitHub account ID, rather than assuming the automation account is the Founder reviewer. It explicitly requires self-review prevention, no administrator bypass, a single main branch deployment rule, workflow-based Pages, HTTPS and the expected organisation URL with no custom domain.

The production verification job performs a read-only settings inspection from the same-repository preparation PR with `contents: read`, `actions: read` and `pages: read`. Inspection neither creates a deployment nor changes settings. Publication preflight still requires main and a dispatch actor different from the Founder reviewer. Failures stop the workflow; no broad PAT or protection bypass is used.

The suite contains seven deployment/integrity/context test methods and three artifact tests. It covers fifteen unsafe setting variants, wrong branch/actor/repository context, candidate mutations, immutable files, update-origin models and exact tar contents. These are distribution checks, not physical Kodi execution or a new application regression run.

## Current controls

The live Protect main ruleset was inspected after the Founder saved it: active on main, required PR, zero required approving reviews, stale-review dismissal, resolved conversations, deletion/force-push restrictions, required `verify-production` from GitHub Actions and strict up-to-date checks. The current connection cannot bypass. The Founder confirmed an empty bypass list; the limited ruleset response does not enumerate all bypass actors.

The Founder confirmed Pages Source = GitHub Actions, HTTPS enabled and no custom domain. The environment has a single Founder reviewer, self-review prevention enabled, administrator bypass disabled and main-only deployments with no tags. The read-only CI audit must additionally pass against those live settings on the final candidate.

Keep repository default workflow permissions read-only and the restricted action policy. The production tree contains only verification and manual publication workflows. Required action pins are:

- `actions/checkout@11d5960a326750d5838078e36cf38b85af677262`
- `actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02`
- `actions/deploy-pages@d6db90164ac5ed86f2b6aed7e0febac5b3c0c03e`

## Separate approval sequence

A. After final SHA, complete CI, live settings audit and branch currency are verified, request explicit Founder approval to merge PR #3 into main. Zero required GitHub review approvals does not grant autonomous merge permission.

B. After an authorised merge, recheck main and request separate publication approval. Only after B may the authorised automation account dispatch **Publish Founder-approved Shadow repository** on main with the exact manifest SHA above and `PUBLISH REVIEWED SHADOW CANDIDATE`. The Founder then approves `github-pages` using the configured reviewer account. Do not initiate the run as that same reviewer: self-review prevention must remain enabled.

Only the deployment job receives `pages: write` and `id-token: write`, after verification and the environment approval gate. Pushes, PR updates and merging PR #3 do not automatically publish. A successful read-only audit does not consume or replace the eventual Founder deployment approval.

## Distribution and Xbox acceptance

Website: `https://shadow-app-org.github.io/shadow-download/`.
Kodi source: `https://shadow-app-org.github.io/shadow-download/kodi/`.
The website root retains the legacy .53 landing page; use `/kodi/` for the current Stable installer.

After approved publication, verify each public file's HTTPS response, lack of redirects and exact SHA256. Use `delivery/tools/check_https.py` for the Kodi files and `delivery/config/legacy-hashes.json` for the five root files.

On Xbox, install official Kodi from Microsoft Store and confirm 21.x compatibility. With only the controller and on-screen keyboard, enable Unknown sources, add the HTTPS source, select `repository.shadow.stable-0.1.1.zip` directly, then choose **Install from repository > Shadow Stable / Tester > Program add-ons > Shadow**. No USB, computer or Developer Mode is required by this intended flow.

For old manual ZIP installs, explicitly select .57 from this repository if needed to establish update origin; preserve profiles. Use **Check for updates** and verify repository version 0.1.1. A future application update needs a separately approved higher version and actual Xbox acceptance; .57 alone cannot demonstrate that path. Keep Development disabled for casual testers. Full controller instructions are in `delivery/INSTALL.txt`.

## Rollback and hosting retention

Before publication, keep the candidate unmerged or undispatched and preserve existing hosting. If verification fails, fix it through reviewed preparation; do not remove gates. If deployment fails, inspect the live state before assuming it is unchanged.

After a bad publication, pause rollout and prepare an approved revert to the last accepted site's committed files and matching catalogues/checksums, retaining immutable archives. Use normal PR/checks, a separate merge decision and a separate environment-approved publication; never force-push main. There is no recorded prior accepted organisation deployment before this first release, so do not claim a one-click rollback exists.

Website rollback does not downgrade installed Kodi applications. A manual downgrade requires separate approval and a profile-preservation plan. Keep the original personal-account repository and hosting as a temporary fallback, verifying any fallback URL before use. Do not retire it until controller-only organisation installation and a future approved application update have passed physical Xbox testing.

## Evidence limits

The exact final SHA and run result are recorded in PR #3 after verification. Earlier reports' independent-review and missing-status-check blockers are superseded by the Founder's policy decision and saved ruleset. Historical personal references remain preserved; active public metadata is Shadow-branded. The repository-only validator cache and historical recovery documentation are excluded from the Pages export. No anonymity guarantee, live-publication claim or physical Xbox acceptance is implied.
