"""Read GitHub settings; fail closed unless the Founder gate is configured."""
import argparse
import json
import os
import urllib.request

REPO = 'Shadow-app-org/shadow-download'
FOUNDER_ACCOUNT_ID = 113293879

def validate(environment, policies, pages):
    rules = environment.get('protection_rules', [])
    reviewers = [x for r in rules if r.get('type') == 'required_reviewers'
                 for x in r.get('reviewers', [])]
    # Listing only the Founder prevents a different required reviewer satisfying the gate.
    assert len(reviewers) == 1 and reviewers[0].get('type') == 'User', 'Founder-only reviewer required'
    assert reviewers[0].get('reviewer', {}).get('id') == FOUNDER_ACCOUNT_ID, 'Wrong Founder account'
    reviewer_rules = [r for r in rules if r.get('type') == 'required_reviewers']
    assert len(reviewer_rules) == 1 and reviewer_rules[0].get('prevent_self_review') is True, 'Founder self-review prevention must remain enabled'
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

def check(inspect_only=False):
    assert os.environ.get('GITHUB_REPOSITORY') == REPO, 'Unexpected repository'
    if not inspect_only:
        assert os.environ.get('GITHUB_REF') == 'refs/heads/main', 'Only main may publish'
        actor = os.environ.get('GITHUB_ACTOR_ID', '')
        assert actor.isdigit() and int(actor) != FOUNDER_ACCOUNT_ID, 'Use a separate authorised operator to dispatch; Founder approves the environment'
    validate(get('/environments/github-pages'),
             get('/environments/github-pages/deployment-branch-policies'), get('/pages'))
    print('Founder reviewer, self-review prevention, no bypass, main-only Pages workflow and HTTPS settings verified. Read-only inspection; no deployment.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--inspect-only', action='store_true', help='Read and validate settings from a preparation branch; never publish')
    check(parser.parse_args().inspect_only)
