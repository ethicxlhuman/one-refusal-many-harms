# 5. Discussion and Limitations

## 5.1 What this means

The three results fit one picture. Gemma 4 31B represents *what kind* of harmful request it is reading with a component specific to cyber, but it *refuses* through a component shared with every other harm. ARA removed much of the shared component, so cyber unlocked and bio/chem leaked. Abliteration removed a little, so little leaked and only half of cyber unlocked. Removing only the cyber-specific component left refusal untouched. The same picture appears in Zhao et al.'s study of other models [3], and Hadetskyi et al. saw the same all-domain collapse on Gemma 3 27B [2]. It does not contradict their domain-specific results on Kimi K2 and Gemma 3 12B; selectivity depends on the model.

For practitioners, the overlap check is cheap and predictive. If the cyber and general refusal directions have a cosine above about 0.7 in the layers that carry refusal, expect a direction edit to trade cyber unlock against other refusals, and evaluate other harm categories one by one.

For safety evaluation, the lesson is in Figure 1's third panel. An edit can pass a cyber-only score while answering bio/chem weapon requests. Per-category refusal checks, tone and length measures, paired benchmark tests and a second grader all changed the picture here.

## 5.2 Limitations

- **One model, one run.** One model, one random seed and one search per method, with candidates picked by hand. Other models may separate cyber refusal; Hadetskyi et al. report some that do [2].
- **Small categories.** Bio/chem has 14 prompts and child safety 10. Only ARA's bio/chem and stalking drops are clearly outside noise. One bio/chem prompt (K004) is actually a drug-synthesis request and is mislabelled.
- **One automatic judge.** The hand-read of 30 answers was done by an AI assistant, not a human expert, and no code was executed.
- **Round 1b was not judged.** It was scored by refusal openings. That rule matched the judge on cyber replies but undercounts other-harm refusals, because many of those open with a redirect.
- **Training-set statistics.** The overlap and d′ values come from the prompts used to build the directions; I did not measure them on held-out prompts.
- **One kind of edit.** Round 1b removed one perpendicular direction per layer with one recipe. It did not test multi-direction edits [6], steering that switches on only for cyber inputs, or fine-tuning.
- **Reproduction detail.** The reproduced Heretic edit matched its drift and its non-cyber refusals, but unlocked 5 more cyber validation prompts than Heretic reported. The likely cause, shorter test replies (96 versus 160 tokens), was not tested.
- **Small benchmarks.** 140 to 150 questions per benchmark; differences under about 3 points are noise.

## 5.3 Responsible release

I do not release the edited weights or the full model replies. Some replies contain working offensive-security content, and ARA's replies include answers to bio/chem and child-safety requests. In the paper and repository I show prompts, refusals, harmless answers and the opening sentence of harmful answers. Each full reply is identified by a SHA-256 hash, so anyone given the private files can check every label.
