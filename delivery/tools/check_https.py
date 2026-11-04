"""Read-only post-publication download verification. TLS required; no redirect fallback."""
import argparse
import hashlib
import json
from pathlib import Path
import ssl
import urllib.request
from urllib.parse import urlsplit

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('Unexpected redirect; review final host and certificate before continuing')

def check(site, base):
    if urlsplit(base).scheme!='https':raise ValueError('HTTPS required')
    manifest=json.loads((site/'deployment-manifest.json').read_text())
    opener=urllib.request.build_opener(NoRedirect(),urllib.request.HTTPSHandler(context=ssl.create_default_context()))
    results=[]
    for rel,sha in manifest.items():
        if not rel.startswith('kodi/'):continue
        url=base+rel[len('kodi/'):]
        request=urllib.request.Request(url,headers={'User-Agent':'Shadow-Repository-Verification/0.1','Accept-Encoding':'identity'})
        with opener.open(request,timeout=30) as response:
            size=(site/rel).stat().st_size
            data=response.read(size+1)
            if response.status!=200 or len(data)!=size or hashlib.sha256(data).hexdigest()!=sha:raise ValueError('Public response does not match approved file: '+rel)
            results.append({'path':rel,'status':200,'sha256':sha,'tls':'system validation; no redirects'})
    return results

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--site',type=Path,required=True);p.add_argument('--base',required=True);a=p.parse_args()
    print(json.dumps(check(a.site,a.base),indent=2))
