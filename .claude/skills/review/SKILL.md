---
description: 観点カテゴリごとにサブエージェントを並列起動し、指摘を集約してレビューする（ADR 0006）
metadata:
    github-path: skills/review
    github-ref: refs/heads/main
    github-repo: https://github.com/MunehiroSoma/ai-dev-kit
    github-tree-sha: 4114a3a619b78151c9c68b0f693dfe8980c2e429
name: review
---
# skill: review

`docs/coding-standards/review-checklist.md` の観点カテゴリごとにサブエージェントを並列起動し、
指摘を集約するレビュースキル（ADR 0006 の観点分割方針を反映）。

## 使い方

```
/review <対象機能名 or ファイルパス>
例: /review EventService
例: /review app/core/event_generation.py
```

## 実行タイミング

- **PR作成時（`ship` 実行後、人間承認前）のみ**に実行する。
- push のたびには実行しない（機械的チェックは既存の pre-commit / CI ruff・mypy で代替済みのため）。

## 観点特化サブエージェントの起動

`docs/coding-standards/review-checklist.md` の観点カテゴリに対応する Explore 系サブエージェントを
並列起動する。各エージェントは自分の観点のチェックリストファイルのみを読み、担当外のファイルは読まない。

| 観点 | チェックリスト | 入力範囲 | 想定モデル |
|---|---|---|---|
| 基本品質 | `docs/coding-standards/review-checklist/01-basic-quality.md` | 差分のみ | 軽量 |
| エラー処理 | `docs/coding-standards/review-checklist/02-error-handling.md` | 差分のみ | 軽量 |
| セキュリティ | `docs/coding-standards/review-checklist/03-security.md` | 差分のみ | 上位 |
| テスト | `docs/coding-standards/review-checklist/04-test.md` | 差分のみ | 軽量〜中位 |
| 設計整合性 | `docs/coding-standards/review-checklist/05-design-consistency.md` | 差分 + ADR/研究ノート | 上位 |
| harness-eval-registry | `docs/coding-standards/review-checklist/06-harness-eval-registry.md` | 差分のみ（registry変更時はADRも） | 上位 |

- **モデル適材適所**: 規約・フォーマット系の機械的チェック（命名・import整理・禁止パターン検出等）は軽量モデル、
  設計判断・harnessロジック・アーキテクチャ整合性の判断が必要な観点は上位モデルで起動する。
- **起動規模の可変**: 変更差分が小さい（目安: 5ファイル未満）場合は主要観点（基本品質・エラー処理・テスト）のみ、
  model-onboarding や大規模harness変更等は全観点を起動する。

## 観点特化サブエージェントのノイズ抑制ルール（必須遵守）

- 良い点の指摘をしない（指摘のみに集中する）
- 修正案の提案はしない（修正は実装者/別スキルの責務）
- YAGNI違反（過剰設計）の指摘はしない
- 差分に含まれない既存実装への指摘はしない
- 観点ごとに入力範囲を絞る（担当外の観点のファイル・チェックリストは読まない）

## 権限方針

観点特化サブエージェントには **Read/Grep/Glob 相当の読み取り専用権限のみ**を与える。書き込みはさせない。

## 出力形式

観点特化サブエージェントの出力は次の形式に統一する。

```
SEVERITY(Must/Should/Nits) / FILE / LINE / ISSUE / 観点
```

例:

```
Must / app/core/event_generation.py / 42 / 例外を握りつぶしている（空のexcept） / エラー処理
Should / app/api/event.py / 10 / タイムアウト未設定 / セキュリティ
Nits / tests/test_event.py / 5 / テスト名が命名規約に沿っていない / テスト
```

`review` スキル本体は各エージェントの出力を集約し、重複を排除してから提示する。

> 言語固有の規約レビューが必要な場合は、別途 `py-review` 等の言語別スキルを併用する。

## 実行後の改善確認（必須）

スキル実行の最後に、次を必ず人間へ確認する。

1. 今回の進め方の感想（良かった点）
2. 使いにくかった点・迷った点（使い勝手）
3. エージェントからの改善提案（手順 / コマンド / 出力）
4. このスキルを今すぐ更新するか（Yes / No）

### 遷移ルール

- Yes: `/update-skill review` を実行し、改善案を提示して承認後に反映する
- No: 更新見送り理由を 1 行で記録し、次回見直しの条件を確認する
