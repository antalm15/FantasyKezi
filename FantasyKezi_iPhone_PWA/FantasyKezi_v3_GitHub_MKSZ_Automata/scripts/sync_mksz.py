#!/usr/bin/env python3
"""Conservative MKSZ fixture extractor. Never publish an unverified or incomplete week.

The HTML of the third-party site may change; failures are deliberate and keep
existing verified files intact. Usage: python scripts/sync_mksz.py [--week YYYY-MM-DD]
"""
import argparse
import datetime as dt
import json
import re
import sys
import unicodedata
from pathlib import Path

CLUBS = {
    'VESZ':['ONE Veszprém HC','Veszprém HC'],
    'SZEG':['OTP Bank-PICK Szeged','PICK Szeged'],
    'CSKK':['Csurgói KK'],
    'MTB':['MOL Tatabánya KC','MOL Tatabánya','Tatabánya KC'],
    'PLER':['PLER-Budapest','PLER Budapest'],
    'FTC':['FTC-Green Collect','Ferencvárosi TC','FTC'],
    'ETO':['ETO University HT'],
    'NEKA':['LIQUI MOLY NEKA','NEKA'],
    'GYON':['HE-DO B. Braun Gyöngyös','B. Braun Gyöngyös','Braun Gyöngyös'],
    'SZIG':['Szigetszentmiklósi KSK','Szigetszentmiklós'],
    'BFU':['Balatonfüredi KSE','Balatonfüred'],
    'DAB':['Bepelog Dabas KC','Dabas KC'],
    'BFR':['Budai Farkasok-Rév','Budai Farkasok'],
    'EGER':['QHB-Eger','Eger']
}
DATE = re.compile(r'(?<!\d)(20\d\d)\.(\d\d?)\.(\d\d?)\.?\s*(\d\d?:\d\d)?')
LEAGUE = re.compile(r'K\s*&\s*H\s+F[eé]rfi\s+Liga', re.I)


def norm(s):
    return ''.join(c for c in unicodedata.normalize('NFKD',s.lower()) if not unicodedata.combining(c))


def teams_in(text):
    t=norm(text)
    found=set()
    for code,aliases in CLUBS.items():
        for name in aliases:
            needle=norm(name)
            if re.search(r'(?<![a-z])'+re.escape(needle)+r'(?![a-z])',t):
                found.add(code)
                break
    return found


def extract_fixtures(page_text,week):
    """Parse chronological match blocks from the rendered *men's league* page.

    We only keep blocks explicitly labelled K&H Férfi Liga, containing exactly
    two known clubs, and dated inside the requested Monday-to-Sunday interval.
    Repeated clubs, contradictory blocks, or multiple matches for one team fail
    closed. A successfully extracted list is still PARTIAL, not a full schedule.
    """
    monday=dt.date.fromisoformat(week)
    if monday.weekday()!=0: raise ValueError('A hét kezdete hétfő legyen.')
    sunday=monday+dt.timedelta(days=6)
    markers=list(DATE.finditer(page_text))
    matches=[]
    seen=set()
    for i,m in enumerate(markers):
        y,mo,day=map(int,m.group(1,2,3))
        try: date=dt.date(y,mo,day)
        except ValueError: continue
        if not monday<=date<=sunday: continue
        end=markers[i+1].start() if i+1<len(markers) else len(page_text)
        block=page_text[m.start():min(end,m.start()+950)]
        # Some MKSZ pages show multiple competitions together. Reject others.
        if not LEAGUE.search(block) or re.search(r'K\s*&\s*H\s+N[oő]i\s+Liga',block,re.I):continue
        clubs=teams_in(block)
        if len(clubs)!=2: continue
        pair=tuple(sorted(clubs))
        if pair in seen:continue
        seen.add(pair)
        matches.append({'date':date.isoformat(),'home':pair[0],'away':pair[1]})
    # Home/away is deliberately not asserted: order in flattened text is not
    # a trustworthy signal. App only needs participant clubs, not sides.
    usage={}
    for match in matches:
        for club in (match['home'],match['away']):usage[club]=usage.get(club,0)+1
    if any(count>1 for count in usage.values()):
        raise ValueError('Ugyanaz a klub több mérkőzésben szerepel, kézi ellenőrzés kell.')
    return sorted(matches,key=lambda x:(x['date'],x['home']))


def get_mksz_page():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as e:raise RuntimeError('Telepítsd: pip install playwright; python -m playwright install chromium') from e
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        page=browser.new_page(locale='hu-HU',timezone_id='Europe/Budapest')
        page.goto('https://www.mksz.hu/minden-kezilabda',wait_until='domcontentloaded',timeout=55000)
        page.wait_for_timeout(5500)
        # Resolve the current men's league from the season selector instead of
        # inventing a season-specific competition ID.
        candidates=page.get_by_text('K&H Férfi Liga',exact=True)
        if candidates.count()==0:raise RuntimeError('Az MKSZ K&H Férfi Liga hivatkozása nem található.')
        candidates.first.click(timeout=12000)
        page.wait_for_timeout(5500)
        url=page.url
        if '/versenyek/felnottFerfiVersenyek/' not in url:
            raise RuntimeError('Nem a férfi liga versenyoldala nyílt meg: '+url)
        title=page.locator('body').inner_text(timeout=15000)
        if not re.search(r'K\s*&\s*H\s+F[eé]rfi\s+Liga',title,re.I):
            raise RuntimeError('Hiányzik a férfi liga megnevezése.')
        browser.close()
        return title,url


def run():
    arg=argparse.ArgumentParser()
    arg.add_argument('--week',default=None,help='Vizsgált hét hétfője, YYYY-MM-DD')
    arg.add_argument('--text-file',type=Path,help='Helyi próba-adat; nem publikál hiteles adatlapot')
    arg.add_argument('--output-dir',type=Path,default=Path('FantasyKezi_iPhone_PWA/data/weeks'))
    args=arg.parse_args()
    today=dt.datetime.now(dt.timezone(dt.timedelta(hours=2))).date()
    monday=today-dt.timedelta(days=today.weekday())
    week=args.week or monday.isoformat()
    if args.text_file:
        body=args.text_file.read_text(encoding='utf-8')
        source='local-test-file'
    else:
        body,source=get_mksz_page()
    matches=extract_fixtures(body,week)
    if not matches:
        print(f'Nem volt bizonyítható férfi liga mérkőzés ({week}); nincs adatközzététel.',file=sys.stderr)
        return 0
    payload={'schemaVersion':1,'league':'K&H Férfi Liga','week':week,
             'verified':not bool(args.text_file), 'complete':False,
             'checkedAt':dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z'),
             'sourceUrl':source,'matches':matches}
    args.output_dir.mkdir(parents=True,exist_ok=True)
    target=args.output_dir/(week+'.json')
    if args.text_file:
        print(json.dumps(payload,ensure_ascii=False,indent=2))
        print('Csak próbamód: a JSON-fájl NEM kerül mentésre.')
    else:
        target.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(f'{len(matches)} ellenőrzött részleges mérkőzés a {target} fájlba.')
    return 0


if __name__=='__main__':
    try:sys.exit(run())
    except Exception as e:
        print('MKSZ frissítési hiba (nem írunk fájlt):',e,file=sys.stderr)
        sys.exit(1)
