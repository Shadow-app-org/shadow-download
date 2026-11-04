"""Create Pages artifact.tar from verified staged files, without publication."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tarfile

def package(source, destination):
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if destination == source or source in destination.parents:
        raise ValueError('Artifact destination must be outside the staged site')
    if destination.exists():
        raise ValueError('Refusing to overwrite an artifact')
    files = {}
    for p in sorted(source.rglob('*')):
        if p.is_symlink() or not (p.is_file() or p.is_dir()):
            raise ValueError('Links and special files are forbidden')
        if p.is_file(): files[p.relative_to(source).as_posix()] = p
    manifest = 'full-site-manifest.json'
    expected = json.loads(files[manifest].read_text())
    actual = {name: hashlib.sha256(p.read_bytes()).hexdigest()
              for name, p in files.items() if name != manifest}
    if actual != expected:
        raise ValueError('Staging inventory does not match its verified manifest')
    if any(name.startswith(('.git/', '.github/', 'delivery/', 'tools/')) for name in files):
        raise ValueError('Engineering path in Pages artifact')
    # Match actions/upload-pages-artifact's Linux archive operation, including
    # the root/parent directories and ./ paths. Upload remains SHA-pinned in
    # the workflow, avoiding a composite action's mutable nested dependencies.
    # Keep .nojekyll: it is an explicitly approved legacy artifact.
    with destination.open('xb') as output:
        try:
            subprocess.run(['tar', '--dereference', '--hard-dereference',
                            '--directory', str(source), '-cf', '-',
                            '--exclude=.git', '--exclude=.github', '.'],
                           stdout=output, check=True)
        except Exception:
            destination.unlink(missing_ok=True)
            raise
    try:
        with tarfile.open(destination) as archive:
            members = archive.getmembers()
            if any(not (m.isfile() or m.isdir()) for m in members):
                raise ValueError('Links or special entries in Pages artifact')
            names = [m.name.removeprefix('./') for m in members if m.isfile()]
            observed = {m.name.removeprefix('./'): hashlib.sha256(archive.extractfile(m).read()).hexdigest()
                        for m in members if m.isfile()}
            approved = {**actual, manifest: hashlib.sha256(files[manifest].read_bytes()).hexdigest()}
            if len(names) != len(set(names)) or observed != approved:
                raise ValueError('Packaged files differ from verified staging inventory')
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    return len(files)

if __name__ == '__main__':
    print('Packaged', package(sys.argv[1], sys.argv[2]), 'verified files; no deployment.')
