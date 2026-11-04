"""Regressions for the Xbox source-browsing failures; no Kodi runtime claimed."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from verify_production import ROOT
from source_indexes import kodi_entries, validate_indexes, write_indexes


class SourceIndexTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name) / 'kodi'
        shutil.copytree(ROOT / 'delivery/site/kodi', self.root)

    def test_controller_route_and_cached_repository_reads(self):
        validate_indexes(self.root)
        root_entries = kodi_entries((self.root / 'index.html').read_text())
        self.assertIn('stable/', root_entries)
        stable = self.root / 'stable'
        cached = kodi_entries((stable / 'index.html').read_text())
        self.assertIn('repository.shadow.stable-0.1.1.zip', cached)
        # Kodi caches the full directory before applying the ZIP display mask.
        # These reads must not be rejected as absent from the cached parent.
        for name in ['addons.xml', 'addons.xml.sha256', 'script.shadow/']:
            self.assertIn(name, cached)
        package_entries = kodi_entries((stable / 'script.shadow/index.html').read_text())
        for name in ['script.shadow-0.0.57.zip', 'script.shadow-0.0.57.zip.sha256']:
            self.assertIn(name, package_entries)

    def test_old_nested_link_is_invisible(self):
        old = '<ul><li><a href="stable/repository.shadow.stable-0.1.1.zip">repository.shadow.stable-0.1.1.zip</a></li></ul>'
        self.assertEqual(kodi_entries(old), [])
        (self.root / 'index.html').write_text(old)
        with self.assertRaises(ValueError): validate_indexes(self.root)

    def test_old_zip_only_listing_rejected(self):
        old = '<ul><li><a href="repository.shadow.stable-0.1.1.zip">repository.shadow.stable-0.1.1.zip</a></li></ul>'
        self.assertNotIn('addons.xml.sha256', kodi_entries(old))
        (self.root / 'stable/index.html').write_text(old)
        with self.assertRaises(ValueError): validate_indexes(self.root)

    def test_missing_nested_index_rejected(self):
        (self.root / 'stable/script.shadow/index.html').unlink()
        with self.assertRaises(ValueError): validate_indexes(self.root)

    def test_new_file_requires_listing_refresh(self):
        (self.root / 'stable/new-checksum.sha256').write_text('test')
        with self.assertRaises(ValueError): validate_indexes(self.root)
        write_indexes(self.root)
        validate_indexes(self.root)

    def test_unsafe_links_rejected(self):
        p = self.root / 'index.html'
        original = p.read_text()
        for link in ['../secret', '%2e%2e/secret', '//example.com/file', '/stable/', 'stable/?q=1']:
            with self.subTest(link=link):
                p.write_text(original + '<a href="' + link + '">' + link + '</a> ')
                with self.assertRaises(ValueError): validate_indexes(self.root)

    def test_regeneration_preserves_packages_and_is_deterministic(self):
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        write_indexes(self.root)
        after = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before, after)


if __name__ == '__main__': unittest.main()
