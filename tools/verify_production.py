"""Verify the frozen migration and stage it without network access or publication."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'delivery/tools'))
import repository as r
from prepare_pages import prepare

MANIFEST = '39cbd432f1d3832c11c1baf3f24f5d99a3cf7b42a5641a9afcc029c583310da7'
DEVELOPMENT = '7e537c3b67196282bee93d72d2e3e9dd1ae55f9cbb61af8837e016e888393605'
RUNTIME = '581aa60e3c3b3b702b006829140f43567eb24ee83472e6722342de08b5d9700f'
BASE = 'https://shadow-app-org.github.io/shadow-download/kodi/'

def verify(output):
    delivery = ROOT / 'delivery'
    site = delivery / 'site'
    plan = json.loads((delivery / 'config/release-plan.json').read_text())
    legacy = json.loads((delivery / 'config/legacy-hashes.json').read_text())
    r.require(plan['base_url'] == BASE, 'Unexpected production host')
    r.require(plan['channels']['stable']['releases'] == ['0.0.57'], 'Stable baseline changed')
    r.require(plan['channels']['development']['releases'] == ['0.1.0'], 'Unexpected Development candidate')
    r.require(plan['releases']['0.1.0']['stable_approved'] is False, 'Development is not Stable approved')
    development = site / 'kodi/development/script.shadow/script.shadow-0.1.0.zip'
    r.require(r.digest(development.read_bytes()) == DEVELOPMENT, 'Development candidate changed')
    preserved = json.loads((delivery / 'config/shk003-preserved.json').read_text())
    for name, digest in preserved.items():
        r.require(r.digest((site / name).read_bytes()) == digest, 'Previously published artifact changed: ' + name)
    for cfg in plan['channels'].values():
        r.require(cfg['version'] == '0.1.1', 'Installer version changed')
    runtime = site / 'kodi/stable/script.shadow/script.shadow-0.0.57.zip'
    r.require(r.digest(runtime.read_bytes()) == RUNTIME, '.57 runtime changed')
    expected = {}
    for line in (delivery / 'SHA256SUMS.txt').read_text().splitlines():
        digest, name = line.split('  ', 1)
        r.require(name not in expected, 'Duplicate checksum path')
        expected[name] = digest
    actual = {p.relative_to(delivery).as_posix(): r.digest(p.read_bytes())
              for p in delivery.rglob('*') if p.is_file()
              and p.name != 'SHA256SUMS.txt' and '__pycache__' not in p.parts}
    r.require(actual == expected, 'Delivery checksum inventory differs')
    prepare(site, ROOT, output, plan, legacy, MANIFEST)
    full = json.loads((Path(output) / 'full-site-manifest.json').read_text())
    observed = r.tree_hashes(Path(output))
    observed.pop('full-site-manifest.json')
    r.require(full == observed, 'Full staged site differs')
    result = {'candidate_manifest_sha256': MANIFEST, 'runtime_sha256': RUNTIME,
              'development_runtime_sha256': DEVELOPMENT, 'preserved_site_files': len(preserved),
              'legacy_files': len(legacy), 'staged_files': len(observed) + 1,
              'full_site_manifest_sha256': r.digest((Path(output)/'full-site-manifest.json').read_bytes()),
              'base_url': BASE, 'published': False, 'xbox_accepted': False}
    print(json.dumps(result, indent=2))
    return result

if __name__ == '__main__':
    verify(sys.argv[1] if len(sys.argv) == 2 else ROOT / '_shadow_pages')
