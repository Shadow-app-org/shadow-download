import hashlib
import json
from pathlib import Path
import shutil
import tarfile
import tempfile
import unittest

from package_pages import package
from verify_production import ROOT, MANIFEST
from prepare_pages import prepare

class PagesArtifactTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.site = self.root/'site'
        prepare(ROOT/'delivery/site', ROOT, self.site,
                json.loads((ROOT/'delivery/config/release-plan.json').read_text()),
                json.loads((ROOT/'delivery/config/legacy-hashes.json').read_text()), MANIFEST)
    def test_exact_artifact_contents(self):
        destination = self.root/'artifact.tar'
        self.assertEqual(package(self.site, destination), 35)
        expected = {p.relative_to(self.site).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in self.site.rglob('*') if p.is_file()}
        with tarfile.open(destination) as archive:
            self.assertTrue(all(m.isfile() and not m.uname and not m.gname for m in archive))
            actual = {m.name: hashlib.sha256(archive.extractfile(m).read()).hexdigest() for m in archive}
            self.assertEqual(expected, actual)
    def test_modified_and_extra_files_rejected(self):
        for mode in ['modified', 'extra', 'symlink']:
            with self.subTest(mode=mode):
                probe = self.root/mode
                shutil.copytree(self.site, probe)
                if mode == 'modified': (probe/'index.html').write_text('changed')
                if mode == 'extra': (probe/'unexpected.txt').write_text('extra')
                if mode == 'symlink': (probe/'link').symlink_to('index.html')
                with self.assertRaises(ValueError): package(probe, self.root/(mode+'.tar'))
    def test_unsafe_destination_rejected(self):
        with self.assertRaises(ValueError): package(self.site, self.site/'artifact.tar')
        destination = self.root/'existing.tar'
        destination.write_bytes(b'existing')
        with self.assertRaises(ValueError): package(self.site, destination)

if __name__ == '__main__': unittest.main()
