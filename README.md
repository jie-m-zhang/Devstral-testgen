# Devstral-testgen

Test generation for [SWT-bench Lite](https://swtbench.com) using [Devstral](https://mistral.ai/news/devstral).

## Results

| Benchmark | Score |
|-----------|-------|
| SWT-bench Lite | 81.8% (216/264 evaluated) |

Predictions: [`predictions.jsonl`](./predictions.jsonl)

## Approach

Devstral-testgen generates reproducing tests for software bugs using Devstral as the underlying model.

Given a GitHub issue and the codebase at the pre-fix commit, the system:

1. Loads instances from the [SWT-bench Lite dataset](https://huggingface.co/datasets/logic-star-ai/swt-bench)
2. Runs Devstral inside SWT-bench's native Docker containers (same images used for evaluation)
3. Generates a test that reproduces the described bug
4. Validates the test with **F→P semantics** — the test must *fail* on the base (buggy) commit and *pass* on the fixed commit
5. If validation fails, attempts up to 3 repair rounds using execution output as feedback

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](./LICENSE) file for details.
