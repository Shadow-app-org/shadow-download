"""Complete immediate-child indexes for Kodi's HTTP directory cache."""
from html import escape, unescape
from pathlib import Path
import re
from urllib.parse import quote, unquote, urlsplit


def kodi_entries(document):
    """Restricted Kodi 21.2 HTTPDirectory model for our simple ASCII listings.

    Uses its anchor expression and decoded-name equality rule. This is a
    regression model, not execution of Kodi or its directory cache.
    """
    pattern = r'<a href="([^"]*)"[^>]*>\s*(.*?)\s*</a>(.+?)(?=<a|</tr|$)'
    entries = []
    for href, label, _ in re.findall(pattern, document, re.I | re.S):
        name = unescape(label.strip()).rstrip('/')
        decoded = unquote(unescape(href)).rstrip('/')
        if decoded not in ('', '..') and name == decoded:
            entries.append(unquote(unescape(href)))
    return entries


def children(directory):
    return {p.name + ('/' if p.is_dir() else '') for p in directory.iterdir()}


def write_indexes(kodi_root):
    root = Path(kodi_root)
    directories = [root] + sorted(p for p in root.rglob('*') if p.is_dir())
    for directory in directories:
        (directory / 'index.html').touch(exist_ok=True)
        relative = directory.relative_to(root).as_posix()
        title = 'Shadow for Kodi' if relative == '.' else 'Shadow / ' + relative
        guidance = ('Open stable/ and install repository.shadow.stable-0.1.1.zip. '
                    'Then use Install from repository > Shadow Stable / Tester > Program add-ons > Shadow.'
                    if directory == root else
                    'Use repository.shadow.stable-0.1.1.zip for Stable / Tester installation.'
                    if relative == 'stable' else
                    'Experimental channel; no application release is offered.'
                    if relative.startswith('development') else 'Published packages and checksums.')
        lines = ['<!doctype html>', '<html><head><meta charset="utf-8">',
                 '<title>' + escape(title) + '</title></head><body>',
                 '<h1>' + escape(title) + '</h1>', '<p>' + escape(guidance) + '</p>', '<ul>']
        for name in sorted(children(directory)):
            lines.append('<li><a href="' + quote(name, safe='/') + '">' + escape(name) + '</a></li>')
        lines.extend(['</ul>', '</body></html>', ''])
        (directory / 'index.html').write_text('\n'.join(lines), encoding='utf-8')


def validate_indexes(kodi_root):
    root = Path(kodi_root)
    for directory in [root] + sorted(p for p in root.rglob('*') if p.is_dir()):
        index = directory / 'index.html'
        if not index.is_file():
            raise ValueError('Missing Kodi directory index: ' + str(directory))
        document = index.read_text(encoding='utf-8')
        for href in re.findall(r'href="([^"]*)"', document):
            decoded = unquote(unescape(href))
            parsed = urlsplit(decoded)
            name = decoded.rstrip('/')
            if (parsed.scheme or parsed.netloc or parsed.query or parsed.fragment
                    or '/' in name or '\\' in name or name in ('', '.', '..')
                    or not (directory / name).exists()):
                raise ValueError('Unsafe or broken Kodi source link: ' + href)
        entries = kodi_entries(document)
        if len(entries) != len(set(entries)) or set(entries) != children(directory):
            raise ValueError('Incomplete or Kodi-invisible directory listing: ' + str(directory))
