# datasets — 評価データ

## 方針（PUBLIC リポジトリ）
- `golden/` … **自前ゴールデンセット（本番評価データ）。実データはコミット禁止**（`.gitignore` で保護）。
  - 実データ（例: 既存システムの仕様書、自分の文書）はローカル or 別 private 保管。
  - **`golden/samples/` に公開可能な少数サンプルのみ**を置く。
- CIガード（`.github/workflows/validate.yml`）が samples 以外の混入を検知。

## ゴールデンセットのスキーマ（例）
各用途で 30–100 件。JSONL 推奨。

### コーディング（仕様書駆動）
```jsonl
{"id":"code-001","spec_path":"...","repo":"...","task":"...","test_cmd":"pytest -q","rubric":"..."}
```
### 要約・タグ付け
```jsonl
{"id":"tag-001","input":"...","gold_tags":["..."],"json_schema":"schemas/tag.json"}
{"id":"sum-001","input":"...","reference":"...","rubric":"忠実性/網羅性/日本語"}
```
### コンシェルジュ（多モーダルQA）
```jsonl
{"id":"con-001","image":"samples/img/...","audio":null,"question":"...","rubric":"正確性/日本語/幻覚"}
```

## 使い方
`harness/task/`（promptfoo/DeepEval）から参照。judge モデルは固定（ADR/研究 §13.5）。
