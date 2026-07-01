---
description: 新しいブランチを main から切って開発を開始する
metadata:
    github-path: skills/new-feature
    github-ref: refs/heads/main
    github-repo: https://github.com/MunehiroSoma/ai-dev-kit
    github-tree-sha: 85f6bc18f0f05c444c41187f9a7585f51b677ed2
name: new-feature
---
# skill: new-feature

新しいブランチを main から切って開発を開始する。

## 使い方

```
/new-feature <prefix>/<ブランチ名>
例: /new-feature feat/eval-runner
例: /new-feature exp/gemma4-mac-swebench
例: /new-feature model/gemma4-26b-a4b
```

## 手順

1. main を最新に更新する
   ```bash
   git checkout main
   git pull origin main
   ```

2. ブランチを作成して移動する
   ```bash
   git checkout -b <prefix>/<ブランチ名>
   ```

3. ブランチ名・目的をユーザーに確認して開発を開始する

## ブランチ命名規則（本リポジトリ = conventions.md 準拠）

| プレフィックス | 用途 | 例 |
|---|---|---|
| `feat/` | harness等の機能 | `feat/eval-runner` |
| `fix/` | 修正 | `fix/login-retry` |
| `exp/` | 計測ラン・実験（BOLT） | `exp/gemma4-mac-swebench` |
| `model/<id>` | モデル追加・検証（BOLT） | `model/gemma4-26b-a4b` |
| `env/` | 環境構築（runbook/compose） | `env/dgx-spark-vllm` |
| `docs/` | 資料 | `docs/api-reference` |
| `chore/` | 雑務・設定 | `chore/update-deps` |

- すべて英小文字・ハイフン区切り。日本語・スペース・アンダースコア禁止。
- BOLT（Unit of Work = モデル×環境×評価、または harness の1機能）は `exp/*` `model/<id>` を優先して使う。

## 実行後の改善確認（必須）

スキル実行の最後に、次を必ず人間へ確認する。

1. 今回の進め方の感想（良かった点）
2. 使いにくかった点・迷った点（使い勝手）
3. エージェントからの改善提案（手順 / コマンド / 出力）
4. このスキルを今すぐ更新するか（Yes / No）

### 遷移ルール

- Yes: `/update-skill new-feature` を実行し、改善案を提示して承認後に反映する
- No: 更新見送り理由を 1 行で記録し、次回見直しの条件を確認する
