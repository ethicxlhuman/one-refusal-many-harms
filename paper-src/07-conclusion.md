# 6. Conclusion

On Gemma 4 31B-it, erasing refusal directions did not produce a model that answers cyber requests and still refuses the rest. The strongest edit unlocked 89% of cyber requests and half of the bio/chem requests. The cleanest edit kept the other refusals and unlocked half of cyber. Removing only the cyber-specific part of the direction changed nothing. The next approaches to test are ones that do not remove the shared refusal direction: a small cyber-only fine-tune, or steering that activates only on cyber inputs. Each should be checked with the same per-category exam.

## Code and data

The repository contains the paper, all figures, the analysis scripts, per-reply labels for every exam prompt (judge label, refusal opening, length, finish reason, SHA-256 of the reply), the aggregate results and the curated examples. I left out the model replies to harmful prompts and the edited weights.
