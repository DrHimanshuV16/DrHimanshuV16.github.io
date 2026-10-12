#!/usr/bin/env python3
"""Read the Google Scholar profile and save it as data/scholar.json.

Standard library only, so the GitHub workflow needs no installs. Scholar has
no API; this reads the public profile page and each paper's detail page, with
pauses in between so it stays a polite, low-volume reader.

Scholar also turns away automated readers from shared cloud addresses, so being
refused is a normal outcome rather than a breakage. A CAPTCHA or an HTTP
429/403 is retried with a growing pause; if Scholar is still refusing, this
exits BLOCKED (75) and leaves the old JSON untouched, and the workflow treats
that as "nothing to do this week" instead of a failure. A page that is neither
a CAPTCHA nor the expected layout exits 1, because that means the scraper
itself needs updating.
"""
import html
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

BLOCKED = 75          # EX_TEMPFAIL: Scholar turned us away; try again next run
ATTEMPTS = 3
BACKOFF = (60, 180)   # seconds to wait before retries 2 and 3

USER = 'MD55-F8AAAAJ'
BASE = 'https://scholar.google.com'
OUT = Path(__file__).resolve().parent.parent / 'data' / 'scholar.json'
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0 Safari/537.36')


class TurnedAway(Exception):
    """Scholar served a CAPTCHA or throttled the request."""


def fetch_once(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Language': 'en-US,en;q=0.9'})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        if e.code in (403, 429, 503):
            raise TurnedAway(f'Scholar answered HTTP {e.code}') from None
        raise
    if 'gs_captcha' in body or 'unusual traffic' in body or 'id="recaptcha"' in body:
        raise TurnedAway('Scholar served a CAPTCHA page')
    return body


def get(url):
    for attempt in range(1, ATTEMPTS + 1):
        try:
            return fetch_once(url)
        except TurnedAway as e:
            if attempt == ATTEMPTS:
                print(f'{e}. Still refused after {ATTEMPTS} attempts; leaving data unchanged.',
                      file=sys.stderr)
                sys.exit(BLOCKED)
            wait = BACKOFF[attempt - 1]
            print(f'{e}. Waiting {wait}s before attempt {attempt + 1} of {ATTEMPTS}.', file=sys.stderr)
            time.sleep(wait)


def text(s):
    return html.unescape(re.sub(r'<[^>]+>', '', s)).strip()


def profile():
    pubs, start = [], 0
    while True:
        page = get(f'{BASE}/citations?user={USER}&hl=en&cstart={start}&pagesize=100&sortby=pubdate')
        if start == 0:
            name = re.search(r'<div id="gsc_prf_in">(.*?)</div>', page)
            stats = [text(x) for x in re.findall(r'<td class="gsc_rsb_std">(.*?)</td>', page)]
            if not name or len(stats) < 6:
                sys.exit('Scholar profile page did not have the expected layout; leaving data unchanged.')
        rows = re.findall(r'<tr class="gsc_a_tr">(.*?)</tr>', page, re.S)
        for row in rows:
            link = re.search(r'href="([^"]*citation_for_view=[^"]+)"[^>]*class="gsc_a_at">(.*?)</a>', row, re.S)
            grays = re.findall(r'<div class="gs_gray">(.*?)</div>', row, re.S)
            cites = re.search(r'class="gsc_a_ac gs_ibl"[^>]*>(\d*)<', row)
            year = re.search(r'class="gsc_a_h gsc_a_hc gs_ibl"[^>]*>(\d*)<', row)
            if not link:
                continue
            pubs.append({
                'id': html.unescape(link.group(1)).split('citation_for_view=')[1].split('&')[0],
                'title': text(link.group(2)),
                'authors': text(grays[0]) if grays else '',
                'venue_line': text(re.sub(r'<span class="gs_oph">.*?</span>', '', grays[1])) if len(grays) > 1 else '',
                'citations': int(cites.group(1)) if cites and cites.group(1) else 0,
                'year': int(year.group(1)) if year and year.group(1) else None,
            })
        if len(rows) < 100:
            break
        start += 100
        time.sleep(4)
    return text(name.group(1)), stats, pubs


def details(pid):
    page = get(f'{BASE}/citations?view_op=view_citation&hl=en&user={USER}&citation_for_view={pid}')
    fields = dict(
        (text(k), text(v)) for k, v in re.findall(
            r'<div class="gsc_oci_field">(.*?)</div><div class="gsc_oci_value"[^>]*>(.*?)</div>', page, re.S))
    link = re.search(r'<a class="gsc_oci_title_link" href="([^"]+)"', page)
    fields.pop('Total citations', None)
    fields.pop('Description', None)
    fields.pop('Scholar articles', None)
    return {'fields': fields, 'link': html.unescape(link.group(1)) if link else None}


def main():
    name, s, pubs = profile()
    old = {}
    if OUT.exists():
        old = {p['id']: p for p in json.loads(OUT.read_text()).get('publications', [])}
    for p in pubs:
        # Detail pages rarely change; only fetch ones not seen before.
        if p['id'] in old and old[p['id']].get('fields'):
            p['fields'], p['link'] = old[p['id']]['fields'], old[p['id']].get('link')
            continue
        time.sleep(5)
        p.update(details(p['id']))
    data = {
        'profile': f'{BASE}/citations?user={USER}&hl=en',
        'name': name,
        'fetched': time.strftime('%Y-%m-%d'),
        'citations': int(s[0]), 'citations_since': int(s[1]),
        'h_index': int(s[2]), 'h_index_since': int(s[3]),
        'i10_index': int(s[4]), 'i10_index_since': int(s[5]),
        'publications': pubs,
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
    print(f'{name}: {data["citations"]} citations, h-index {data["h_index"]}, {len(pubs)} publications')


if __name__ == '__main__':
    main()
