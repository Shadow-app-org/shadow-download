"""Release-specific Development isolation, payload and controller-route checks."""
import ast
import io
import json
from pathlib import Path
import tempfile
import shutil
import unittest
import xml.etree.ElementTree as ET
import zipfile

from verify_production import ROOT, DEVELOPMENT, RUNTIME
import repository as r
from source_indexes import kodi_entries

class DevelopmentTests(unittest.TestCase):
    def setUp(self):
        self.site=ROOT/'delivery/site'
        self.plan=json.loads((ROOT/'delivery/config/release-plan.json').read_text())
    def test_only_development_advertises_candidate(self):
        for channel,version in [('stable','0.0.57'),('development','0.1.0')]:
            root=ET.parse(self.site/'kodi'/channel/'addons.xml').getroot()
            apps=[n.get('version') for n in root if n.get('id')=='script.shadow']
            self.assertEqual(apps,[version])
        self.assertFalse(self.plan['releases']['0.1.0']['stable_approved'])
    def test_exact_runtime_and_safe_contents(self):
        data=(self.site/'kodi/development/script.shadow/script.shadow-0.1.0.zip').read_bytes()
        self.assertEqual(r.digest(data),DEVELOPMENT)
        r.validate_package(data,'script.shadow','0.1.0',self.plan['dependencies'])
        provenance=json.loads((self.site/'kodi/provenance.json').read_text())
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            self.assertEqual(len(archive.namelist()),106)
            self.assertEqual({n:r.digest(archive.read(n)) for n in archive.namelist()},provenance['runtime_files']['0.1.0'])
            for name in archive.namelist():
                parts=Path(name).parts
                self.assertFalse(set(parts)&{'tests','tools','engineering','.signing','userdata','addon_data','__pycache__'})
                self.assertTrue(name.startswith('script.shadow/'))
                if name.endswith('.py'):ast.parse(archive.read(name),feature_version=(3,8))
                if name.endswith('.xml'):ET.fromstring(archive.read(name))
    def test_existing_artifacts_remain_byte_identical(self):
        preserved=json.loads((ROOT/'delivery/config/shk003-preserved.json').read_text())
        self.assertEqual(len(preserved),25)
        for name,digest in preserved.items():
            with self.subTest(path=name):self.assertEqual(r.digest((self.site/name).read_bytes()),digest)
        self.assertEqual(r.digest((self.site/'kodi/stable/script.shadow/script.shadow-0.0.57.zip').read_bytes()),RUNTIME)
    def test_controller_route_and_cached_checksum_reads(self):
        for directory,required in [('kodi',{'development/'}),('kodi/development',{'addons.xml','addons.xml.sha256','script.shadow/','repository.shadow.development-0.1.1.zip'}),('kodi/development/script.shadow',{'script.shadow-0.1.0.zip','script.shadow-0.1.0.zip.sha256'})]:
            entries=set(kodi_entries((self.site/directory/'index.html').read_text()))
            self.assertTrue(required<=entries)
    def test_development_cannot_promote_into_stable_without_approval(self):
        self.plan['channels']['stable']['releases']=['0.1.0']
        with self.assertRaises(ValueError):r.plan_check(self.plan)
    def test_wrong_channel_metadata_is_rejected_even_with_new_tree_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            site=Path(directory)/'site';shutil.copytree(self.site,site)
            p=site/'kodi/stable/addons.xml';p.write_bytes((site/'kodi/development/addons.xml').read_bytes())
            p.with_suffix('.xml.sha256').write_text(r.digest(p.read_bytes())+'\n')
            hashes=r.tree_hashes(site);hashes.pop('deployment-manifest.json')
            (site/'deployment-manifest.json').write_bytes(r.json_bytes(hashes))
            with self.assertRaises(ValueError):r.validate_site(site,self.plan)
    def test_private_origin_update_model_keeps_stable_at_57(self):
        feeds={'repository.shadow.stable':'0.0.57','repository.shadow.development':'0.1.0'}
        self.assertIsNone(r.update_model('0.0.57','repository.shadow.stable',feeds))
        self.assertEqual(r.update_model('0.0.57','repository.shadow.development',feeds),'0.1.0')

if __name__=='__main__':unittest.main()
