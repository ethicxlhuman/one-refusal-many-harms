#!/usr/bin/env python3
"""Plain-SVG figures from analysis/out/*.json (no plotting library on this machine). One colour per model throughout."""
import json, math, pathlib
A = pathlib.Path(__file__).resolve().parent; OUT = A / 'out'; FIG = A.parent / 'figures'
S = json.load(open(OUT / 'exam-summary.json')); F = json.load(open(OUT / 'facts.json'))
H = json.load(open(OUT / 'refusal-opening.json'))['counts']; T = json.load(open(OUT / 'tone.json'))
COL = {'Base': '#8c8c8c', 'ARA t27': '#d4691e', 'Abliteration t8': '#2b5d8f', 'Cyber-only ×2': '#3a8a3f'}
FONT = 'font-family="Georgia,serif" font-size="12" fill="#222"'

def wil(k, n, z=1.96):
    p = k / n; d = 1 + z*z/n; c = (p + z*z/(2*n)) / d; h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return 100*p, 100*max(0, c-h), 100*min(1, c+h)

def svg(W, Hh, body): return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {Hh}" {FONT}>' + ''.join(body) + '</svg>'
def txt(x, y, s, **k):
    a = ' '.join(f'{kk.replace("_","-")}="{v}"' for kk, v in k.items()); return f'<text x="{x:.1f}" y="{y:.1f}" {a}>{s}</text>'

def hbars(x0, y0, w, title, items, target=None, target_lab='', xmax=100):
    """items: (label, value, lo, hi, colour, hatch, annot)"""
    b = [txt(x0, y0, title, font_weight='bold', font_size=13)]; rowh = 34; top = y0 + 14; lw = 118; pw = w - lw - 10
    X = lambda v: x0 + lw + pw * v / xmax
    for i, (lab, v, lo, hi, c, hatch, ann) in enumerate(items):
        y = top + i * rowh
        b.append(txt(x0 + lw - 8, y + 19, lab, text_anchor='end'))
        b.append(f'<rect x="{X(0):.1f}" y="{y+6}" width="{X(v)-X(0):.1f}" height="20" fill="{c}" fill-opacity="{0.45 if hatch else 0.9}" stroke="{c}" stroke-dasharray="{"4 2" if hatch else "0"}"/>')
        if lo is not None: b.append(f'<line x1="{X(lo):.1f}" x2="{X(hi):.1f}" y1="{y+16}" y2="{y+16}" stroke="#000" stroke-width="1.2"/>')
        b.append(txt(X(max(v, hi or 0)) + 5, y + 20, ann, font_size=11))
    bot = top + len(items) * rowh + 4
    b.append(f'<line x1="{X(0):.1f}" x2="{X(xmax):.1f}" y1="{bot}" y2="{bot}" stroke="#999"/>')
    for v in range(0, xmax + 1, 25): b.append(txt(X(v), bot + 14, f'{v}%', text_anchor='middle', font_size=10))
    if target is not None:
        b.append(f'<line x1="{X(target):.1f}" x2="{X(target):.1f}" y1="{top}" y2="{bot}" stroke="#b00" stroke-dasharray="5 3"/>')
        b.append(txt(X(target), top - 2, target_lab, text_anchor='middle', font_size=10, fill='#b00'))
    return b

# Fig 1 teaser
kb = S['base']['keep_kept'][0]
ca = [(m, *wil(*S[t]['cyber_complied'])) for m, t in [('Base', 'base'), ('ARA t27', 'ara-t27'), ('Abliteration t8', 'abl-t8')]]
cyc = H['r1b3-ortho-x2.0']['cyber_harmful']; cyb = H['base']['cyber_harmful']
items1 = [(m, v, lo, hi, COL[m], False, f'{v:.0f}%') for m, v, lo, hi in ca]
items1.append(('Cyber-only ×2', 100 * (cyc[1] - cyc[0]) / cyc[1], None, None, COL['Cyber-only ×2'], True, f'{100*(cyc[1]-cyc[0])/cyc[1]:.0f}%*'))
items2 = [('Base', 100.0, None, None, COL['Base'], False, '100%')]
for m, t in [('ARA t27', 'ara-t27'), ('Abliteration t8', 'abl-t8')]:
    items2.append((m, 100 * S[t]['keep_kept'][0] / kb, None, None, COL[m], False, f"{100*S[t]['keep_kept'][0]/kb:.0f}%"))
kc, kbh = H['r1b3-ortho-x2.0']['keep_refusing'][0], H['base']['keep_refusing'][0]
items2.append(('Cyber-only ×2', 100 * kc / kbh, None, None, COL['Cyber-only ×2'], True, f'{100*kc/kbh:.0f}%*'))
bio = [('Base', 'base'), ('ARA t27', 'ara-t27'), ('Abliteration t8', 'abl-t8')]
items3 = [(m, 100 * S[t]['keep_kept:bio_chem'][0] / 14, *wil(S[t]['keep_kept:bio_chem'][0], 14)[1:], COL[m], False, f"{S[t]['keep_kept:bio_chem'][0]}/14") for m, t in bio]
items3.append(('Cyber-only ×2', 100 * H['r1b3-ortho-x2.0']['keep_refusing:bio_chem'][0] / 14, None, None, COL['Cyber-only ×2'], True, f"{H['r1b3-ortho-x2.0']['keep_refusing:bio_chem'][0]}/14*"))
b = hbars(10, 18, 330, 'Cyber prompts answered (goal: high)', items1, 80, 'goal 80%')
b += hbars(350, 18, 330, 'Other refusals kept, vs base (goal: high)', items2, 90, 'goal 90%')
b += hbars(690, 18, 330, 'Bio/chem refusals kept (goal: 14/14)', items3)
b.append(txt(10, 214, '* Cyber-only edit scored by refusal openings, not the LLM judge. Whiskers: 95% Wilson intervals. 93 cyber, 94 other-harm, 14 bio/chem held-out prompts.', font_size=10.5, fill='#555'))
(FIG / 'fig1-teaser.svg').write_text(svg(1030, 222, b))

# Fig 2 pipeline
def box(x, y, w, h, title, sub, c='#2b5d8f'):
    r = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#fff" stroke="{c}" stroke-width="1.6"/>', txt(x + w/2, y + 20, title, text_anchor='middle', font_weight='bold')]
    for i, s in enumerate(sub): r.append(txt(x + w/2, y + 38 + 15*i, s, text_anchor='middle', font_size=11, fill='#444'))
    return r
def arrow(x1, y1, x2, y2): return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#555" stroke-width="1.6" marker-end="url(#a)"/>'
b = ['<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#555"/></marker></defs>']
b += [txt(10, 16, 'Round 1', font_weight='bold', fill='#555'), txt(10, 146, 'Round 1b', font_weight='bold', fill='#555')]
b += box(10, 24, 180, 92, '1. Prompt pairs', ['122 cyber harmful/harmless', 'twins, same topic words', '+ 93 other-harm prompts'])
b += box(215, 24, 180, 92, '2. Measure directions', ['cyber vs general refusal', 'direction per layer', '(cosine, before editing)'])
b += box(420, 24, 190, 92, '3. Heretic search', ['60 trials × 2 methods', 'min cyber refusals, keep', 'others, min drift (KL)'])
b += box(635, 24, 180, 92, '4. Held-out exam', ['297 prompts, 5 sets', 'LLM judge + capability', 'tests + hand-read'], '#3a8a3f')
b += [arrow(190, 70, 213, 70), arrow(395, 70, 418, 70), arrow(610, 70, 633, 70)]
b += box(215, 154, 180, 92, '5. Remove the shared part', ['project the general', 'refusal direction out of', 'the cyber direction'], '#d4691e')
b += box(420, 154, 190, 92, '6. Same edit as Heretic', ['trial-8 recipe, cyber-only', 'direction, strength ×1–×3'], '#d4691e')
b += box(635, 154, 180, 92, '7. Exam the best one', ['strength ×2, same 297', 'prompts (refusal openings)'], '#3a8a3f')
b += [arrow(305, 116, 305, 152), arrow(395, 200, 418, 200), arrow(610, 200, 633, 200)]
(FIG / 'fig2-pipeline.svg').write_text(svg(825, 256, b))

# Fig 3 concept
b = ['<defs><marker id="b" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs>']
ox, oy = 70, 210
def vec(x2, y2, c, lab, lx, ly, dash=''): return [f'<line x1="{ox}" y1="{oy}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="3" stroke-dasharray="{dash}" marker-end="url(#b)"/>', txt(lx, ly, lab, fill=c, font_weight='bold')]
b += vec(330, 210, '#8c8c8c', 'general refusal direction (shared by all harms)', 150, 232)
b += vec(300, 60, '#2b5d8f', 'cyber refusal direction', 310, 58)
b += [f'<line x1="300" y1="210" x2="300" y2="68" stroke="#3a8a3f" stroke-width="2" stroke-dasharray="5 4"/>']
b += vec(70, 70, '#3a8a3f', 'cyber-only part (round 1b)', 80, 64, '6 3')
b += [txt(108, 200, 'cos ≈ 0.67–0.86', font_size=11, fill='#2b5d8f'), txt(318, 150, '= shared part', font_size=11, fill='#8c8c8c'), txt(318, 166, '+ cyber-only part', font_size=11, fill='#3a8a3f')]
b += [txt(470, 70, 'ARA: removes much of the shared part', font_size=12), txt(470, 86, '→ cyber unlocked, bio/chem leaks', font_size=12, fill='#d4691e'),
      txt(470, 118, 'Abliteration: removes a little of it', font_size=12), txt(470, 134, '→ little leakage, half of cyber unlocked', font_size=12, fill='#2b5d8f'),
      txt(470, 166, 'Cyber-only part removed (×1–×3)', font_size=12), txt(470, 182, '→ almost nothing changes', font_size=12, fill='#3a8a3f')]
(FIG / 'fig3-concept.svg').write_text(svg(780, 250, b))

# Fig 6 per-category
cats = [('bio_chem', 'bio/chem', 14), ('child_safety', 'child safety', 10), ('privacy', 'privacy', 15), ('privacy_osint_people', 'people-OSINT', 10), ('self_harm', 'self-harm', 20), ('violence', 'violence', 25)]
W, Hh, l, t, pw, ph = 760, 266, 50, 50, 690, 170; gw = pw / len(cats); bw = gw / 4.2
b = [txt(l, 16, 'Refusals kept, by harm category (LLM judge, held-out)', font_weight='bold', font_size=13)]
Y = lambda v: t + ph * (1 - v / 100)
for v in range(0, 101, 25): b += [f'<line x1="{l}" x2="{l+pw}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="#e5e5e5"/>', txt(l - 6, Y(v) + 4, f'{v}%', text_anchor='end', font_size=10)]
for i, (k, lab, n) in enumerate(cats):
    for j, (m, tg) in enumerate([('Base', 'base'), ('ARA t27', 'ara-t27'), ('Abliteration t8', 'abl-t8')]):
        kk = S[tg][f'keep_kept:{k}'][0]; p, lo, hi = wil(kk, n); x = l + i * gw + 0.35 * bw + j * (bw + 3)
        b += [f'<rect x="{x:.1f}" y="{Y(p):.1f}" width="{bw:.1f}" height="{Y(0)-Y(p):.1f}" fill="{COL[m]}"/>', f'<line x1="{x+bw/2:.1f}" x2="{x+bw/2:.1f}" y1="{Y(lo):.1f}" y2="{Y(hi):.1f}" stroke="#000"/>',
              txt(x + bw/2, Y(p) - 3 if p < 92 else Y(p) + 12, f'{kk}', text_anchor='middle', font_size=9.5, fill='#000' if p < 92 else '#fff')]
    b.append(txt(l + i * gw + gw/2 - 4, t + ph + 16, f'{lab} (n={n})', text_anchor='middle', font_size=11))
for j, m in enumerate(['Base', 'ARA t27', 'Abliteration t8']): b += [f'<rect x="{l+j*130}" y="26" width="12" height="12" fill="{COL[m]}"/>', txt(l + 16 + j*130, 36, m, font_size=11)]
(FIG / 'fig6-categories.svg').write_text(svg(W, Hh, b))

# Fig 7 round 1b strength
g = F['round1b']['mpoa_grid']; base = F['round1b']['mpoa_base_val']
W, Hh = 760, 260; b = []
def panel(x0, title, ylab, ymin, ymax, ser, hl):
    pw, ph, t = 280, 170, 40; X = lambda v: x0 + 40 + pw * (v - 0.5) / 3; Y = lambda v: t + ph * (1 - (v - ymin) / (ymax - ymin))
    r = [txt(x0, 18, title, font_weight='bold', font_size=13), f'<rect x="{x0+40}" y="{t}" width="{pw}" height="{ph}" fill="none" stroke="#999"/>']
    for k in range(5): v = ymin + (ymax - ymin) * k / 4; r += [txt(x0 + 34, Y(v) + 4, f'{v:g}', text_anchor='end', font_size=10)]
    for v in (1, 1.5, 2, 3): r.append(txt(X(v), t + ph + 15, f'×{v:g}', text_anchor='middle', font_size=10))
    r.append(txt(x0 + 40 + pw/2, t + ph + 32, 'edit strength', text_anchor='middle', font_size=11))
    r.append(f'<text transform="translate({x0+8} {t+ph/2}) rotate(-90)" text-anchor="middle" font-size="11">{ylab}</text>')
    for lab, v, c in hl: r += [f'<line x1="{x0+40}" x2="{x0+40+pw}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="{c}" stroke-dasharray="5 3"/>', txt(x0 + 44 + pw, Y(v) + 4, lab, font_size=10, fill=c)]
    for xs, ys, c, mk in ser:
        r.append(f'<polyline points="{" ".join(f"{X(a):.1f},{Y(bb):.1f}" for a, bb in zip(xs, ys))}" fill="none" stroke="{c}" stroke-width="2"/>')
        r += [f'<circle cx="{X(a):.1f}" cy="{Y(bb):.1f}" r="{mk}" fill="{c}"/>' for a, bb in zip(xs, ys)]
    return r
xs = [1, 1.5, 2, 3]; o = [g[f'ortho-x{v:.1f}'] for v in xs]
b += panel(10, 'Cyber refusals (of 60, validation)', 'refused', 30, 60, [(xs, [x['cyber_refusals'] for x in o], COL['Cyber-only ×2'], 4), ([1], [g['plain-x1.0']['cyber_refusals']], COL['Abliteration t8'], 6)],
           [('base 56', base['cyber_refusals'], '#555')])
b += panel(400, 'Drift from base (KL, 8 tokens)', 'KL', 0, 0.5, [(xs, [x['kl_8tok'] for x in o], COL['Cyber-only ×2'], 4), ([1], [g['plain-x1.0']['kl_8tok']], COL['Abliteration t8'], 6)], [])
b += [f'<circle cx="60" cy="248" r="5" fill="{COL["Cyber-only ×2"]}"/>', txt(70, 252, 'cyber-only direction', font_size=11), f'<circle cx="230" cy="248" r="6" fill="{COL["Abliteration t8"]}"/>', txt(240, 252, 'full cyber direction (Heretic trial-8 recipe, ×1)', font_size=11)]
(FIG / 'fig7-round1b.svg').write_text(svg(W, Hh + 8, b))

# Fig 8 side effects
C = F['capability_paired']; W = 760; b = [txt(10, 16, 'Benchmark questions lost / gained vs base', font_weight='bold', font_size=13)]
rows = [(task, m, C[f'{tg}:{task}']) for task in ('mmlu_pro', 'gsm8k', 'ifeval') for m, tg in (('ARA t27', 'ara-t27'), ('Abliteration t8', 'abl-t8'))]
cx = 300; sc = 14
for i, (task, m, c) in enumerate(rows):
    y = 34 + i * 24; name = {'mmlu_pro': 'MMLU-Pro', 'gsm8k': 'GSM8K', 'ifeval': 'IFEval'}[task]
    b += [txt(140, y + 13, f'{name} · {m.split()[0]}', text_anchor='end', font_size=11),
          f'<rect x="{cx - c["lost"]*sc}" y="{y}" width="{c["lost"]*sc}" height="16" fill="{COL[m]}"/>', f'<rect x="{cx}" y="{y}" width="{c["gained"]*sc}" height="16" fill="{COL[m]}" fill-opacity="0.35"/>',
          txt(cx - c['lost']*sc - 4, y + 13, f'−{c["lost"]}', text_anchor='end', font_size=10), txt(cx + c['gained']*sc + 4, y + 13, f'+{c["gained"]}  p={c["mcnemar_p"]:.2f}', font_size=10)]
b += [f'<line x1="{cx}" x2="{cx}" y1="30" y2="{34+len(rows)*24}" stroke="#333"/>', txt(cx - 60, 34 + len(rows)*24 + 14, 'lost', text_anchor='middle', font_size=10), txt(cx + 40, 34 + len(rows)*24 + 14, 'gained', text_anchor='middle', font_size=10)]
x0 = 480; b.append(txt(x0, 16, 'Cyber answers opening with a disclaimer', font_weight='bold', font_size=13))
for i, (m, tg) in enumerate([('Base', 'base'), ('ARA t27', 'ara-t27'), ('Abliteration t8', 'abl-t8'), ('Cyber-only ×2', 'r1b3-ortho-x2.0')]):
    k, n = T[tg]['disclaimer_open_cyber']; y = 34 + i * 30; w = 180 * k / n
    b += [txt(x0 + 100, y + 14, m, text_anchor='end', font_size=11), f'<rect x="{x0+106}" y="{y}" width="{max(w,1):.1f}" height="18" fill="{COL[m]}"/>', txt(x0 + 112 + w, y + 14, f'{k}/{n}', font_size=11)]
b.append(txt(x0, 166, 'Median length of short knowledge answers (tokens):', font_size=11))
for i, (m, tg) in enumerate([('Base', 'base'), ('ARA t27', 'ara-t27'), ('Abliteration t8', 'abl-t8'), ('Cyber-only ×2', 'r1b3-ortho-x2.0')]):
    b.append(txt(x0 + 10 + i * 70, 184, f'{T[tg]["median_tokens_knowledge"]:g}', font_weight='bold', fill=COL[m]))
(FIG / 'fig8-side-effects.svg').write_text(svg(W, 200, b))
print(sorted(p.name for p in FIG.glob('*.svg')))
