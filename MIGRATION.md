# Shadow Kodi migration recovery

This PR recovers the distribution directly inside GitHub Actions, avoiding the connector's inability to transfer binary ZIP files.

Source: `Hallettash/shadow-download`, pinned to commit `9e0a21712188554566ba11da3472e05a26ddd454`.

The verification workflow prepares an unpublished candidate artifact with repository installers version 0.1.1 pointing to `https://shadow-app-org.github.io/shadow-download/kodi/`. The 0.0.57 application archive, historical repository archives and five legacy download files must remain unchanged.

Checks cover the original and migrated catalogues, archive checksums, installer URLs and identities, retained historical archives, legacy downloads, and rejection of extra, missing, modified and symlinked files. `VERIFICATION.json` records the candidate manifest hash.

The workflow has read-only repository access and uploads a review artifact. It does not deploy Pages or change the old repository. The generated publication template remains outside `.github/workflows` and cannot run. Final publication approval and physical Xbox acceptance remain pending.
