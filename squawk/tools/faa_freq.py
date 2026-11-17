"""Convert FAA NASR FRQ.csv + ATC_BASE.csv into Squawk's airports/freq/<letter>.json.

US airports get an object: {"f": [[type, desc, MHz, sector?], ...], "t": tower call,
"a": approach call, "d": departure call, "h": tower hours}. Non-US airports keep the
OurAirports list format. FAA data is public domain.

usage: python3 -I faa_freq.py FRQ.csv ATC_BASE.csv existing_freq_dir out_dir
"""
import csv, json, os, re, sys
from collections import defaultdict

frq_path, base_path, old_dir, out_dir = sys.argv[1:5]

NON_CONUS = {'AK', 'HI', 'PR', 'VI', 'GU', 'AS', 'MP', 'MH', 'FM', 'PW'}
base = {}
for r in csv.DictReader(open(base_path, encoding='latin-1')):
    base[r['FACILITY_ID']] = r

def icao_for(lid, state):
    b = base.get(lid)
    if b and b['ICAO_ID'].strip():
        return b['ICAO_ID'].strip()
    if len(lid) == 3 and lid.isalpha() and state not in NON_CONUS:
        return 'K' + lid
    return lid  # small fields like 00R, N92: users type the FAA code

def kind(use):
    u = use.upper().strip()
    if u in ('CD/P', 'CD/S', 'PTD', 'CD PRE TAXI CLNC'): return 'CLD', 1
    if u in ('GND/P', 'GND/S'): return 'GND', 1
    if u in ('LCL/P', 'LCL/S'): return 'TWR', 1
    if u in ('APCH/P DEP/P', 'APCH/P DEP/P IC', 'APCH/S DEP/S', 'APCH/S DEP/S IC'): return 'A/D', 1
    if u in ('APCH/P', 'APCH/P IC', 'APCH/S', 'APCH/S IC'): return 'APP', 1
    if u in ('DEP/P', 'DEP/S', 'DEP/P IC', 'DEP/S IC'): return 'DEP', 1
    if u in ('CLASS B', 'CLASS C', 'TRSA'): return 'A/D', 3   # same controllers, listed after the main entries
    if u in ('ATIS', 'D-ATIS'): return 'ATIS', 1
    if u == 'CTAF': return 'CTAF', 1
    if u == 'UNICOM': return 'UNIC', 1
    if u == 'RAMP CTL': return 'RAMP', 1
    if re.search(r'\b(AWOS|ASOS)', u): return 'AWOS', 2
    if re.search(r'\bDP$', u): return 'DP', 2
    if re.search(r'\bSTAR$', u): return 'STAR', 2
    return None, 0

# Compass words are approximate halves; the FAA gives no exact line for them.
OCT = {'N': 0, 'NE': 45, 'E': 90, 'SE': 135, 'S': 180, 'SW': 225, 'W': 270, 'NW': 315}
COMPASS = {'NORTHEAST': [1, 89], 'SOUTHEAST': [91, 179], 'SOUTHWEST': [181, 269], 'NORTHWEST': [271, 359], 'NORTH': [271, 89], 'EAST': [0, 180], 'SOUTH': [91, 269], 'WEST': [181, 360]}

def sector(s):
    s = s.upper()
    out = {}
    m = re.search(r'\b(\d{3})\s*-\s*(\d{3})\b', s)
    if m:
        out['b'] = [int(m.group(1)), int(m.group(2))]
    elif re.search(r'\b(NE|NW|SE|SW|N|E|S|W)\s*-\s*(NE|NW|SE|SW|N|E|S|W)\b', s):
        m = re.search(r'\b(NE|NW|SE|SW|N|E|S|W)\s*-\s*(NE|NW|SE|SW|N|E|S|W)\b', s)
        out['b'] = [OCT[m.group(1)], OCT[m.group(2)]]
    else:
        for w, b in COMPASS.items():
            if re.search(r'\b' + w + r'\b', s):
                out['b'] = b
                break
    if re.search(r'\bABV\b|\bABOVE\b', s): out['alt'] = 'high'
    elif re.search(r'BLW|BELOW', s) and not re.search(r'FT\s*-', s): out['alt'] = 'low'
    return out or None

data = defaultdict(list)
seen = defaultdict(set)
for r in csv.DictReader(open(frq_path, encoding='latin-1')):
    if r['SERVICED_SITE_TYPE'] not in ('AIRPORT', 'SEAPLANE BASE'):
        continue
    try:
        mhz = float(r['FREQ'].split('/')[0])
    except ValueError:
        continue
    if not (118 <= mhz < 137):
        continue
    t, pri = kind(r['FREQ_USE'])
    if not t:
        continue
    if re.search(r'/S\b|PRE TAXI', r['FREQ_USE'].upper()):
        pri += 1   # secondary and pre-taxi channels after the primary one
    lid = r['SERVICED_FACILITY'].strip()
    icao = icao_for(lid, r['SERVICED_STATE'])
    sect = r['SECTORIZATION'].strip()
    desc = (r['FREQ_USE'].strip() + ' ' + sect).strip()
    key = (t, desc, mhz)
    if key in seen[icao]:
        continue
    seen[icao].add(key)
    own = 0 if r['FACILITY'].strip() == lid else 1   # the airport's own tower first
    e = [t, desc, mhz]
    sc = sector(sect) if t in ('A/D', 'APP', 'DEP', 'DP', 'STAR') else None
    if sc: e.append(sc)
    data[icao].append(((pri, own), e))

def call(s):
    return s.strip()

out = {}
for icao, items in data.items():
    items.sort(key=lambda x: x[0])
    lid = icao[1:] if icao.startswith('K') and len(icao) == 4 else icao
    b = base.get(lid) or {}
    obj = {'f': [e for _, e in items]}
    for k, col in (('t', 'TWR_CALL'), ('a', 'PRIMARY_APCH_RADIO_CALL'), ('d', 'PRIMARY_DEP_RADIO_CALL'), ('h', 'TWR_HRS')):
        v = call(b.get(col, ''))
        if v and not v.endswith('ARTCC'):
            obj[k] = v
    out[icao] = obj

os.makedirs(out_dir, exist_ok=True)
buckets = defaultdict(dict)
for f in os.listdir(old_dir):
    if f.endswith('.json'):
        buckets[f[:-5]].update(json.load(open(os.path.join(old_dir, f))))
replaced = 0
for icao, obj in out.items():
    ch = icao[0]
    if icao in buckets[ch]: replaced += 1
    buckets[ch][icao] = obj
for ch, d in buckets.items():
    with open(os.path.join(out_dir, ch + '.json'), 'w') as fh:
        json.dump(d, fh, separators=(',', ':'), sort_keys=True)
print('FAA airports:', len(out), 'replaced OurAirports entries:', replaced)
