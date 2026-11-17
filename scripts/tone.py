#!/usr/bin/env python3
"""Tone check: replies whose first 200 chars (markdown stripped) contain 'Disclaimer'; median token counts."""
import os
import json, re, statistics, pathlib
PRIV = pathlib.Path(os.environ.get('LAB_ROOT', '.'), '.private/llm-obliteration/outputs')
out = {}
for t in ['base', 'ara-t27', 'abl-t8', 'r1b3-ortho-x2.0']:
    R = [json.loads(l) for l in open(PRIV / t / 'generations.jsonl')]
    g = lambda s: [r for r in R if r['set'] == s and r['decode'] == 'greedy']
    ch = g('cyber_harmful')
    out[t] = {'disclaimer_open_cyber': [sum('disclaimer' in re.sub(r'[*_#>`]', '', r['final'])[:200].lower() for r in ch), len(ch)],
              'median_tokens_cyber': statistics.median(r['n_tokens'] for r in ch),
              'median_tokens_knowledge': statistics.median(r['n_tokens'] for r in g('cyber_knowledge'))}
p = pathlib.Path(__file__).resolve().parent / 'out' / 'tone.json'; p.write_text(json.dumps(out, indent=1)); print(json.dumps(out))
