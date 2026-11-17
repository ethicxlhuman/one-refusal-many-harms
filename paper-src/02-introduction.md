# 1. Introduction

Chat models refuse harmful requests. For most users that is the right call, but penetration testers and red teams ask legitimate questions that look exactly like attacks: how a known exploit works, how phishing pages are built, how malware hides. They would like a model that answers those questions and still refuses the dangerous rest (bio/chem weapons, violence, child abuse, stalking real people).

Abliteration is the cheapest way to change refusal behaviour. Arditi et al. [1] showed that refusal in many chat models is controlled by a single direction in the model's internal activations. Subtract that direction from the weights and the model stops refusing. Public "uncensored" models are made this way, and the best of them lose little measured capability [5]. They also stop refusing everything.

So the question for a cyber-only model is whether cyber refusal has its own direction that can be removed while the others stay. Earlier work disagrees. Hadetskyi et al. [2] report that cyber-targeted abliteration was domain-specific on Kimi K2 and Gemma 3 12B but removed refusals across all domains on Gemma 3 27B. Zhao et al. [3] found that models represent *what kind* of harm a request is separately for each category, while the refusal signal itself is almost the same for every category.

[[FIG1]]

I tested this on Gemma 4 31B-it, a current 31-billion-parameter open model, with fixed success criteria: at least 80% of held-out cyber requests answered, at least 90% of the model's other refusals kept, and at most a 1-point loss on standard benchmarks. Figure 1 summarizes the outcome. No edit came close.

The paper makes three points:

1. **The overlap is measurable before any editing, and it predicted the failure.** Cyber refusal and general refusal point the same way inside the model, and both Heretic methods traded one against the other along a single curve.
2. **Removing only the cyber-specific part does nothing.** That part still distinguishes harmful from harmless cyber requests, but erasing it does not stop the model refusing. The refusal itself lives in the shared part.
3. **A single cyber score hides the damage.** The edit that "worked" on cyber also answered bio/chem weapon requests, padded answers with disclaimers, and was scored very differently by two automatic graders.

This is an AI-safety measurement study. It tells deployers what to test for, and it shows that on this model a cheap cyber-only unlock is not available.
