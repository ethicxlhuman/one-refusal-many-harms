#!/usr/bin/env python3
"""Derive every paper number not produced by summarize_paper.py / refusal_opening.py.
Reads project runs/ and .private/ copies (read-only). Writes paper/analysis/out/facts.json and paper/figures/*.svg.
Paired capability tests: exact two-sided McNemar on per-item correctness (same items, same order)."""
import os
import json, glob, math, re, pathlib
ROOT = pathlib.Path(os.environ.get('LAB_ROOT', '.')); P = ROOT / 'projects/llm-obliteration'
V = ROOT / '.private/llm-obliteration/volume-copy'; RUNS = P / 'runs'
OUT = P / 'paper/analysis/out'; FIG = P / 'paper/figures'; FIG.mkdir(parents=True, exist_ok=True)
F = {}

def binom_two_sided(b, c):
    n = b + c
    if n == 0: return 1.0
    k = min(b, c); p = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * p)

# ---- capability: paired per item
def items(tag, task_glob, key):
    out = {}
    for f in sorted(glob.glob(str(V / tag / 'lm_eval' / '*' / '*' / f'samples_{task_glob}_*.jsonl'))):
        sub = re.search(r'samples_(.+?)_2026', f).group(1)
        for l in open(f):
            d = json.loads(l)
            if task_glob == 'truthfulqa_mc2' or ('filter' in d and task_glob == 'gsm8k' and d['filter'] != 'strict-match'): continue
            out[(sub, d['doc_id'])] = float(d[key])
    return out
cap = {}
for task, glob_, key in [('mmlu_pro', 'mmlu_pro_*', 'exact_match'), ('gsm8k', 'gsm8k', 'exact_match'), ('ifeval', 'ifeval', 'prompt_level_strict_acc')]:
    b = items('base', glob_, key)
    for tag in ('ara-t27', 'abl-t8'):
        e = items(tag, glob_, key); ks = sorted(set(b) & set(e))
        lost = sum(b[k] == 1 and e[k] == 0 for k in ks); gained = sum(b[k] == 0 and e[k] == 1 for k in ks)
        cap[f'{tag}:{task}'] = {'n': len(ks), 'base_acc': round(100 * sum(b[k] for k in ks) / len(ks), 1),
            'edit_acc': round(100 * sum(e[k] for k in ks) / len(ks), 1), 'lost': lost, 'gained': gained,
            'mcnemar_p': round(binom_two_sided(lost, gained), 4)}
for tag in ('base', 'ara-t27', 'abl-t8'):
    f = glob.glob(str(V / tag / 'lm_eval' / '*' / '*' / 'results_*.json'))
    for x in f:
        r = json.load(open(x))['results']
        if 'truthfulqa_mc2' in r: cap[f'{tag}:truthfulqa_mc2'] = round(100 * r['truthfulqa_mc2']['acc,none'], 1)
F['capability_paired'] = cap

# ---- Heretic studies
def study(run):
    d = json.load(open(RUNS / run / 'study.json')); T = []
    for t in d['trials']:
        s = [int(x['score']['md_display'].split('/')[0]) for x in t['scores'][:2]]
        T.append({'trial': t['index'], 'cyber': s[0], 'keep': s[1], 'kl': t['values'][2], 'params': t['params']})
    base = [int(x['baseline']['md_display'].split('/')[0]) for x in d['trials'][0]['scores'][:2]]
    return T, base
ara, ara_base = study('20261117T061533Z-heretic_run-ara-matched')
abl, abl_base = study('20261117T071717Z-heretic_run-abl-matched')
pick = lambda T, i: next(t for t in T if t['trial'] == i)
F['heretic'] = {
 'ara_base': ara_base, 'abl_base': abl_base, 'n_trials': [len(ara), len(abl)],
 'ara_t27': pick(ara, 27), 'ara_t7': pick(ara, 7), 'ara_t11': pick(ara, 11), 'ara_t9': pick(ara, 9),
 'ara_kl_le_0.5': [t for t in ara if t['kl'] <= 0.5],
 'abl_t8': pick(abl, 8), 'abl_kl_range': [min(t['kl'] for t in abl), max(t['kl'] for t in abl)],
 'abl_min_cyber': min(abl, key=lambda t: (t['cyber'], -t['keep'])),
 'ara_trials_layer0': sum(t['params'].get('start_layer_index') == 0 for t in ara),
}
# leakage vs strength in abliteration: correlation of cyber drop and keep drop
xs = [abl_base[0] - t['cyber'] for t in abl]; ys = [abl_base[1] - t['keep'] for t in abl]
mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
F['heretic']['abl_pearson_cyberdrop_keepdrop'] = round(sum((a - mx) * (b - my) for a, b in zip(xs, ys)) / math.sqrt(sum((a - mx) ** 2 for a in xs) * sum((b - my) ** 2 for b in ys)), 3)

# ---- direction statistics
dc = json.load(open(RUNS / '20261117T055808Z-direction_checks-base/RUN.json'))['summary']
cos = dc['cos_cyberMatched_vs_keepGeneric']; cg = dc['cos_cyberGeneric_vs_keepGeneric']
dm, dg = dc['dprime_cyber_vs_matched'], dc['dprime_cyber_vs_generic']
F['directions'] = {'n_layers': len(cos),
 'cos_matched_keep_L21_59': [round(min(cos[21:]), 3), round(max(cos[21:]), 3)],
 'cos_matched_keep_L0_17': [round(min(cos[:18]), 3), round(max(cos[:18]), 3)],
 'cos_generic_keep_L21_59': [round(min(cg[21:]), 3), round(max(cg[21:]), 3)],
 'dprime_matched_max': [round(max(dm), 2), dm.index(max(dm))], 'dprime_generic_max': [round(max(dg), 2), dg.index(max(dg))],
 'dprime_matched_L25plus_range': [round(min(dm[25:59]), 2), round(max(dm[25:59]), 2)]}
og = json.load(open(RUNS / '20261117T101510Z-ortho_gated/RUN.json'))['summary']
mp = json.load(open(RUNS / '20261117T102140Z-mpoa_ortho/RUN.json'))['summary']
F['round1b'] = {
 'dprime_ortho_L45': round(og['stats']['dprime_bad_good_ortho'][45], 2), 'dprime_plain_L45': round(og['stats']['dprime_bad_good_plain'][45], 2),
 'dprime_ortho_max': round(max(og['stats']['dprime_bad_good_ortho']), 2),
 'mpoa_cos_plain_ortho_L21_59': [round(min(mp['stats']['cos_plain_ortho'][21:]), 3), round(max(mp['stats']['cos_plain_ortho'][21:]), 3)],
 'mpoa_max_abs_cos_ortho_keep': max(abs(x) for x in mp['stats']['cos_ortho_vs_keepdir']),
 'mpoa_base_val': mp['base_val'], 'mpoa_grid': mp['grid'], 'mpoa_pick': mp['pick'],
 'heretic_t8_merge_kl8': json.load(open(V / 'abl-matched/merge_check.t8.json'))['kl_mean_8tok'],
}
# ---- costs
L = [json.loads(l) for l in open(RUNS / 'COST-LEDGER.jsonl')]
r1b = [x for x in L if x['run_id'] >= '20261117T09']
F['cost'] = {'ledger_total': round(sum(x['cost_est_usd'] for x in L), 2), 'ledger_round1': round(sum(x['cost_est_usd'] for x in L if x not in r1b), 2),
 'ledger_round1b': round(sum(x['cost_est_usd'] for x in r1b), 2),

 'gpu_hours_ledger': round(sum(x['wall_s'] for x in L if x['stage'] != 'download') / 3600, 2), 'n_stages': len(L)}
(OUT / 'facts.json').write_text(json.dumps(F, indent=1, default=str))

# ---- figures (hand-written SVG; no plotting library available)
def svg_lines(series, fname, ylab, ymin, ymax, title, hline=None):
    W, H, l, r, t, b = 660, 300, 56, 175, 30, 40; pw, ph = W - l - r, H - t - b
    X = lambda i: l + pw * i / 59; Y = lambda v: t + ph * (1 - (v - ymin) / (ymax - ymin))
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Georgia,serif" font-size="11">',
         f'<text x="{l}" y="18" font-size="12" font-weight="bold">{title}</text>',
         f'<rect x="{l}" y="{t}" width="{pw}" height="{ph}" fill="none" stroke="#999"/>']
    for k in range(6):
        v = ymin + (ymax - ymin) * k / 5; s.append(f'<line x1="{l-4}" x2="{l}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="#999"/><text x="{l-7}" y="{Y(v)+4:.1f}" text-anchor="end">{v:g}</text>')
    for i in range(0, 60, 10): s.append(f'<text x="{X(i):.1f}" y="{t+ph+14}" text-anchor="middle">{i}</text>')
    s.append(f'<text x="{l+pw/2}" y="{H-6}" text-anchor="middle">layer</text><text transform="translate(14 {t+ph/2}) rotate(-90)" text-anchor="middle">{ylab}</text>')
    if hline is not None: s.append(f'<line x1="{l}" x2="{l+pw}" y1="{Y(hline):.1f}" y2="{Y(hline):.1f}" stroke="#bbb" stroke-dasharray="3 3"/>')
    for j, (name, ys, col, dash) in enumerate(series):
        pts = ' '.join(f'{X(i):.1f},{Y(max(ymin, min(ymax, v))):.1f}' for i, v in enumerate(ys))
        s.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="1.8" stroke-dasharray="{dash}"/>')
        s.append(f'<line x1="{l+pw+10}" x2="{l+pw+30}" y1="{t+14+18*j}" y2="{t+14+18*j}" stroke="{col}" stroke-width="2" stroke-dasharray="{dash}"/><text x="{l+pw+34}" y="{t+18+18*j}">{name}</text>')
    s.append('</svg>'); (FIG / fname).write_text('\n'.join(s))
svg_lines([('matched cyber vs keep', cos, '#1f4e79', ''), ('generic cyber vs keep', cg, '#c55a11', '5 3')],
          'fig4-overlap.svg', 'cosine', -0.5, 1.0, 'Cyber refusal direction vs general (keep-refusing) direction', hline=0)
pass  # d-prime figure retired in v0.2
if False: svg_lines([('plain (matched)', og['stats']['dprime_bad_good_plain'], '#1f4e79', ''), ('ortho (keep removed)', og['stats']['dprime_bad_good_ortho'], '#2e7d32', '5 3'), ('generic good side', dg, '#c55a11', '2 2')],
          'fig2-dprime.svg', "d′ (harmful vs harmless)", 0, 15, "Separation of cyber-harmful from harmless prompts along each direction")

def svg_scatter(fname):
    W, H, l, r, t, b = 640, 310, 56, 20, 30, 46; pw, ph = (W - l - r) / 2 - 20, H - t - b
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Georgia,serif" font-size="11">']
    for p, (name, T, base, mark) in enumerate([('ARA (60 trials)', ara, ara_base, 27), ('Abliteration (60 trials)', abl, abl_base, 8)]):
        x0 = l + p * (pw + 50); X = lambda v: x0 + pw * v / 60; Y = lambda v: t + ph * (1 - v / 60)
        s.append(f'<text x="{x0}" y="18" font-size="12" font-weight="bold">{name}</text><rect x="{x0}" y="{t}" width="{pw}" height="{ph}" fill="none" stroke="#999"/>')
        for v in range(0, 61, 20):
            s.append(f'<text x="{X(v):.1f}" y="{t+ph+14}" text-anchor="middle">{v}</text><text x="{x0-6}" y="{Y(v)+4:.1f}" text-anchor="end">{v}</text>')
        s.append(f'<text x="{x0+pw/2}" y="{H-6}" text-anchor="middle">cyber refusals /60 (lower = unlocked)</text>')
        s.append(f'<text transform="translate({x0-34} {t+ph/2}) rotate(-90)" text-anchor="middle">keep refusals /60</text>')
        s.append(f'<line x1="{X(0)}" y1="{Y(base[1])}" x2="{X(60)}" y2="{Y(base[1])}" stroke="#bbb" stroke-dasharray="3 3"/>')
        for tr in T:
            col = '#2e7d32' if tr['kl'] <= 0.5 else ('#c55a11' if tr['kl'] <= 3 else '#999999')
            rad = 5 if tr['trial'] == mark else 3
            s.append(f'<circle cx="{X(tr["cyber"]):.1f}" cy="{Y(tr["keep"]):.1f}" r="{rad}" fill="{col}" fill-opacity="0.75" stroke="{"#000" if tr["trial"]==mark else "none"}"/>')
        s.append(f'<circle cx="{X(base[0]):.1f}" cy="{Y(base[1]):.1f}" r="5" fill="none" stroke="#000"/><text x="{X(base[0]):.1f}" y="{Y(base[1])+18:.1f}" text-anchor="middle">base</text>')
        mt = pick(T, mark); s.append(f'<text x="{X(mt["cyber"])-8:.1f}" y="{Y(mt["keep"])-8:.1f}" text-anchor="end" font-weight="bold">t{mark}</text>')
    s.append('</svg>'); (FIG / fname).write_text('\n'.join(s))
svg_scatter('fig5-trials.svg')
print(json.dumps({k: F[k] for k in ('directions', 'cost')}, indent=1)); print(json.dumps(cap, indent=1))
print({k: v for k, v in F['heretic'].items() if k != 'ara_kl_le_0.5'}); print('ara KL<=0.5:', [(t['trial'], t['cyber'], t['keep'], round(t['kl'], 3)) for t in F['heretic']['ara_kl_le_0.5']])
print({k: F['round1b'][k] for k in F['round1b'] if 'grid' not in k})
