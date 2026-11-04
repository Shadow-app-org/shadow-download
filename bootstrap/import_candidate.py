"""One-time, hash-verified import from this organisation's own Actions artifact."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
artifact = Path(sys.argv[1]).resolve()
expected = json.loads((root/'bootstrap/expected-artifact.json').read_text())
for p in artifact.rglob('*'):
    if p.is_symlink(): raise ValueError('Symlink in migration artifact')
actual = {p.relative_to(artifact).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
          for p in artifact.rglob('*') if p.is_file()}
if actual != expected: raise ValueError('Artifact differs from reviewed complete inventory')
shutil.copytree(artifact/'delivery', root/'delivery')
for name in ['.nojekyll','README.md','SHA256SUMS.txt','index.html','script.shadow-0.0.53-dev.zip']:
    shutil.copyfile(artifact/name,root/name)
shutil.copyfile(artifact/'VERIFICATION.json',root/'MIGRATION-VERIFICATION.json')
shutil.copytree(root/'bootstrap/final',root,dirs_exist_ok=True)
for name in ['verify-recovery.yml','import-candidate.yml']:
    (root/'.github/workflows'/name).unlink(missing_ok=True)
shutil.rmtree(root/'bootstrap')
subprocess.run([sys.executable,'-B','tools/test_deployment.py'],cwd=root,check=True)
subprocess.run([sys.executable,'-B','tools/verify_production.py'],cwd=root,check=True)
shutil.rmtree(root/'_shadow_pages')
print('Verified self-contained files ready for a review branch; no publication.')
