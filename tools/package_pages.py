"""Create Pages artifact.tar from verified staged files, without publication."""
import hashlib
import json
from pathlib import Path
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
    with tarfile.open(destination, 'x', format=tarfile.USTAR_FORMAT) as archive:
        for name, p in files.items():
            info = tarfile.TarInfo(name)
            info.size = p.stat().st_size
            info.mode = 0o644
            info.uid = info.gid = info.mtime = 0
            with p.open('rb') as stream: archive.addfile(info, stream)
    return len(files)

if __name__ == '__main__':
    print('Packaged', package(sys.argv[1], sys.argv[2]), 'verified files; no deployment.')
