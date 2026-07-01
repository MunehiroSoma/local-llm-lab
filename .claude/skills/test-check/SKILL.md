---
description: 実装完了判定チェックリストを実行し、テスト記録テンプレートを提供する
metadata:
    github-path: skills/test-check
    github-ref: refs/heads/main
    github-repo: https://github.com/MunehiroSoma/ai-dev-kit
    github-tree-sha: 4c4f6edf1623c4dbaecc7e4fa7be574154f9f2c7
name: test-check
---
# skill: test-check

実装完了判定チェックリストを実行する。

## 使い方

```
/test-check <対象機能名>
例: /test-check EventService
```

## 実装完了の定義

以下をすべて満たすまで「完了」としない。

- [ ] `<TEST_CMD>` が通過する
- [ ] `<LINT_CMD>` エラーなし
- [ ] `<FORMAT_CMD>` で差分なし
- [ ] 正常系が確認されている
- [ ] 異常系が確認されている（不正入力・外部 API エラー）
- [ ] ログで問題を切り分け可能である
- [ ] 確認結果の記録（`docs/` 配下のテスト記録）

## 正常系の最低確認項目

- [ ] 期待通りの出力が返る
- [ ] DB にレコードが保存される（DB 操作がある場合）
- [ ] ファイルが保存される（ファイル出力がある場合）

## 異常系の最低確認項目

- [ ] 不正入力で適切なエラーが返る
- [ ] 外部 API 障害時に適切にフォールバック／エラーが返る
- [ ] エラーログに技術的な詳細が残る

## モデル・オンボーディング（harness/eval作業）向け完了条件

`model-onboarding` Issue や `exp/*` `model/<id>` ブランチの作業では、上記に加えて以下を満たすまで「完了」としない（research §13.5 / §12.4）。

- [ ] レイヤ1 **Fit**: 実ロードでOOMが発生しない（対象 max_model_len）
- [ ] レイヤ2 **Speed**: tok/s・TTFT・(MM時)前処理時間を計測済み
- [ ] レイヤ3 **標準ベンチ**: 用途別の足切りベンチ（SWE-bench/Aider/MMMU/llm-jp-eval等）を実施
- [ ] レイヤ4 **自前タスク評価**: promptfoo/DeepEval（日本語含む）を実施
- [ ] `results/results.csv` に1行追記済み（追記のみ、既存行の書き換え禁止）
- [ ] 判定（採用 / 保留 / 不採用）と理由を記録済み
- [ ] Operations フェーズの受け入れ承認（人間）が済んでいる

## テストケース記録テンプレート

`docs/<カテゴリ>/TC_<機能名>.md` に以下の形式で記録する。

```markdown
# TC_<機能名>

## 実施情報
- 実施日: YYYY-MM-DD
- 実施者: <名前>

## 正常系
- （確認内容）

## 異常系
- （確認内容）

## 未確認
- （未確認項目）

## 備考
- （特記事項）
```

## 実行後の改善確認（必須）

スキル実行の最後に、次を必ず人間へ確認する。

1. 今回の進め方の感想（良かった点）
2. 使いにくかった点・迷った点（使い勝手）
3. エージェントからの改善提案（手順 / コマンド / 出力）
4. このスキルを今すぐ更新するか（Yes / No）

### 遷移ルール

- Yes: `/update-skill test-check` を実行し、改善案を提示して承認後に反映する
- No: 更新見送り理由を 1 行で記録し、次回見直しの条件を確認する
