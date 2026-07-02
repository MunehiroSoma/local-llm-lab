# harness/task/coding_agent — Spec-Driven Coding Agent Eval

仕様書駆動の coding-agent 評価ケースを実行し、agent command と test command の成否から
`task_score` を記録する。Aider / OpenHands / Codex などの実行コマンドは case YAML 側で固定する。

```bash
python3 -m harness.task.coding_agent.run_case \
  --case harness/task/coding_agent/case.example.yaml \
  --append-results
```

運用時はケースごとに一時作業ディレクトリを用意し、評価対象リポジトリや fixture を固定する。
この公開リポジトリには実案件の仕様書・ソース断片を置かない。
