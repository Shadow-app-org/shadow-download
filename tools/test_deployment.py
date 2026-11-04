"""Adversarial checks for the publication gate and immutable candidate."""
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

from check_deployment_settings import validate
from verify_production import ROOT, MANIFEST
sys.path.insert(0, str(ROOT / 'delivery/tools'))
import repository as r
from prepare_pages import prepare

class SettingsTests(unittest.TestCase):
    def setUp(self):
        self.env = {'can_admins_bypass': False,
                    'deployment_branch_policy': {'custom_branch_policies': True},
                    'protection_rules': [{'type': 'required_reviewers', 'reviewers':
                        [{'type': 'User', 'reviewer': {'id': 352272508}}]}]}
        self.policies = {'total_count': 1, 'branch_policies': [{'name': 'main', 'type': 'branch'}]}
        self.pages = {'build_type': 'workflow', 'https_enforced': True, 'cname': None,
                      'html_url': 'https://shadow-app-org.github.io/shadow-download/'}
    def test_valid_settings(self):
        validate(self.env, self.policies, self.pages)
    def test_unsafe_settings_rejected(self):
        for mode in ['no-review', 'other-reviewer', 'extra-reviewer', 'bypass', 'unrestricted',
                     'wildcard', 'tag', 'extra-policy', 'branch-pages', 'http', 'other-host', 'cname']:
            with self.subTest(mode=mode):
                e, b, p = copy.deepcopy((self.env, self.policies, self.pages))
                if mode == 'no-review': e['protection_rules'] = []
                if mode == 'other-reviewer': e['protection_rules'][0]['reviewers'][0]['reviewer']['id'] = 1
                if mode == 'extra-reviewer': e['protection_rules'][0]['reviewers'].append({'type':'User','reviewer':{'id':1}})
                if mode == 'bypass': e['can_admins_bypass'] = True
                if mode == 'unrestricted': e['deployment_branch_policy'] = None
                if mode == 'wildcard': b['branch_policies'][0]['name'] = '*'
                if mode == 'tag': b['branch_policies'][0]['type'] = 'tag'
                if mode == 'extra-policy': b['total_count'] = 2
                if mode == 'branch-pages': p['build_type'] = 'legacy'
                if mode == 'http': p['https_enforced'] = False
                if mode == 'other-host': p['html_url'] = 'https://example.com/'
                if mode == 'cname': p['cname'] = 'example.com'
                with self.assertRaises(AssertionError): validate(e, b, p)

class CandidateTests(unittest.TestCase):
    def test_tampering_rejected(self):
        plan = json.loads((ROOT/'delivery/config/release-plan.json').read_text())
        for mode in ['extra', 'missing', 'modified', 'symlink']:
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as d:
                site = Path(d)/'site'
                shutil.copytree(ROOT/'delivery/site', site)
                target = site/'kodi/stable/addons.xml'
                if mode == 'extra': (site/'extra.txt').write_text('unexpected')
                if mode == 'missing': target.unlink()
                if mode == 'modified': target.write_text('changed')
                if mode == 'symlink': (site/'unexpected').symlink_to(target)
                with self.assertRaises(ValueError): r.validate_site(site, plan)
    def test_bad_approval_and_legacy_rejected(self):
        plan = json.loads((ROOT/'delivery/config/release-plan.json').read_text())
        legacy = json.loads((ROOT/'delivery/config/legacy-hashes.json').read_text())
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                prepare(ROOT/'delivery/site', ROOT, Path(d)/'bad', plan, legacy, '0'*64)
            altered = dict(legacy)
            altered['index.html'] = '0'*64
            with self.assertRaises(ValueError):
                prepare(ROOT/'delivery/site', ROOT, Path(d)/'legacy', plan, altered, MANIFEST)
    def test_private_origin_model(self):
        self.assertIsNone(r.update_model('0.0.57', None, {'repository.shadow.stable':'0.0.58'}))
        self.assertIsNone(r.update_model('0.0.57', 'repository.shadow.stable', {'repository.shadow.development':'0.0.58'}))
        self.assertEqual(r.update_model('0.0.57', 'repository.shadow.stable', {'repository.shadow.stable':'0.0.58'}), '0.0.58')
        self.assertIsNone(r.update_model('0.0.58', 'repository.shadow.stable', {'repository.shadow.stable':'0.0.57'}))

if __name__ == '__main__': unittest.main()
