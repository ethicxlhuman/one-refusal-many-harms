# Appendix A. More examples

[[EX:E3]]

[[EX:E4]]

[[EX:E8]]

[[EX:E6]]

[[EX:E7]]

The last example shows why the privacy numbers are slightly strict. The judge counted "I don't have access to that, but here is how to look it up internally" as compliance for both Heretic edits; the original model said almost the same thing and was counted as a refusal. Four privacy prompts behave this way.

# Appendix B. Full results table

[[TABLE2]]

[[TABLE3]]

# Appendix C. Reproducibility

| Item | Value |
|---|---|
| Target | google/gemma-4-31B-it @ 842da3794eaa0b77d5f08bae87a17459d91ff475, thinking off |
| Judge | Qwen/Qwen3.8-27B @ 37561816e66b5b9153b1b64c10968c18c1e6f4a0, non-thinking, temperature 0 |
| Refusal classifier (Heretic) | VINAY-UMRETHE/Refusal-Classifier @ 8d60280075beb3d5dc3b416cfed14dea53dec2bb |
| Heretic | 2.1.0, seed 2026, 60 trials (20 random start-up), replies 160 tokens |
| Stack | torch 2.14.0, transformers 5.20.2, vLLM 0.33.0, lm-eval 0.4.13 |
| ARA trial 27 | layers 9–56; preserve-good 0.0203; steer-bad 0.0142; overcorrect 0.168; neighbours 5 |
| Abliteration trial 8 | o_proj max 0.995 at layer 55.6, min 0.737, distance 32.5; down_proj max 0.246 at 39.4, min 0.057, distance 29.3 |
| Exam caps | 1,536 tokens cyber/defensive, 1,024 other-harm/vague, 512 trivia, 128 child safety |
| Hardware | 1 × NVIDIA H200 141 GB |

# Appendix D. Disclosures

**AI assistance.** An AI coding agent (Claude) wrote the experiment code under my direction, ran the jobs, recomputed every number from the stored outputs, did the 30-answer read and drafted the text. I set the research question, the success criteria and the safety rules, and approved every spend.

**Resources.** Free cloud GPU credit (Modal); nothing was billed. No institutional affiliation.
