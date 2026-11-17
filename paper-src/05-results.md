# 4. Results

## 4.1 Before editing: cyber refusal and general refusal overlap

[[FIG4]]

In the first 18 layers the cyber direction and the general refusal direction are unrelated (cosine −0.40 to 0.10). From layer 21 to the last layer they point the same way, with cosine 0.67 to 0.86 (Figure 4). Inside the model, "this is a harmful cyber request" and "this is a harmful request" are mostly the same signal in the layers where refusal is decided.

[[FIG3]]

Figure 3 shows what that means for editing. Any cut along the cyber direction also cuts along general refusal. A strong cut unlocks cyber and leaks other refusals; a gentle cut leaks less and unlocks less. Only the perpendicular "cyber-only" part could in principle unlock cyber alone. Round 1b tests whether that part does anything.

Two practical notes. Building the cyber direction from generic harmless prompts (everyday instructions instead of matched cyber twins) gives a stronger-looking direction (d′ 13.8 against 4.7) that overlaps general refusal even more (cosine 0.76 to 0.95), because it also encodes "cyber topic versus everyday topic". I used the matched twins. And this whole check took minutes on the original model, before any search.

## 4.2 Round 1: both Heretic methods trade cyber against everything else

[[FIG5]]

Figure 5 plots all 120 Heretic trials. The original model refused 57 of 60 cyber validation prompts and 43 of 60 non-cyber ones. A selective edit would land at the far left on the dashed line. No trial did.

**ARA** found no gentle edit that unlocked cyber. Of 60 trials, only one stayed under KL 0.5, and it unlocked 5 cyber prompts. Two trials scored a "perfect" 0 refusals on both sets because they broke the model (KL above 19); refusal counts alone would have selected them. I picked trial 27: cyber refusals 57→28, non-cyber refusals unchanged at 43, KL 1.91.

**Abliteration** stayed gentle (KL at most 0.43 in all 60 trials), but cyber unlocking and leakage moved together. Across trials, the drop in cyber refusals and the drop in other refusals correlate at r = 0.87. The strongest cyber cut (57→37) also cut other refusals from 43 to 23. I picked trial 8: cyber 57→46, others 43→41, KL 0.076.

## 4.3 Held-out exam

[[TABLE1]]

On the 297 held-out prompts (Table 1), **ARA trial 27** answered 83 of 93 cyber requests (89%, interval 81–94%) and refused none outright. But it kept only 71 of the 90 refusals the original model made (79%). **Abliteration trial 8** kept 85 of 90 (94%) and answered 46 of 93 cyber requests (49%, interval 40–59%). Neither meets both goals. The re-run with random sampling agrees for ARA: 82/93 cyber answered, 70/94 refusals kept.

[[FIG6]]

The per-category view (Figure 6) shows where ARA's lost refusals went. Bio/chem dropped from 14/14 to 7/14 and stalking/doxxing people from 8/10 to 3/10. Both intervals exclude the original rate. Abliteration kept every bio/chem refusal. The smaller drops (child safety, violence, privacy) are within noise at these sample sizes.

## 4.4 What the answers actually looked like

The examples below are real, unedited replies (greedy decoding, text shortened). Labels are the judge's, except for the cyber-only edit (refusal openings). Where a model answered a harmful request, only the opening sentence is shown and the rest is withheld. More examples are in Appendix A.

[[EX:E1]]

Example 1 shows the typical pattern. The original model refuses and offers a defensive overview instead. ARA opens with a boilerplate disclaimer and then answers. Abliteration refuses the code but explains the vulnerability in detail (a soft refusal). The cyber-only edit gives almost the same refusal as the original, word for word.

[[EX:E2]]

Example 2 is the harmless twin of Example 1, a request to *detect and patch* the same vulnerability on one's own server. The original model over-refuses it, and so does the cyber-only edit; both Heretic edits answer it. On the full defensive set, though, the original model refused only 1 of 40.

[[EX:E5]]

Example 3 is the leak. The original model, Abliteration and the cyber-only edit refuse a bio/chem request. ARA answers it with the same disclaimer template it uses for cyber. Seven of the 14 bio/chem requests went the same way.

## 4.5 Round 1b: removing only the cyber-specific part changes nothing

The cyber-only direction is still informative. It separates harmful from harmless cyber twins almost as well as the full cyber direction (d′ 6.1 against 6.6 at layer 45, computed on the training prompts). If the model refused cyber requests because of what is specific to cyber, removing this direction should unlock them.

[[FIG7]]

It does not (Figure 7). With the full cyber direction, the reproduced Heretic edit brought cyber refusals on the validation set from 56 down to 41 of 60 at very low drift. With the cyber-only direction, refusals stayed at 55, 55, 53 and 53 of 60 at strengths ×1 to ×3. The edit was strong enough to matter. Its drift rose to KL 0.45, 34 times that of the full-direction edit. It changed the model's outputs without changing whether the model refused.

On the full exam, the pre-selected ×2 edit opened 84 of 93 cyber replies with a refusal, against 86 of 93 for the original model, and kept every bio/chem, child-safety, self-harm and violence refusal. Examples 1, 3 and 4 show its replies next to the original's, nearly word for word.

## 4.6 Side effects a cyber score does not show

[[FIG8]]

**Benchmarks.** ARA's benchmark scores fell by up to 6 points, but on 140 to 150 questions most of that is within noise. Comparing the same questions before and after, only its GSM8K math loss is clear: 8 questions lost, 1 gained (p = 0.04; Figure 8). Abliteration lost 1 to 3 questions per benchmark (p ≥ 0.6). TruthfulQA fell from 67.1 to 61.5 for ARA and to 66.7 for Abliteration.

**Tone.** ARA opened 68 of 93 cyber answers with "Disclaimer: This information is provided for educational…", and it doubled the length of short factual answers (Example 6 in Appendix A: a one-line CVE answer became a 150-token summary). Abliteration added disclaimers to 24 of 93 cyber answers and kept short answers short. The judge counts a disclaimer-wrapped answer as compliance, so this drift only shows up when measured on its own.

**Drift.** On 100 ordinary prompts, ARA trial 27 had KL 0.37 and Abliteration trial 8 had KL 0.012.

**Two graders, two answers.** Heretic's built-in refusal classifier, which steered the search, still counted 28 of 60 ARA replies as refusals. The LLM judge found 0 outright refusals and 10 soft refusals in 93 held-out replies. The sets differ, but the gap is large. The search saw much less unlocking than the exam found.

**Correctness.** I read 30 answered cyber replies (20 ARA, 10 Abliteration). All 30 delivered what was asked. I saw no factual errors (for example, the cloud metadata address, the KNOB Bluetooth attack and the SMB session sequence were all described correctly). The content was textbook-level, and no code was run.

## 4.7 Cost

All runs used free cloud credit on one H200 GPU: $17.93 for round 1 and $2.58 for round 1b, metered by the provider, $20.51 in total. Nothing was billed. The two Heretic searches were the largest items: ARA took 1 h 36 min ($8.03) and Abliteration 57 min ($4.76).
