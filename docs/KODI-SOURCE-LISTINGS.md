# SHK-003 Xbox source listing correction

The Founder confirmed repository installation, displayed Shadow version 0.0.57
and apparently normal operation on Xbox Series S / Kodi 21.2 on 4 November 2026.
This is a user-reported installation and launch check, not full runtime regression
coverage or proof of a future higher-version application update.

## Why fresh installation needed a workaround

The original `/kodi/` page linked to a nested ZIP using only its basename as
the label. Kodi's HTTP directory parser compares the decoded link and label;
the mismatch hid the ZIP. Browsing `/kodi/stable/` exposed the installer, but
that directory index advertised only the ZIP. Kodi caches the full directory
before applying the visible file mask and can reject a subsequent file read
when the cached parent omits that file. The device log reported a failed read
of `stable/addons.xml.sha256`, despite successful independent HTTPS retrieval.
Fully quitting Kodi and opening the repository before revisiting the ZIP source
allowed the repository to load and the installation to complete. This evidence
supports the incomplete-cache diagnosis; no on-device instrumentation was used.

Relevant Kodi 21.2 source:

- [HTTPDirectory.cpp](https://github.com/xbmc/xbmc/blob/21.2-Omega/xbmc/filesystem/HTTPDirectory.cpp): link/label equality.
- [Directory.cpp](https://github.com/xbmc/xbmc/blob/21.2-Omega/xbmc/filesystem/Directory.cpp): cache before masking.
- [DirectoryCache.cpp](https://github.com/xbmc/xbmc/blob/21.2-Omega/xbmc/filesystem/DirectoryCache.cpp): cached existence lookup.
- [File.cpp](https://github.com/xbmc/xbmc/blob/21.2-Omega/xbmc/filesystem/File.cpp): cached-parent missing-file rejection.

## Correction and verification

Generate complete immediate-child indexes for all six Kodi directories. Every
link has a matching filename or folder label. The source route becomes
`/kodi/` > `stable/` > `repository.shadow.stable-0.1.1.zip`. Include feeds,
checksums, historical files and package folders in the HTML even where Kodi's
ZIP selection dialog hides non-ZIP files. Generate indexes after retaining
historical packages so none are omitted from the cache.

The production validator rejects missing, incomplete, unsafe and Kodi-invisible
listings. Seven regression tests cover the two old failures, the controller
route, checksum availability in cached listings, missing nested indexes, added
files, unsafe links and deterministic regeneration. The parser/cache checks are
restricted models, not execution of Kodi. Both verification and manual
publication workflows run these tests alongside the existing eleven tests.

Only the three existing public indexes change; three nested indexes are added.
The candidate manifest changes accordingly. All existing ZIPs, checksum sidecars,
feed XML, provenance and release notes remain byte-for-byte unchanged. The five
legacy root files remain unchanged. The staged site grows from 35 to 38 files.
Historical provenance describes its original preparation state; this report
records the later physical acceptance without rewriting immutable artifacts.

## Release gates and retest

This correction requires separate Founder merge and publication approvals.
It does not change repository rules, deployment settings or workflow permissions.
Publication remains manual from main with the exact new manifest hash, explicit
confirmation text, security checks and the existing Founder environment gate.

After approved publication, verify every public file against the staged manifest.
On Xbox, fully quit Kodi once to discard any old cache, then browse the canonical
source, install repository 0.1.1 and immediately open Shadow Stable / Tester
without another restart. Confirm Shadow 0.0.57 remains available, install/select
it and check launch and existing settings. Do not reset Kodi or delete profiles.

A higher-version update test remains pending a separately approved application
release. No Android feature port or licensing change is included. Retain the
original hosting as fallback. If correction verification or deployment fails,
stop; preserve current hosting. If published indexes regress, prepare a protected
revert and obtain approval before manually republishing the verified prior
candidate. The current stable-source-plus-restart workaround remains available.

## Prepared candidate evidence

- Base main: `540fae983e769dee2aa70ac39f7a364b1ce576dc`.
- Local verification: all 18 tests passed; complete production staging passed.
- Candidate manifest SHA-256: `16a45b4ce9d9e790a51b58078cd85e58d4ad52caecce1a012b64c203a3a3b031`.
- Full staged-site manifest SHA-256: `9ee5511548fc7b2db26bd001c819dbdfa50481b6d7930c6d5d1febccaee25265`.
- Shadow .57 SHA-256: `581aa60e3c3b3b702b006829140f43567eb24ee83472e6722342de08b5d9700f`.
- Comparison against the prior 35-file site preserves all existing archive and checksum files and all five legacy root files.
- Corrected fresh-install Xbox retest and a future-version application update: pending.

Publication inputs after separate approval: select `main`, use the candidate
manifest above, and enter `PUBLISH REVIEWED SHADOW CANDIDATE`. Dispatch using
the release identity; the Founder then opens the run, selects Review deployments,
checks github-pages, and chooses Approve and deploy. Never bypass this gate.
