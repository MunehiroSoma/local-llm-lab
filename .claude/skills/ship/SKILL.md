---
description: 現在のブランチの変更をコミット → push → PR 作成まで一括で行う
metadata:
    github-path: skills/ship
    github-ref: refs/heads/main
    github-repo: https://github.com/MunehiroSoma/ai-dev-kit
    github-tree-sha: 7a8633b2cf8d7f4a0ee055cfc53e9821a26be2dd
name: ship
---
# skill: ship

現在のブランチの変更をコミット → push → PR 作成まで一括で行う。

> 本リポジトリの `<MERGE_STYLE>` = **squash**（conventions.md 準拠、固定）。
> マージは AI-DLC の Construction フェーズ完了ゲート（PRレビュー承認）を経てから行う。

## 使い方

```
/ship <コミットメッセージ>
例: /ship feat: DBスキーマとマイグレーション実装
```

## 手順

0. 作業ツリーの汚れを確認する
   ```bash
   git status --short
   ```
   - 対象 Issue と無関係な変更がある場合は、そのまま push/PR しない
   - dirty の場合は一時 worktree で隔離するか `git stash` で退避する
   - 変更破棄（`git restore` など）はユーザー確認なしで実行しない

1. 変更ファイルと検証を確認する
   ```bash
   git status
   git diff --stat
   <PRECOMMIT_CMD>   # または <LINT_CMD> / <FORMAT_CMD>
   ```

2. ステージングとコミット
   ```bash
   git add <関連ファイル>
   git commit -m "<type>: <概要>"
   ```

3. push する
   ```bash
   git push origin <current-branch>
   ```

4. PR を作成する（関連 Issue があれば `Closes #XX` を含め、なければ `N/A` を明記）
   ```bash
   gh pr create --title "<type>: <概要>" --body "## 概要
   <変更内容>

   ## 関連 Issue
   Closes #<番号>   # なければ N/A

   ## 確認事項
   - [ ] 正常系確認
   - [ ] 異常系確認
   - [ ] テスト追加（該当時）
   - [ ] 検証コマンド通過"
   ```

5. **人間承認ゲート（必須・省略不可）**
   - PR URL を人間へ提示し、レビュー結果（マージしてよいか）を待つ
   - AI-DLC の Construction フェーズ遷移ゲートに相当するため、承認が出るまで手順6へ進まない

6. マージと後処理（承認後のみ実行）
   ```bash
   gh pr merge <PR番号> --squash --delete-branch
   git checkout main
   git pull origin main
   ```

- 方針: 統合後は不要ブランチを削除して `main` に戻った状態を作業の終了条件にする
- マージ方式は本リポジトリの規約（conventions.md）に従い **squash 固定**

## コミットメッセージ規則

| type | 意味 |
|---|---|
| `feat` | 新機能 |
| `fix` | バグ修正 |
| `docs` | ドキュメント |
| `refactor` | リファクタリング |
| `chore` | 設定変更 |
| `test` | テスト追加・修正 |

## 実行後の改善確認（必須）

スキル実行の最後に、次を必ず人間へ確認する。

1. 今回の進め方の感想（良かった点）
2. 使いにくかった点・迷った点（使い勝手）
3. エージェントからの改善提案（手順 / コマンド / 出力）
4. このスキルを今すぐ更新するか（Yes / No）

### 遷移ルール

- Yes: `/update-skill ship` を実行し、改善案を提示して承認後に反映する
- No: 更新見送り理由を 1 行で記録し、次回見直しの条件を確認する
