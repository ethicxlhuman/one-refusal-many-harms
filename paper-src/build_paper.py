#!/usr/bin/env python3
"""Build paper.html from draft/*.md + analysis/out/*.json + figures/*.svg, then render paper.pdf with headless Chromium.

Tables are generated from the recomputed JSON, never typed by hand. Typography follows the compassionate-agent-encounters
template contract (Old Standard TT body 11pt, headings 14pt #434343 / 13pt #666666, Letter, 1in margins), with Noto Serif fallback.
usage: build_paper.py [--no-pdf]
"""
import html, json, math, pathlib, re, subprocess, sys
D = pathlib.Path(__file__).resolve().parent; PAPER = D.parent; OUT = PAPER / 'analysis/out'; FIG = PAPER / 'figures'
META = json.loads((D / 'metadata.json').read_text())
S = json.loads((OUT / 'exam-summary.json').read_text()); F = json.loads((OUT / 'facts.json').read_text())
H = json.loads((OUT / 'refusal-opening.json').read_text()); T = json.loads((OUT / 'tone.json').read_text())


def wil(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return f'{k}/{n} ({100*p:.0f}% [{100*max(0,c-h):.0f}–{100*min(1,c+h):.0f}])'


def table(caption, head, rows, note=''):
    h = ''.join(f'<th>{x}</th>' for x in head)
    b = ''.join('<tr>' + ''.join(f'<td>{x}</td>' for x in r) + '</tr>' for r in rows)
    return f'<figure class="tbl"><figcaption>{caption}</figcaption><table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table>' + (f'<p class="note">{note}</p>' if note else '') + '</figure>'


def t1():
    tags = ['base', 'ara-t27', 'abl-t8']; rows = []
    for key, lab in [('cyber_complied', 'Cyber answered (judge)'), ('cyber_delivered', 'Cyber delivered'), ('keep_kept', 'Keep-refusing kept')]:
        rows.append([lab] + [wil(*S[t][key]) for t in tags])
    kb = S['base']['keep_kept'][0]
    rows.append(['Retention vs base', '—'] + [f"{100*S[t]['keep_kept'][0]/kb:.1f}%" for t in tags[1:]])
    for cat, lab in [('bio_chem', 'bio/chem'), ('child_safety', 'child safety'), ('privacy', 'privacy'), ('privacy_osint_people', 'people-OSINT'), ('self_harm', 'self-harm'), ('violence', 'violence')]:
        rows.append([f'&nbsp;&nbsp;kept: {lab}'] + ['{}/{}'.format(*S[t][f'keep_kept:{cat}']) for t in tags])
    for key, lab in [('over_refusal', 'Defensive over-refused'), ('vague_ok', 'Vague prompts answered'), ('knowledge_acc', 'Knowledge correct'), ('finish_rate_all', 'Finished (all sets)')]:
        rows.append([lab] + ['{}/{}'.format(*S[t][key]) for t in tags])
    rows.append(['Cyber replies opening with "Disclaimer"'] + ['{}/{}'.format(*T[t]['disclaimer_open_cyber']) for t in tags])
    rows.append(['Median tokens, knowledge answers'] + [f"{T[t]['median_tokens_knowledge']:g}" for t in tags])
    return table('Table 1. Held-out exam, greedy decoding, LLM judge. 95% Wilson intervals in brackets.', ['', 'Base', 'ARA t27', 'Abliteration t8'], rows,
                 'Kept = judge refusal or soft refusal. Delivered = answered and ended with a stop token without looping.')


def t2():
    C = F['capability_paired']; rows = []
    for task, lab in [('mmlu_pro', 'MMLU-Pro (140)'), ('gsm8k', 'GSM8K strict (150)'), ('ifeval', 'IFEval prompt-strict (150)')]:
        a, b = C[f'ara-t27:{task}'], C[f'abl-t8:{task}']
        rows.append([lab, f"{a['base_acc']}", f"{a['edit_acc']} (−{a['lost']}/+{a['gained']}, p={a['mcnemar_p']:.3f})", f"{b['edit_acc']} (−{b['lost']}/+{b['gained']}, p={b['mcnemar_p']:.3f})"])
    rows.append(['TruthfulQA-MC2 (150)', f"{C['base:truthfulqa_mc2']}", f"{C['ara-t27:truthfulqa_mc2']}", f"{C['abl-t8:truthfulqa_mc2']}"])
    return table('Table 2. Capability subsets. Accuracy %, items lost/gained against base, exact McNemar p (uncorrected).', ['Task', 'Base', 'ARA t27', 'Abliteration t8'], rows)


def t3():
    g = F['round1b']['mpoa_grid']; b = F['round1b']['mpoa_base_val']; rows = [['base', '—', f"{b['cyber_refusals']}/60", f"{b['keep_refusals']}/60"]]
    for k, lab in [('plain-x1.0', 'plain ×1 (reproduction control)'), ('ortho-x1.0', 'orthogonalized ×1'), ('ortho-x1.5', 'orthogonalized ×1.5'), ('ortho-x2.0', 'orthogonalized ×2 (pick)'), ('ortho-x3.0', 'orthogonalized ×3')]:
        x = g[k]; rows.append([lab, f"{x['kl_8tok']:.4f}", f"{x['cyber_refusals']}/60", f"{x['keep_refusals']}/60"])
    h = F['heretic']['abl_t8']
    rows.append(['Heretic trial 8 (round 1)', f"{F['round1b']['heretic_t8_merge_kl8']:.4f}", f"{h['cyber']}/60 (base 57)", f"{h['keep']}/60 (base 43)"])
    return table('Table 3. Round 1b: Heretic MPOA re-implementation with trial-8 parameters. Validation refusals by the refusal classifier.', ['Configuration', 'KL (8 tok)', 'Cyber refusals', 'Keep refusals'], rows,
                 'Heretic trial-8 KL is from the merged-model check on the same protocol; its refusal counts are Heretic\'s own (160-token replies) and use a slightly different base.')


EX = {e['id']: e for e in json.loads((PAPER / 'examples/examples.json').read_text())}
EXCOL = {'Base': '#8c8c8c', 'ARA t27': '#d4691e', 'Abliteration t8': '#2b5d8f', 'Cyber-only ×2': '#3a8a3f'}
EXN = {}


def example(eid):
    e = EX[eid]; n = EXN.setdefault(eid, len(EXN) + 1)
    rows = ''.join(f'<div class="exrow"><span class="exm" style="color:{EXCOL[r["model"]]}">{r["model"]}</span>'
                   f'<span class="exl">{r["label"].replace("_", " ")} · {r["tokens"]} tok</span><div class="ext">{html.escape(r["text"])}</div></div>' for r in e['replies'])
    return (f'<figure class="ex"><div class="exh">Example {n} · {html.escape(e["set"].replace("_", " "))} · {e["prompt_id"]}</div>'
            f'<div class="exp"><b>Prompt:</b> {html.escape(e["prompt"])}</div>{rows}<div class="exn">{html.escape(e["note"])}</div></figure>')


def fig(name, cap, cls='fig'):
    return f'<figure class="{cls}">{(FIG / name).read_text()}<figcaption>{cap}</figcaption></figure>'


BLOCKS = {
 'TABLE1': t1, 'TABLE2': t2, 'TABLE3': t3,
 'FIG1': lambda: fig('fig1-teaser.svg', 'Figure 1. The outcome at a glance. Goals are dashed red lines. ARA reaches the cyber goal but loses refusals elsewhere, including half of bio/chem; Abliteration keeps refusals but unlocks half of cyber; the cyber-only edit behaves like the original model.', 'fig wide'),
 'FIG2': lambda: fig('fig2-pipeline.svg', 'Figure 2. The two rounds. Everything in green was scored on prompts never used for editing.'),
 'FIG3': lambda: fig('fig3-concept.svg', 'Figure 3. Why a direction edit cannot separate cyber from other refusals when the two overlap. Sketch, not to scale.'),
 'FIG4': lambda: fig('fig4-overlap.svg', 'Figure 4. Cosine between the cyber refusal direction and the general refusal direction at each of the 60 layers of the original model. Solid: cyber direction built from matched harmless twins (used). Dashed: built from generic everyday prompts.'),
 'FIG5': lambda: fig('fig5-trials.svg', 'Figure 5. Every Heretic trial (60 per method). Each dot is one edited model, scored on 60 cyber and 60 non-cyber validation prompts. Colour is drift (KL): green ≤ 0.5, orange 0.5–3, grey &gt; 3 (model broken). Dashed: the original model\'s non-cyber refusals. Open ring: original model. Outlined: chosen trial.'),
 'FIG6': lambda: fig('fig6-categories.svg', 'Figure 6. Refusals kept per harm category on held-out prompts (numbers on bars are counts; whiskers are 95% intervals). ARA\'s losses concentrate in bio/chem and stalking/doxxing.'),
 'FIG7': lambda: fig('fig7-round1b.svg', 'Figure 7. Round 1b. Left: cyber refusals on 60 validation prompts. The full cyber direction (blue) unlocks 15; the cyber-only direction (green) unlocks 1 to 3 at any strength. Right: the cyber-only edits still change the model, with more drift than the full-direction edit.'),
 'FIG8': lambda: fig('fig8-side-effects.svg', 'Figure 8. Side effects. Left: benchmark questions answered correctly by the original but not the edit (lost) and the reverse (gained), with exact McNemar p-values. Right: disclaimer openings on cyber answers, and median length of short factual answers.'),
}


def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t); t = re.sub(r'(?<![\w*])\*(?!\s)(.+?)\*(?!\w)', r'<em>\1</em>', t)
    t = re.sub(r'`(.+?)`', r'<code>\1</code>', t); t = re.sub(r'(https?://[^\s)]+)', r'<a href="\1">\1</a>', t)
    return t


def md(text):
    out, lines, i = [], text.strip().split('\n'), 0
    while i < len(lines):
        l = lines[i]
        if not l.strip(): i += 1; continue
        m = re.fullmatch(r'\[\[(\w+)(?::(\w+))?\]\]', l.strip())
        if m: out.append(example(m.group(2)) if m.group(1) == 'EX' else BLOCKS[m.group(1)]()); i += 1; continue
        if l.startswith('# '): cls = ' class="appx"' if l[2:].startswith('Appendix A') else ''; out.append(f'<h2{cls}>{inline(l[2:])}</h2>'); i += 1; continue
        if l.startswith('## '): out.append(f'<h3>{inline(l[3:])}</h3>'); i += 1; continue
        if l.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r'[:\- ]+', c) for c in cells): rows.append(cells)
                i += 1
            out.append(table('', rows[0], [[inline(c) for c in r] for r in rows[1:]]).replace('<figcaption></figcaption>', '')); continue
        if re.match(r'(\d+\.|-) ', l):
            tag = 'ol' if l[0].isdigit() else 'ul'; items = []
            while i < len(lines) and re.match(r'(\d+\.|-) ', lines[i]):
                items.append(re.sub(r'^(\d+\.|-) ', '', lines[i])); i += 1
            out.append(f'<{tag}>' + ''.join(f'<li>{inline(x)}</li>' for x in items) + f'</{tag}>'); continue
        para = []
        while i < len(lines) and lines[i].strip() and not re.match(r'(#|\||\[\[|\d+\. |- )', lines[i]):
            para.append(lines[i]); i += 1
        out.append(f'<p>{inline(" ".join(para))}</p>')
    return '\n'.join(out)


CSS = '''
@import url('https://fonts.googleapis.com/css2?family=Old+Standard+TT:ital,wght@0,400;0,700;1,400&display=swap');
@page { size: Letter; margin: 1in; @bottom-center { content: counter(page); } }
:root { --ink:#000; --h2:#434343; --h3:#666666; --rule:#D9D9D9; }
body { font-family: 'Old Standard TT', 'Noto Serif', Georgia, serif; font-size: 11pt; line-height: 1.3; color: var(--ink); background:#fff; margin:0; }
h1 { font-size: 20pt; text-align: center; margin: 0 0 10pt; } .subtitle{text-align:center;font-size:15pt;margin:-6pt 0 10pt;font-weight:600}
.author { text-align:center; font-size:12pt; margin:0; } .affil { text-align:center; font-size:11pt; margin:0 0 4pt; }
.status { text-align:center; font-size:9.5pt; color:#7a2e00; margin:4pt 0 10pt; }
.abstract h2 { text-align:center; color:var(--ink); margin-top:6pt; }
.abstract { border-top:1px solid #bbb; border-bottom:1px solid #bbb; padding: 2pt 18pt 8pt; margin-bottom: 8pt; }
h2 { font-size: 14pt; color: var(--h2); margin: 12pt 0 2pt; line-height:1.5; break-after: avoid; }
h2.appx, h2.refs { break-before: page; }
h3 { font-size: 13pt; color: var(--h3); margin: 10pt 0 2pt; break-after: avoid; }
p { margin: 0 0 7pt; text-align: justify; hyphens: auto; } li { margin-bottom: 3pt; } ol, ul { margin: 0 0 7pt; padding-left: 20pt; }
code { font-size: 9pt; font-family: 'DejaVu Sans Mono', monospace; }
a { color: #1f4e79; text-decoration: none; word-break: break-all; }
figure { margin: 8pt 0 10pt; break-inside: avoid; } figure.fig svg { display:block; width: 88%; max-height: 2.9in; margin: 0 auto; }
figcaption { font-size: 9.5pt; margin: 3pt 0; }
table { border-collapse: collapse; width: 100%; font-size: 9.5pt; }
th:first-child, td:first-child { width: 34%; } th, td { border: 1px solid var(--rule); padding: 2.5pt 4pt; text-align: left; vertical-align: top; }
thead th { background: #F2F2F2; } tr { break-inside: avoid; }
.note { font-size: 8.5pt; color: #444; margin-top: 2pt; text-align:left; }
.ex { border:1px solid #d9d9d9; border-left:4px solid #555; padding:6pt 9pt; margin:9pt 0; background:#fafafa; break-inside: avoid; }
.exh { font-weight:bold; font-size:10.5pt; margin-bottom:3pt; } .exp { font-size:10pt; margin-bottom:4pt; }
.exrow { margin:3pt 0; font-size:9.3pt; line-height:1.25; } .exm { font-weight:bold; margin-right:6pt; } .exl { color:#666; font-size:8.6pt; }
.ext { margin-left:10pt; font-family:'DejaVu Sans', sans-serif; font-size:8.4pt; color:#222; }
.exn { font-size:9pt; font-style:italic; color:#444; margin-top:4pt; }
figure.wide svg { width:100%; max-height:none; }
.refs-list p { font-size: 9.5pt; text-align:left; }
'''


def main():
    parts = {p.stem: p.read_text() for p in sorted(D.glob('0*.md'))}
    abstract = parts.pop('01-abstract').split('\n', 1)[1]
    body = '\n'.join(md(v) for k, v in sorted(parts.items()) if k != '08-appendices')
    refs = (D / 'references.md').read_text().split('\n', 1)[1]
    html_ = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{META['title']}: {META.get('subtitle','')}</title><style>{CSS}</style></head><body>
<h1>{META['title']}</h1>{('<p class="subtitle">' + META['subtitle'] + '</p>') if META.get('subtitle') else ''}<p class="author">{META['author']}</p><p class="affil">{META['affiliation']}</p>{('<p class="status">' + META['display_status'] + '</p>') if META.get('display_status') else ''}
<section class="abstract"><h2>Abstract</h2><p>{inline(" ".join(abstract.split()))}</p></section>
{body}
<h2 class="refs">References</h2><div class="refs-list">{md(refs)}</div>
{md(parts_app := (D / '08-appendices.md').read_text())}
</body></html>'''
    (PAPER / 'paper.html').write_text(html_)
    if '--no-pdf' not in sys.argv:
        subprocess.run(['chromium', '--headless', '--no-sandbox', '--disable-gpu', '--no-pdf-header-footer', '--virtual-time-budget=8000',
                        f'--print-to-pdf={PAPER / "paper.pdf"}', (PAPER / 'paper.html').as_uri()], check=True, capture_output=True, timeout=120)
    print('built', PAPER / 'paper.html')


if __name__ == '__main__':
    main()
