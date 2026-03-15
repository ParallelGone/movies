#!/usr/bin/env python3
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / 'data'
OUT = DATA / 'last_success.json'

counts = {}
for theater in ['fox', 'paradise', 'revue', 'tiff', 'kingsway']:
    p = DATA / f'{theater}_films.json'
    try:
        counts[theater] = len(json.loads(p.read_text(encoding='utf-8')))
    except Exception:
        counts[theater] = None

payload = {
    'generatedAt': datetime.now().astimezone().isoformat(),
    'counts': counts,
}
OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(payload, ensure_ascii=False))
