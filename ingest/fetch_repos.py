"""fetch_repos.py
Minimal ingestion helper: fetch README text from local files or URLs.
This is intentionally tiny: production ingestion should handle rate limits, retries, and many formats.
"""
import os
import requests
from urllib.parse import urlparse

def fetch_text_from_url(url: str) -> str:
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"[WARN] fetch failed for {url}: {e}")
        return ""

def read_local_file(path: str) -> str:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"[WARN] read failed for {path}: {e}")
        return ""

def fetch_readme(source: str) -> str:
    # If source looks like a URL, fetch; otherwise read local path
    p = urlparse(source)
    if p.scheme in ('http', 'https'):
        return fetch_text_from_url(source)
    # try common README filenames in directory
    if os.path.isdir(source):
        for name in ('README.md', 'readme.md', 'README.txt'):
            candidate = os.path.join(source, name)
            if os.path.exists(candidate):
                return read_local_file(candidate)
    # fallback to direct file
    return read_local_file(source)

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('Usage: python fetch_repos.py <path_or_url>')
        sys.exit(1)
    src = sys.argv[1]
    text = fetch_readme(src)
    print(text[:2000])
