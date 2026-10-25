#!/usr/bin/env python3
"""Collect NOAA/NWS marine forecast, alert, and NDBC buoy information.
Each source is validated separately: errors are disclosed rather than fabricated.
"""
import datetime as dt
import json
import pathlib
import urllib.request

UTC = dt.timezone.utc
now = dt.datetime.now(UTC).isoformat()
HEADERS = {'User-Agent': 'DelawareMarineWeatherCenter/1.0 (educational marine dashboard)', 'Accept': 'application/geo+json, application/json, text/plain, */*'}

def fetch(url, timeout=18):
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=timeout) as resp:
        return resp.read().decode('utf-8', errors='replace')

out = {'checked_at_utc': now, 'zones': {}, 'alerts': {}, 'buoys': {}}
for zone in ('ANZ430','ANZ431','ANZ454','ANZ455','ANZ630','ANZ631','ANZ632'):
    item = {'source': 'https://api.weather.gov/zones/forecast/' + zone + '/forecast'}
    try:
        raw = json.loads(fetch(item['source']))
        props = raw.get('properties', {})
        item.update({'ok': True, 'issued': props.get('issued') or props.get('updated'), 'updated': props.get('updated'), 'periods': props.get('periods', []), 'forecast': props.get('forecast') or props.get('text') or props.get('description')})
        if not item['forecast'] and not item['periods']:
            item['ok'] = False
            item['error'] = 'No forecast text in NOAA response'
    except Exception as exc:
        item.update({'ok': False, 'error': str(exc)[:200]})
    out['zones'][zone] = item

url = 'https://api.weather.gov/alerts/active?area=DE'
try:
    raw = json.loads(fetch(url))
    out['alerts'] = {'ok': True, 'source': url, 'items': [{'event': x.get('properties',{}).get('event'), 'headline':x.get('properties',{}).get('headline'), 'area': x.get('properties',{}).get('areaDesc'), 'expires': x.get('properties',{}).get('expires'), 'url': x.get('properties',{}).get('web') or x.get('id')} for x in raw.get('features', [])]}
except Exception as exc:
    out['alerts'] = {'ok': False, 'source': url, 'error': str(exc)[:200]}

# Marine zone-specific alerts: state-only alerts do not reliably cover coastal waters.
out['marine_alerts'] = {}
for zone in out['zones']:
    url = 'https://api.weather.gov/alerts/active?zone=' + zone
    try:
        raw = json.loads(fetch(url))
        events = []
        for feature in raw.get('features', []):
            p = feature.get('properties', {})
            events.append({'event':p.get('event'), 'headline':p.get('headline'),
                           'severity':p.get('severity'), 'expires':p.get('expires'),
                           'url':p.get('web') or feature.get('id')})
        out['marine_alerts'][zone] = {'ok':True,'items':events,'source':url}
    except Exception as exc:
        out['marine_alerts'][zone] = {'ok':False,'items':[],'error':str(exc)[:200],'source':url}

for station in ('44009','44014','44025','LWSD1'):
    url = f'https://www.ndbc.noaa.gov/data/realtime2/{station}.txt'
    try:
        lines = fetch(url).splitlines()
        out['buoys'][station] = {'ok': True, 'source': url, 'headers': lines[:2], 'latest': lines[2] if len(lines)>2 else None}
    except Exception as exc:
        out['buoys'][station] = {'ok': False, 'source': url, 'error': str(exc)[:200]}
path = pathlib.Path('data/latest.json')
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(out, indent=2))
print('Collected marine data at', now)
