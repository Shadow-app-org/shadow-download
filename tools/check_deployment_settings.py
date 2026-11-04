"""Read GitHub settings; fail closed unless the Founder gate is configured."""
import json
import os
import urllib.request

REPO = 'Shadow-app-org/shadow-download'

def validate(environment, policies, pages):
    rules = environment.get('protection_rules', [])
    reviewers = [x for r in rules if r.get('type') == 'required_reviewers'
                 for x in r.get('reviewers', [])]
    # Listing only the Founder prevents a different required reviewer satisfying the gate.
    assert len(reviewers) == 1 and reviewers[0].get('type') == 'User', 'Founder-only reviewer required'
    assert reviewers[0].get('reviewer', {}).get('id') == 352272508, 'Wrong Founder account'
    assert environment.get('can_admins_bypass') is False, 'Environment bypass must be disabled'
    branch = environment.get('deployment_branch_policy') or {}
    assert branch.get('custom_branch_policies') is True, 'Explicit main-only policy required'
    assert policies.get('total_count') == 1, 'Exactly one branch deployment policy required'
    policy = policies['branch_policies'][0]
    assert policy.get('name') == 'main' and policy.get('type') == 'branch', 'Only main may deploy'
    assert pages.get('build_type') == 'workflow', 'Pages must use GitHub Actions'
    assert pages.get('https_enforced') is True, 'HTTPS must be enforced'
    assert pages.get('html_url', '').rstrip('/') == 'https://shadow-app-org.github.io/shadow-download', 'Wrong Pages URL'
    assert pages.get('cname') is None, 'Unexpected custom domain'

def get(path):
    request = urllib.request.Request('https://api.github.com/repos/' + REPO + path,
        headers={'Authorization': 'Bearer ' + os.environ['GH_TOKEN'],
                 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)

if __name__ == '__main__':
    assert os.environ.get('GITHUB_REPOSITORY') == REPO, 'Unexpected repository'
    assert os.environ.get('GITHUB_REF') == 'refs/heads/main', 'Only main may publish'
    validate(get('/environments/github-pages'),
             get('/environments/github-pages/deployment-branch-policies'), get('/pages'))
    print('Founder reviewer, no bypass, main-only Pages workflow and HTTPS settings verified.')
