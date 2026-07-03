# qwen3-coder-30b-a3b coding-agent-public-v1 report

## Summary

| Item | Value |
|---|---|
| Issue | #63 `[BOLT] onboard qwen3-coder-30b-a3b` |
| Model | `qwen3-coder-30b-a3b` |
| Runtime | `ollama` |
| Environment | `mac` |
| Endpoint | `http://127.0.0.1:11434/v1` |
| Task set | `coding-agent-public-v1` |
| Judge | `deterministic-json-files-pytest-rubric-v1` |
| Raw evidence | `results/raw/qwen3-coder-30b-a3b-coding-agent-public-v1.json` |

## Existing onboarding status

Issue #63 already records Mac / Ollama Layer 1-2 measurements:

- Fit: `yes`
- Speed: `tok_s=78.0234`, `ttft_ms=111.398`
- Ollama model id: `06c1097efce0`
- Source revision: `b2cff646eb4bb1d68355c01b18ae02e7cf42d120`

This report records only the Layer 4 `coding-agent-public-v1` result. Layer 3
standard benchmark, `results/results.csv` append, and final adopt/hold/reject
verdict remain separate Operations-gate work.

## Command

```bash
python3 -m harness.task.coding_agent.run_case \
  --base-url http://127.0.0.1:11434/v1 \
  --model qwen3-coder-30b-a3b \
  --runtime ollama \
  --env mac \
  --profile coding \
  --output-json results/raw/qwen3-coder-30b-a3b-coding-agent-public-v1.json
```

The command intentionally omitted `--append-results`.

## Result

| Metric | Value |
|---|---:|
| task_count | 2 |
| passed_count | 1 |
| mean_score | 0.96875 |
| median_tok_s | 76.37836650834119 |
| median_ttft_ms | 4791.938749998735 |

## Task details

| Task | Passed | Score | Notes |
|---|---:|---:|---|
| `slug-normalizer` | no | 0.9375 | Public pytest passed, but fixed marker `re.sub` was missing. |
| `kv-parser` | yes | 1.0 | Schema, file path, markers, and public pytest all passed. |

The failed task is a rubric-marker miss rather than a public-test failure: the
generated slug normalizer collapsed separators with string replacement instead
of using `re.sub`, so marker coverage was `3/4` while tests passed.

## CSV status

`results/results.csv` was not modified. If this Layer 4 row should be appended,
the exact row must be presented for Operations approval before rerunning with
`--append-results`.
