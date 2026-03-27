#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / 'data'
LAST = DATA / 'last_success.json'
CURRENT_THEATERS = ['fox', 'paradise', 'revue', 'tiff', 'kingsway']

# Theater-specific sanity rules. Revue now uses a stable direct-source parser and
# should be judged against that stable smaller baseline rather than the old 135+ UI path.
MIN_FLOORS = {
    'revue': 20,
}
DROP_RATIO_RULES = {
    'default': 0.35,
    'revue': 0.10,  # tolerate the architecture shift away from the old expanded Selenium count
}

current = {}
for theater in CURRENT_THEATERS:
    p = DATA / f'{theater}_films.json'
    try:
        current[theater] = len(json.loads(p.read_text(encoding='utf-8')))
    except Exception as e:
        print(f'ERROR missing_or_bad {theater}: {e}')
        sys.exit(2)

if not LAST.exists():
    print('OK no_baseline ' + json.dumps(current, ensure_ascii=False))
    sys.exit(0)

prev = json.loads(LAST.read_text(encoding='utf-8')).get('counts', {})
problems = []
for theater, count in current.items():
    old = prev.get(theater)

    floor = MIN_FLOORS.get(theater)
    if floor is not None and count < floor:
        problems.append(f'{theater}: below stable floor {floor} -> {count}')
        continue

    if old in (None, 0):
        continue
    if count <= 0:
        problems.append(f'{theater}: zero items')
        continue

    ratio = count / old
    threshold = DROP_RATIO_RULES.get(theater, DROP_RATIO_RULES['default'])
    if ratio < threshold:
        problems.append(f'{theater}: suspicious drop {old} -> {count}')

if problems:
    print('SUSPECT ' + ' | '.join(problems))
    sys.exit(1)

print('OK ' + json.dumps(current, ensure_ascii=False))
