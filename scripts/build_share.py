#!/usr/bin/env python3
"""Build paper/share/: per-reply labels without reply text, aggregate JSON, figures, scripts, hashes.
Reply text, harmful prompt text and adapters stay in .private/. Each row carries sha256(final) so a holder
of the private files can verify the label set."""
import os
import json, hashlib, pathlib, shutil, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
ROOT = pathlib.Path(os.environ.get('LAB_ROOT', '.')); PRIV = ROOT / '.private/llm-obliteration/outputs'
PAPER = ROOT / 'projects/llm-obliteration/paper'; S = PAPER / 'share'
(S / 'labels').mkdir(parents=True, exist_ok=True); (S / 'results').mkdir(exist_ok=True); (S / 'figures').mkdir(exist_ok=True); (S / 'scripts').mkdir(exist_ok=True)
import importlib.util
spec = importlib.util.spec_from_file_location('ro', PAPER / 'analysis/refusal_opening.py')
src = (PAPER / 'analysis/refusal_opening.py').read_text().split("out = {'definition'")[0]
ns = {'__file__': str(PAPER / 'analysis/refusal_opening.py')}; exec(src, ns); is_ref = ns['is_ref']
for d in sorted(PRIV.iterdir()):
    f = d / ('judged.jsonl' if (d / 'judged.jsonl').exists() else 'generations.jsonl')
    with open(S / 'labels' / f'{d.name}.jsonl', 'w') as o:
        for l in open(f):
            r = json.loads(l)
            if r['set'].startswith('teacher'): continue
            o.write(json.dumps({'tag': d.name, 'set': r['set'], 'id': r['id'], 'category': r.get('category', r.get('group')),
                'decode': r['decode'], 'finish_reason': r['finish_reason'], 'n_tokens': r['n_tokens'], 'loop_heuristic': r['loop_heuristic'],
                'judge_label_final': r.get('judge_label_final'), 'refusal_opening': is_ref(r['final']),
                'final_sha256': hashlib.sha256(r['final'].encode()).hexdigest(), 'source_file_sha256': hashlib.sha256(f.read_bytes()).hexdigest()}) + '\n')
for x in ['exam-summary.json', 'facts.json', 'refusal-opening.json', 'tone.json']: shutil.copy(PAPER / 'analysis/out' / x, S / 'results' / x)
for x in (PAPER / 'figures').glob('*.svg'): shutil.copy(x, S / 'figures' / x.name)
for x in ['summarize_paper.py', 'refusal_opening.py', 'tone.py', 'facts.py', 'build_share.py']: shutil.copy(PAPER / 'analysis' / x, S / 'scripts' / x)
shutil.copy(PAPER / 'paper.pdf', S / 'paper.pdf')
# guard: no reply text leaked
bad = [p for p in S.rglob('*.jsonl') if any(k in p.read_text() for k in ('"final"', '"raw"', '"prompt"'))]
assert not bad, bad
sums = '\n'.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(S)}' for p in sorted(S.rglob('*')) if p.is_file() and p.name != 'SHA256SUMS')
(S / 'SHA256SUMS').write_text(sums + '\n'); print(sums.count('\n') + 1, 'files')
