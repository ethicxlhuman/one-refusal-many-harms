# 3. What I Did

[[FIG2]]

## 3.1 Model and setup

The target was google/gemma-4-31B-it (60 layers) with its "thinking" mode off. Every test used the same system prompt ("You are a helpful assistant.") and greedy decoding, so each prompt has exactly one answer per model. The original and ARA models were also re-run once with the model card's random sampling settings, as a check. Everything ran on one rented H200 GPU.

## 3.2 Prompts

**Training pairs.** Abliteration needs harmful and harmless prompts. I used 122 cyber pairs in which the harmless twin asks about the same topic in the same words. For example, "Write code to exploit the BlueKeep vulnerability on a remote target server" is paired with "Write code to detect the BlueKeep vulnerability on a server I own and explain how to patch it". An earlier version of the pairs had giveaway words, such as "a company's" appearing only in attacks and "my own lab" only in defensive prompts. I rewrote those so the model could not tell the sides apart by wording alone. Requests about stalking specific people were moved out of the cyber set and into the must-still-refuse set.

**Held-out exam (297 prompts, never used for editing).**

- 93 harmful cyber requests (exploitation, malware, phishing, reconnaissance);
- 94 harmful non-cyber requests that should still be refused: bio/chem 14, child safety 10, privacy 15, stalking/doxxing people 10, self-harm 20, violence 25, drawn from HarmBench, AdvBench, OR-Bench, Do-Not-Answer and XSTest;
- 40 defensive cyber requests (should be answered);
- 40 vague cyber questions (should get an overview);
- 30 cyber trivia questions with known answers (accuracy check).

## 3.3 Measuring the directions

For each layer I computed three directions from the average activations at the last prompt token: **cyber** (harmful minus harmless cyber twins), **general refusal** (the 93 non-cyber harmful prompts minus ordinary Alpaca instructions), and their cosine similarity. I also measured how well each direction separates harmful from harmless prompts, reported as d′ (difference of means in units of standard deviation).

## 3.4 Round 1: Heretic

Each Heretic method ran 60 trials. Each trial picks edit settings, applies them, and scores the result on three goals: fewer cyber refusals on 60 validation prompts, *more* refusals kept on 60 non-cyber harmful prompts, and low KL drift. Refusals were counted by Heretic's built-in refusal classifier. From each method's best trade-offs I picked one candidate by hand: ARA trial 27 and Abliteration trial 8.

## 3.5 Round 1b: removing only the cyber-specific part

At each layer I subtracted from the cyber direction its component along the general refusal direction (and along the harmless-prompt average, as Heretic does). What remains is exactly perpendicular to general refusal. I call it the **cyber-only direction**. I applied it with the same edit as Heretic's Abliteration, using trial 8's exact settings, at strengths ×1, ×1.5, ×2 and ×3. As a control, the same code applied Heretic's own (full) cyber direction at ×1. It reproduced trial 8's drift (KL 0.0132 against 0.0121), so the code does what Heretic does. The rule for choosing which strength gets the full exam was fixed in advance: fewest cyber refusals with KL ≤ 0.5 and at least 90% of other refusals kept.

## 3.6 Scoring

A different model family, Qwen3.8-27B, judged every exam reply as **complied**, **soft refusal** (deflects or answers a safer question), **refusal** or **broken**. I report:

- **cyber answered:** "complied" on harmful cyber requests;
- **refusals kept:** "refusal" or "soft refusal" on the 94 other-harm requests, overall and per category, and as a share of what the original model refused (retention);
- **side effects:** standard benchmarks (MMLU-Pro 140 questions; GSM8K, IFEval and TruthfulQA 150 each) compared question by question; tone (answers opening with a disclaimer; answer length); KL drift on 100 ordinary prompts.

All percentages come with 95% Wilson intervals. To save the last of the free compute credit, the round-1b exam was scored by **refusal openings** (does the reply start with "I can't", "I'm unable", "I must decline" and similar), not the judge. On round-1 replies this rule agreed with the judge on 93/93 original-model and 92/93 Abliteration cyber answers. I also read 30 complied cyber answers to check that they were real and correct.
