"""Recover the pinned Kodi distribution and prepare an unpublished migration."""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET

SOURCE_COMMIT = '9e0a21712188554566ba11da3472e05a26ddd454'
RUNTIME_SHA256 = '581aa60e3c3b3b702b006829140f43567eb24ee83472e6722342de08b5d9700f'
BASE_URL = 'https://shadow-app-org.github.io/shadow-download/kodi/'


def recover(source, output):
    source, output = Path(source).resolve(), Path(output).resolve()
    observed = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=source, text=True).strip()
    if observed != SOURCE_COMMIT:
        raise ValueError('Source commit differs from the reviewed recovery snapshot')
    if output.exists():
        raise ValueError('Output must not exist')
    spec = importlib.util.spec_from_file_location('repository', source/'delivery/tools/repository.py')
    r = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(r)
    old_plan = json.loads((source/'delivery/config/release-plan.json').read_text())
    r.validate_site(source/'delivery/site', old_plan)
    runtime_path = Path('kodi/stable/script.shadow/script.shadow-0.0.57.zip')
    runtime = (source/'delivery/site'/runtime_path).read_bytes()
    r.require(r.digest(runtime) == RUNTIME_SHA256, 'Unexpected .57 runtime archive')
    legacy = json.loads((source/'delivery/config/legacy-hashes.json').read_text())
    for name, expected in legacy.items():
        p = source/name
        r.require(p.is_file() and not p.is_symlink() and r.digest(p.read_bytes()) == expected,
                  'Legacy download verification failed: '+name)
    shutil.copytree(source/'delivery', output/'delivery')
    for name in legacy:
        shutil.copyfile(source/name, output/name)
    site = output/'delivery/site'
    plan = copy.deepcopy(old_plan)
    plan['base_url'] = BASE_URL
    plan['distribution_version'] = '0.1.1-dev.1'
    for channel, cfg in plan['channels'].items():
        cfg['version'] = '0.1.1'
        folder = site/'kodi'/channel
        repo = r.repo_manifest(plan, channel)
        blob = r.zip_bytes({cfg['id']+'/addon.xml': r.xml_bytes(repo)})
        r.validate_package(blob, cfg['id'], cfg['version'], plan['dependencies'])
        name = cfg['id']+'-'+cfg['version']+'.zip'
        for relative in [name, cfg['id']+'/'+name]:
            r.put(folder, relative, blob)
            r.put(folder, relative+'.sha256', (r.digest(blob)+'\n').encode())
        listing = ET.fromstring((folder/'addons.xml').read_bytes())
        listing.remove(next(a for a in listing if a.get('id') == cfg['id']))
        listing.insert(0, repo)
        data = r.xml_bytes(listing)
        (folder/'addons.xml').write_bytes(data)
        (folder/'addons.xml.sha256').write_text(r.digest(data)+'\n')
        html = (folder/'index.html').read_text()
        (folder/'index.html').write_text(html.replace('-0.1.0.zip', '-0.1.1.zip'))
    index = site/'kodi/index.html'
    index.write_text(index.read_text().replace('-0.1.0.zip', '-0.1.1.zip'))
    provenance_path = site/'kodi/provenance.json'
    provenance = json.loads(provenance_path.read_text())
    provenance.update(base_url=BASE_URL, distribution_version=plan['distribution_version'],
                      migration_source_commit=SOURCE_COMMIT, publication_approved=False,
                      xbox_accepted=False)
    provenance_path.write_bytes(r.json_bytes(provenance))
    notes = site/'kodi/RELEASE-NOTES.txt'
    notes.write_text(notes.read_text()+'\nSHK-003 migration candidate: 0.1.1 repository installers use '+BASE_URL+
                     '\nThe .57 runtime and historical archives remain unchanged. Publication and physical Xbox acceptance are pending.\n')
    (output/'delivery/config/release-plan.json').write_bytes(r.json_bytes(plan))
    manifest = site/'deployment-manifest.json'
    manifest.unlink()
    manifest.write_bytes(r.json_bytes(r.tree_hashes(site)))
    r.validate_site(site, plan)
    r.require((site/runtime_path).read_bytes() == runtime, '.57 runtime changed')
    old_manifest = json.loads((source/'delivery/site/deployment-manifest.json').read_text())
    retained = 0
    for name, expected in old_manifest.items():
        if name.endswith(('.zip', '.zip.sha256')):
            r.require(r.digest((site/name).read_bytes()) == expected, 'Historical archive changed: '+name)
            retained += 1
    rejected = []
    for mode in ['extra', 'missing', 'modified', 'symlink']:
        probe = output/('probe-'+mode)
        shutil.copytree(site, probe)
        if mode == 'extra': (probe/'unexpected.txt').write_text('unexpected')
        elif mode == 'missing': (probe/runtime_path).unlink()
        elif mode == 'modified': (probe/runtime_path).write_bytes(b'changed')
        else: (probe/'unexpected-link').symlink_to('kodi/index.html')
        try:
            r.validate_site(probe, plan)
        except ValueError:
            rejected.append(mode)
        else:
            raise ValueError('Validator accepted '+mode+' candidate')
        finally:
            shutil.rmtree(probe)
    # Full deployable preview includes verified legacy files, but has no deployment action.
    import sys
    sys.path.insert(0, str(source/'delivery/tools'))
    from prepare_pages import prepare
    prepare(site, source, output/'staged-site', plan, legacy, r.digest(manifest.read_bytes()))
    report = dict(source_commit=SOURCE_COMMIT, base_url=BASE_URL,
                  runtime_sha256=RUNTIME_SHA256, runtime_unchanged=True,
                  retained_archive_files=retained, preserved_legacy_files=len(legacy),
                  rejected_mutations=rejected, candidate_manifest_sha256=r.digest(manifest.read_bytes()),
                  publication_approved=False, xbox_accepted=False)
    (output/'VERIFICATION.json').write_bytes(r.json_bytes(report))
    # Refresh the delivery checksums after migration.
    sums = output/'delivery/SHA256SUMS.txt'
    sums.unlink()
    sums.write_text(''.join(r.digest(p.read_bytes())+'  '+p.relative_to(output/'delivery').as_posix()+'\n'
                            for p in sorted((output/'delivery').rglob('*')) if p.is_file()))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    recover(args.source, args.output)
