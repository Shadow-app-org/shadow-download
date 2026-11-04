# SHK-003 production integration

This candidate makes Shadow organisation hosting self-contained. It does not merge, deploy, change GitHub settings, or establish Xbox acceptance. Licensing and Android parity remain separate roadmaps.

## Frozen distribution

- Migration PR #1 remains unchanged at `4d3db4a3f447a98ffc141acf695911e4d42d48d3`.
- Source: this organisation's verified Actions artifact `13309941261`, run `41805413025`.
- Candidate manifest SHA256: `0f900e33e81d9477ade16078830f16f0a2d2d9028a7625cbcd632102a7b57f7e`.
- .57 runtime SHA256: `581aa60e3c3b3b702b006829140f43567eb24ee83472e6722342de08b5d9700f`.
- `delivery/site` remains byte-for-byte identical to the verified artifact. Historical installers/checksums and all five legacy root files remain intact, including .53.
- Stable advertises .57 and repository installer 0.1.1. Development has repository installer 0.1.1 and no application release.
- Current feeds/installers use `https://shadow-app-org.github.io/shadow-download/kodi/`. Frozen 0.1.0 installer archives retain their original URLs; they are historical downloads, not the current bootstrap. Install 0.1.1 explicitly to adopt organisation hosting.
- Production verification and publishing read committed files only. They do not download the old personal repository or expiring migration artifact. The recovery script remains historical evidence, with no active recovery workflow.

## Transfer and verification

The temporary preparation PR uses GitHub's own artifact download and Git operations to create `deployment/shk-003-ready`. It validates every artifact file against a pinned inventory before using it. Its temporary `contents: write` token can create that review branch; no Pages or deployment permission is granted. It refuses to overwrite an existing destination branch. The final branch deletes the temporary importer and recovery workflow.

Local verification passed: five test methods covering twelve unsafe settings, four candidate mutations, bad approval/legacy hashes and four private-origin update scenarios. The staged output has 35 files; full-site manifest SHA256 is `0029064a968b2fc5e9a48ea0761d642938a411742b12ecb95a9afc2f6f199af5`. GitHub server-side import succeeded in run `41811290436`. Final production CI remains a separate check.

Production CI stages the complete site, validates hashes, URLs, packages and channel boundaries, tests candidate tampering, and tests incorrect deployment settings. The private-origin update model is a model only, not real Kodi execution. Existing runtime tests are not re-claimed as newly executed.

## Observed GitHub controls, 4 November 2026

Ruleset `26515183` is active on `main`: one PR approval, dismiss stale reviews, resolve review threads, prohibit deletion and force-push; current account cannot bypass. No required status-check rule was present in the observed ruleset. The classic branch-protection endpoint returned integration permission denied; this does not invalidate the readable ruleset evidence.

Pages, environment reviewers, action allowlists and repository default workflow permissions have NOT been independently inspected in this session. Do not mark deployment ready until the following settings are verified. The publisher fails closed if its runtime settings API check is denied or finds a mismatch; do not add a broad PAT or remove that guard to make it pass.

## Exact manual settings before merge/publication

Repository: `Shadow-app-org/shadow-download`.

1. **Settings → Pages → Build and deployment → Source:** GitHub Actions. **Enforce HTTPS:** enabled. No custom domain. Expected site: `https://shadow-app-org.github.io/shadow-download/`. Do not enable branch publication of the repository root, which contains engineering files.
2. **Settings → Environments → github-pages:** required reviewer `shadowapporg` only; disable administrator bypass. Deployment branches and tags: Selected branches and tags, one **branch** rule `main`, no wildcard/tag/PR rules.
3. Preserve existing self-review restrictions. If Prevent self-review is enabled, another authorised operator must dispatch the publication and the Founder approves it. Do not disable protection to solve a same-account approval block.
4. **Settings → Rules → Rulesets → Protect main:** retain existing controls and add required successful status check `verify-production` after it has run. Require branch to be up to date. No bypass actors. A separate authorised reviewer must approve a PR authored by `shadowapporg`; Founder deployment approval is a separate gate.
5. **Settings → Actions → General:** retain the restricted action allowlist and full SHA pinning. Required actions: `actions/checkout`, `actions/upload-artifact`, `actions/upload-pages-artifact`, `actions/deploy-pages`; the temporary importer also needs `actions/download-artifact`. Default workflow permissions: read repository contents. Keep Actions creating/approving pull requests disabled. Require approval for fork workflows. No PAT, cloud secret or paid hosting is needed.
6. Review final commit, CI and this report; obtain explicit Founder merge/publication approval. Merge only the final self-contained production PR. PR #1 is retained as historical evidence; do not merge the temporary transfer PR. Closing superseded PRs is housekeeping, not permission to deploy.

## Publication after approval

Run **Publish Founder-approved Shadow repository** from `main`. Enter the manifest SHA above and `PUBLISH REVIEWED SHADOW CANDIDATE`. The verify job checks live Pages/environment settings and builds an allowlisted site. Only the publish job receives `pages: write` and `id-token: write`, behind `github-pages` approval. Review its exact commit before approving. Neither a push nor a PR merge dispatches publication.

After publication, run:

```sh
python3 -B delivery/tools/check_https.py --site delivery/site --base https://shadow-app-org.github.io/shadow-download/kodi/
```

Require HTTPS with system certificate verification, HTTP 200, no redirects, and exact bytes for each catalogue, checksum, installer and .57 archive. Check the five legacy root URLs against `delivery/config/legacy-hashes.json` too. Record the deployment URL, commit, workflow run and full-site manifest before Xbox testing.

## Xbox acceptance

Follow `delivery/INSTALL.txt`: add the organisation `/kodi/` source, select **stable**, install `repository.shadow.stable-0.1.1.zip`, then install Shadow from **Shadow Stable / Tester → Program add-ons**. Verify existing settings survive, .57 launches and plays an authorised stream, and controller-only navigation works. For manual ZIP installs, explicitly select/reinstall .57 from this repository to establish origin. Do not uninstall or reset profiles. Validate repository 0.1.0 → 0.1.1 update and confirm all resulting feed URLs are organisation URLs. Test a future application update only with a separately approved higher-version candidate; .57 alone cannot demonstrate that path. Keep Development disabled for casual testers.

## Rollback

- Before the first publication: close/leave the candidate PR unmerged; the old site remains untouched. Do not delete old hosting or artifacts.
- If publication fails before deployment: cancel the run and fix the cause in a reviewed PR. A failed preparation job has no Pages write permission.
- After an unwanted deployment: stop further dispatches; prepare a reviewed revert on `main` to the last accepted site's exact committed bytes. Preserve immutable package URLs and profiles. Update the pinned manifest only through that reviewed rollback PR, verify CI/settings, then dispatch from `main` and require Founder environment approval again. Never force-push `main` or bypass reviews.
- For this organisation's first deployment, no previous accepted organisation deployment is recorded. Restoring the prior unpublished state requires an explicit Founder decision to unpublish the organisation site; the separate old host remains available as fallback. Do not claim a one-click rollback exists without a prior successful deployment.
- Kodi does not automatically downgrade to a lower application version. Any manual package downgrade needs a separate approved test and a profile backup; website rollback alone does not downgrade clients.

## Identity and limitations

Active distribution metadata uses Project Shadow and the organisation URL. The preserved .53 ZIP includes historical engineering files with a personal-account repository search reference. This is a known historical metadata exception, not a newly added identity disclosure; removing it would violate byte preservation. The .57 text scan found only Kodi’s generic `special://home/` path, not a personal home directory. Historical artifacts and recorded migration history are preserved, so this is not a promise of anonymity or removal of existing account linkage. The staged Pages export excludes scripts, workflow source and reports. Corrected installation/operations guides live in the repository and are not extra published paths. Required public attribution inside preserved archives must remain.

Final release blockers: Founder approval, a separate authorised PR reviewer, verified live settings and status-check protection, successful production CI, and post-publication HTTPS/Xbox acceptance. This report does not claim any of those outstanding steps has happened.
