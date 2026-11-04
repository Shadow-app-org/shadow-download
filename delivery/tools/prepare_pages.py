"""Stage only verified release artifacts + preserved legacy downloads. No deployment."""
import argparse
import json
from pathlib import Path
import shutil
import repository as r

def prepare(candidate, existing, destination, plan, legacy, approved_hash):
    candidate=Path(candidate);existing=Path(existing);destination=Path(destination)
    r.require(r.digest((candidate/'deployment-manifest.json').read_bytes())==approved_hash,'Candidate does not match approved manifest')
    r.validate_site(candidate,plan)
    r.require(not destination.exists(),'Publish staging destination must not exist')
    for name,sha in legacy.items():
        r.require(name in {'.nojekyll','README.md','SHA256SUMS.txt','index.html','script.shadow-0.0.53-dev.zip'},'Unexpected legacy path')
        p=existing/name
        r.require(p.is_file() and not p.is_symlink() and r.digest(p.read_bytes())==sha,'Legacy preservation failed: '+name)
    shutil.copytree(candidate,destination)
    for name in legacy:shutil.copyfile(existing/name,destination/name)
    (destination/'legacy-preservation.json').write_bytes(r.json_bytes(legacy))
    # The candidate manifest covers the new delivery; the full-site manifest covers legacy too.
    (destination/'full-site-manifest.json').write_bytes(r.json_bytes(r.tree_hashes(destination)))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--candidate',required=True);p.add_argument('--existing',required=True);p.add_argument('--output',required=True);p.add_argument('--approved-sha',required=True);a=p.parse_args()
    config=Path(__file__).resolve().parents[1]/'config'
    prepare(a.candidate,a.existing,a.output,json.loads((config/'release-plan.json').read_text()),json.loads((config/'legacy-hashes.json').read_text()),a.approved_sha)
    print('Approved candidate and all five existing download-site files preserved. No deployment performed by this script.')
