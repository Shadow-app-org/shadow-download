"""SHK-002 repository builder/validator. Standard library only; no network writes."""
import argparse
import ast
import copy
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from urllib.parse import urlsplit, unquote
import xml.etree.ElementTree as ET
import zipfile
from source_indexes import write_indexes, validate_indexes

ROOT = Path(__file__).resolve().parents[1]
EPOCH = (2026, 11, 3, 0, 0, 0)
ROOT_FILES = {'addon.py', 'addon.xml', 'privacy_shortcut.py', 'ARTWORK-CREDITS.txt'}
FORBIDDEN = {'.git', '.signing', 'engineering', 'addon_data', 'userdata', '__pycache__', 'node_modules'}
SECRET_PATTERNS = [rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
                   rb'gh[pousr]_[A-Za-z0-9]{30,}', rb'github_pat_[A-Za-z0-9_]{30,}',
                   rb'AKIA[0-9A-Z]{16}', rb'https?://[^\s/\"\x27<>]+:[^\s/@\"\x27<>]+@']

def require(ok, reason):
    if not ok: raise ValueError(reason)

def digest(data): return hashlib.sha256(data).hexdigest()

def json_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False)+'\n').encode()

def version(value):
    require(re.fullmatch(r'(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)', value), 'Use monotonically increasing numeric x.y.z application/repository versions')
    return tuple(map(int, value.split('.')))

def safe_name(name):
    p = PurePosixPath(name)
    require(name and not p.is_absolute() and '..' not in p.parts and '\\' not in name and ':' not in name, 'Unsafe path')
    require(not any(x in FORBIDDEN for x in p.parts), 'Private/development/profile path in public package')
    require(not any(x.startswith('.') for x in p.parts), 'Hidden path in package')
    require(p.suffix.lower() not in {'.keystore', '.pem', '.p12', '.pfx', '.db', '.sqlite', '.pyc'}, 'Sensitive/unwanted file type')

def scan(data, name):
    for pattern in SECRET_PATTERNS:
        require(not re.search(pattern, data), 'Credential/key pattern in '+name)

def zip_bytes(files):
    out = io.BytesIO()
    # ZIP_STORED avoids deflate-version differences across builders.
    with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_STORED) as z:
        for name, data in sorted(files.items()):
            safe_name(name)
            item = zipfile.ZipInfo(name, EPOCH)
            item.create_system = 3
            item.external_attr = 0o100644 << 16
            z.writestr(item, data)
    return out.getvalue()

def runtime_files(source):
    require(source.is_dir(), 'Source directory missing')
    result = {}
    for p in sorted(source.rglob('*')):
        require(not p.is_symlink(), 'Symlink in source')
        if not p.is_file(): continue
        rel = p.relative_to(source)
        if rel.parts[0] == 'engineering' or '__pycache__' in rel.parts or p.suffix == '.pyc': continue
        require(rel.as_posix() in ROOT_FILES or rel.parts[0] == 'resources', 'Unapproved source root file: '+str(rel))
        safe_name(rel.as_posix())
        data=p.read_bytes(); scan(data, rel.as_posix())
        if p.suffix == '.py': ast.parse(data, filename=str(rel), feature_version=(3,8))
        if p.suffix == '.xml': ET.fromstring(data)
        result['script.shadow/'+rel.as_posix()] = data
    require(ROOT_FILES <= {n.split('/',1)[1] for n in result}, 'Required runtime files missing')
    return result

def validate_package(blob, expected_id, expected_version, dependencies):
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        require(z.testzip() is None, 'ZIP CRC failed')
        names=z.namelist();require(len(names)==len(set(names)), 'Duplicate ZIP members')
        for info in z.infolist():
            safe_name(info.filename)
            require(PurePosixPath(info.filename).parts[0]==expected_id, 'Incorrect ZIP root')
            require((info.external_attr >> 16) & 0o170000 != 0o120000, 'ZIP symlink')
            scan(z.read(info), info.filename)
        addon=ET.fromstring(z.read(expected_id+'/addon.xml'))
        require((addon.get('id'), addon.get('version'))==(expected_id,expected_version),'Manifest identity mismatch')
        version(expected_version)
        for dep in addon.findall('./requires/import'):
            aid=dep.get('addon');need=dep.get('version','0.0.0')
            require(aid in dependencies and version(dependencies[aid])>=version(need), 'Unavailable/incompatible dependency: '+str(aid))
        for ext in addon.findall('extension'):
            if ext.get('library'): require(expected_id+'/'+ext.get('library') in names,'Missing entry point')
        return addon

def put(root, name, data):
    path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)

def repo_manifest(plan, channel):
    cfg=plan['channels'][channel];base=plan['base_url']+channel+'/'
    addon=ET.Element('addon',id=cfg['id'],version=cfg['version'],name=cfg['name'],**{'provider-name':'Project Shadow'})
    ext=ET.SubElement(addon,'extension',point='xbmc.addon.repository')
    directory=ET.SubElement(ext,'dir',minversion=plan['kodi_min'],maxversion=plan['kodi_max'])
    ET.SubElement(directory,'info',compressed='false').text=base+'addons.xml'
    ET.SubElement(directory,'checksum',verify='sha256').text=base+'addons.xml.sha256'
    ET.SubElement(directory,'datadir',zip='true').text=base
    ET.SubElement(directory,'hashes').text='sha256'
    meta=ET.SubElement(addon,'extension',point='xbmc.addon.metadata')
    ET.SubElement(meta,'summary',lang='en_GB').text=cfg['name']+' for Kodi 21'
    ET.SubElement(meta,'description',lang='en_GB').text=('Founder-approved tester packages. ' if channel=='stable' else 'Experimental engineering builds; not the stable tester channel. ')+ 'Install Shadow from this repository to establish its update origin. Installation is independent of future licence activation.'
    ET.SubElement(meta,'platform').text='all';ET.SubElement(meta,'license').text='All rights reserved'
    return addon

def xml_bytes(node): return ET.tostring(node, encoding='utf-8', xml_declaration=True)

def plan_check(plan):
    parsed=urlsplit(plan['base_url'])
    require(parsed.scheme=='https' and parsed.hostname and not parsed.username and not parsed.password and not parsed.query and not parsed.fragment and plan['base_url'].endswith('/'),'HTTPS base URL required')
    require(parsed.hostname.endswith('.github.io'), 'Hosting change requires reviewed configuration/validator update')
    require(set(plan['channels'])=={'stable','development'},'Both isolated channels required')
    require(plan['channels']['stable']['id']!=plan['channels']['development']['id'],'Repository identity collision')
    for channel,cfg in plan['channels'].items():
        require(cfg['id']=='repository.shadow.'+channel,'Unexpected repository identity')
        version(cfg['version'])
        require(len(cfg['releases'])==len(set(cfg['releases'])),'Duplicate channel release')
        for release in cfg['releases']:
            version(release);require(release in plan['releases'],'Unknown release')
            if channel=='stable': require(plan['releases'][release]['stable_approved'] is True and plan['releases'][release]['approval'],'Stable release lacks recorded approval')

def tree_hashes(root):
    return {str(p.relative_to(root)):digest(p.read_bytes()) for p in sorted(root.rglob('*')) if p.is_file()}

def build(plan, destination, commit, source_root=ROOT, previous=None):
    plan_check(plan);require(re.fullmatch('[a-f0-9]{40}',commit),'Exact source commit required')
    destination=Path(destination);require(not destination.exists() or not any(destination.iterdir()),'Output must be empty; prevents stale/private files')
    destination.mkdir(parents=True,exist_ok=True)
    packages={}; manifests={}; sources={}
    used=set(v for c in plan['channels'].values() for v in c['releases'])
    for v in sorted(used,key=version):
        rel=Path(plan['releases'][v]['source'])
        require(not rel.is_absolute() and '..' not in rel.parts,'Unsafe source path')
        files=runtime_files(source_root/rel)
        data=zip_bytes(files);addon=validate_package(data,'script.shadow',v,plan['dependencies'])
        packages[v]=data;manifests[v]=addon;sources[v]={n:digest(d) for n,d in files.items()}
    for channel,cfg in plan['channels'].items():
        directory='kodi/'+channel
        repo=repo_manifest(plan,channel);rid=cfg['id'];rv=cfg['version']
        rblob=zip_bytes({rid+'/addon.xml':xml_bytes(repo)})
        validate_package(rblob,rid,rv,plan['dependencies'])
        listing=ET.Element('addons');listing.append(repo)
        # Only current app version advertised; all approved historical package URLs retained.
        if cfg['releases']: listing.append(copy.deepcopy(manifests[max(cfg['releases'],key=version)]))
        for aid,v,blob in [(rid,rv,rblob)]+[('script.shadow',v,packages[v]) for v in cfg['releases']]:
            name=f'{directory}/{aid}/{aid}-{v}.zip'
            put(destination,name,blob);put(destination,name+'.sha256',(digest(blob)+'\n').encode())
        bootstrap=f'{rid}-{rv}.zip';put(destination,directory+'/'+bootstrap,rblob)
        put(destination,directory+'/'+bootstrap+'.sha256',(digest(rblob)+'\n').encode())
        index=xml_bytes(listing);put(destination,directory+'/addons.xml',index)
        put(destination,directory+'/addons.xml.sha256',(digest(index)+'\n').encode())
    put(destination,'.nojekyll',b'')
    notes='Shadow distribution '+plan['distribution_version']+'\nSource commit: '+commit+'\n\n'+'\n'.join(v+': '+plan['releases'][v]['notes'] for v in sorted(used,key=version))+'\n\nNo application functionality, licence enforcement or profile migration added. Repository package installation/update remains awaiting physical Xbox acceptance.\n'
    put(destination,'kodi/RELEASE-NOTES.txt',notes.encode())
    report={'schema':1,'distribution_version':plan['distribution_version'],'source_commit':commit,'application_source_commit':plan['application_source_commit'],'application_commit_kind':plan['source_commit_kind'],'baseline_original_sha256':plan['baseline_sha256'],'base_url':plan['base_url'],'channels':{c:{'id':v['id'],'versions':v['releases']} for c,v in plan['channels'].items()},'packages':{v:{'sha256':digest(data),'bytes':len(data)} for v,data in packages.items()},'runtime_files':sources,'publication_approved':False,'xbox_accepted':False}
    put(destination,'kodi/provenance.json',json_bytes(report))
    if previous:
        # Never rewrite or remove previously published immutable archives.
        for name,expected in previous.items():
            if name.endswith(('.zip','.zip.sha256')):
                safe_name(name)
                if not (destination/name).exists():
                    retained=source_root/'archive'/name
                    require(retained.is_file() and not retained.is_symlink() and digest(retained.read_bytes())==expected,'Missing retained immutable archive: '+name)
                    put(destination,name,retained.read_bytes())
                require((destination/name).is_file() and digest((destination/name).read_bytes())==expected,'Published immutable package removed/changed: '+name)
    write_indexes(destination / 'kodi')
    hashes=tree_hashes(destination)
    put(destination,'deployment-manifest.json',json_bytes(hashes))
    validate_site(destination,plan)
    return report

def validate_site(site, plan):
    site=Path(site);plan_check(plan)
    expected=json.loads((site/'deployment-manifest.json').read_text())
    actual=tree_hashes(site);actual.pop('deployment-manifest.json',None)
    require(actual==expected,'Deployment tree/hash mismatch (extra/missing/modified files)')
    for p in site.rglob('*'):require(not p.is_symlink(),'Symlink in deployment')
    for channel,cfg in plan['channels'].items():
        base=site/'kodi'/channel;raw=(base/'addons.xml').read_bytes()
        require((base/'addons.xml.sha256').read_text().strip()==digest(raw),'Catalogue checksum mismatch')
        listing=ET.fromstring(raw);ids=[x.get('id') for x in listing]
        require(len(ids)==len(set(ids)),'Duplicate indexed identity')
        require(set(ids)=={cfg['id']}|({'script.shadow'} if cfg['releases'] else set()),'Cross-channel/unexpected indexed package')
        for addon in listing:
            aid=addon.get('id');v=addon.get('version');file=base/aid/(aid+'-'+v+'.zip')
            blob=file.read_bytes();require(file.with_suffix('.zip.sha256').read_text().strip()==digest(blob),'Package checksum mismatch')
            actual_addon=validate_package(blob,aid,v,plan['dependencies'])
            require(xml_bytes(addon)==xml_bytes(actual_addon),'Catalogue differs from packaged manifest')
            if aid=='script.shadow': require(v==max(cfg['releases'],key=version),'Wrong channel version')
            else:
                directory=addon.find('./extension[@point="xbmc.addon.repository"]/dir')
                require(directory is not None,'Missing repository directory')
                for tag,tail in [('info','addons.xml'),('checksum','addons.xml.sha256'),('datadir','')]:
                    require(directory.find(tag).text==plan['base_url']+channel+'/'+tail,'Cross-channel URL')
                require(directory.find('checksum').get('verify')=='sha256' and directory.find('hashes').text=='sha256','Strong hashes required')
                require(directory.get('minversion')==plan['kodi_min'] and directory.get('maxversion')==plan['kodi_max'],'Wrong Kodi version range')
        for p in base.rglob('*.zip'):
            require(p.with_suffix('.zip.sha256').read_text().strip()==digest(p.read_bytes()),'Historical/bootstrap checksum mismatch')
        bootstrap=cfg['id']+'-'+cfg['version']+'.zip'
        require((base/bootstrap).read_bytes()==(base/cfg['id']/bootstrap).read_bytes(),'Bootstrap differs from update package')
    validate_indexes(site / 'kodi')
    return True

def update_model(installed, origin, feeds):
    """Restricted model of Kodi private-origin update rule; not Kodi execution."""
    candidate=feeds.get(origin)
    return candidate if origin and candidate and version(candidate)>version(installed) else None

def git_commit():
    require(not subprocess.check_output(['git','status','--porcelain','--untracked-files=normal'],cwd=ROOT).strip(),'Commit source changes before release build')
    return subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['build','validate']);parser.add_argument('--output',default=str(ROOT/'dist/site'));parser.add_argument('--previous-manifest');args=parser.parse_args()
    plan=json.loads((ROOT/'config/release-plan.json').read_text())
    if args.command=='build':
        previous=json.loads(Path(args.previous_manifest).read_text()) if args.previous_manifest else json.loads((ROOT/'config/published-packages.json').read_text())
        build(plan,Path(args.output),git_commit(),previous=previous)
    else:validate_site(Path(args.output),plan)
    print('SHK-002 '+args.command+' passed; not published or Xbox-accepted.')

if __name__=='__main__':main()
