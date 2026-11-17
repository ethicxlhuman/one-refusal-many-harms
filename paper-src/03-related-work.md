# 2. Background

**Terms used in this paper.**

- **Refusal direction.** Average the model's internal activations over harmful requests and over harmless ones; the difference is a direction. Pushing activations along it makes the model refuse; removing it makes the model comply [1].
- **Abliteration.** Editing the weights so the model can no longer write along the refusal direction. It needs no training data beyond the two prompt sets.
- **Cosine similarity.** How much two directions point the same way: 1 means the same direction, 0 means unrelated.
- **KL divergence.** How much the edited model's word predictions on ordinary prompts differ from the original's. Near 0 means the model behaves the same on normal requests.
- **Heretic** [4] is an open tool that searches for good abliteration settings automatically. Version 2.1.0 offers two methods: *ARA* (Arbitrary-Rank Ablation, its default) and *Abliteration* (classic direction removal with a norm-preserving update [9]).

**Related work.** Arditi et al. [1] found one refusal direction in 13 open chat models. Wollschläger et al. [6] found several independent refusal directions and showed that two directions can be geometrically unrelated and still interact when one is edited, which is why I tested the cyber-only direction by editing it rather than by measuring angles. Zhao et al. [3] separated a "harmfulness" signal, which differs by harm category, from a "refusal" signal, which is nearly shared (average cosine 0.89 across categories for one category in Qwen2). Park et al. [7] removed the shared harm component from each category and pushed models along the category-specific remainder; whether that remainder caused refusal depended on the category and the model. My round-1b experiment is the removal version of that test, for cyber, on one model.

On cyber specifically, Hadetskyi et al. [2] abliterated 24 models with cyber-focused prompts and string-matched refusals. On Kimi K2 cyber refusal fell from 100% to 7% while explicit-content refusal stayed at 100%. On their public benchmark, cyber fell 88%→51% and chem/bio 100%→88%. Gemma 3 27B lost refusals everywhere. Palette [8] relaxes refusals per domain with learned adapters. On Gemma 4 12B, a small fine-tuned cyber adapter compared by Abliterlitics [5] raised cybercrime compliance from 7/67 to 24/67 while leaving chem/bio at 2/56. It was selective, but it left most cyber requests refused.

I found no earlier test of removing a category-orthogonalized refusal direction on Gemma 4 31B (searches on 2026-11-17). I make no broader novelty claim.
