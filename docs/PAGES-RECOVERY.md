# SHK-003 Pages publication recovery

## Observed failure

Publication run https://github.com/Shadow-app-org/shadow-download/actions/runs/41818830990
failed in the Pages service after Founder environment approval on attempts 1 and 2.
Both attempts target main commit `19e4b9d81c070e93a8be7747fea8e8b502224901`.
The service accepted the deployment request, then returned only
`Deployment failed, try again later.` It did not identify a root cause.

The downloaded artifact `13315264595` contains one `artifact.tar`. All 35 files
match the approved staged site byte-for-byte. Its custom USTAR layout has no
directory entries, uses unprefixed paths, and assigns ownership and timestamps
to zero. GitHub's Linux Pages uploader instead archives the directory with GNU
tar, including the root and parent-directory entries and `./` paths.

Pages settings were rechecked: GitHub Actions source, HTTPS required, empty custom
domain. Founder approval succeeded; it is not the failing stage.

## Proposed compatibility change

Use the archive operation from GitHub's official Linux implementation:
https://github.com/actions/upload-pages-artifact/blob/main/action.yml

Retain the existing SHA-pinned upload action, explicit file allowlist and hash
checks. Reject links and special files before packaging and verify the resulting
archive against the approved inventory. Retain `.nojekyll` explicitly. The
archive container changes; the public file contents and paths do not.

This removes a packaging difference; it is not proof of the backend failure's
cause. If the standard archive still fails, stop retries and investigate GitHub
Pages service state/support without switching to branch publication or weakening
environment protection.

## Verification and release gates

- Regression check reproduces the missing root/directory entries on the prior
  packager and passes on the proposed packager.
- All 11 local test methods pass (7 safeguards/integrity + 4 archive tests).
- All 35 staged file hashes remain unchanged.
- Candidate manifest SHA-256:
  `0f900e33e81d9477ade16078830f16f0a2d2d9028a7625cbcd632102a7b57f7e`.
- Runtime `.57` SHA-256:
  `581aa60e3c3b3b702b006829140f43567eb24ee83472e6722342de08b5d9700f`.
- Full staged-site manifest SHA-256:
  `0029064a968b2fc5e9a48ea0761d642938a411742b12ecb95a9afc2f6f199af5`.
- Required PR verification must pass before merge. The earlier merge approval
  was limited to the previous commit; this correction requires Founder approval.
- A manual publication run and Founder environment approval remain required.
- No production or old-hosting change is part of this preparation.

After deployment succeeds, validate live HTTPS bytes and controller-only Xbox
installation/update behavior before retiring the original hosting.
