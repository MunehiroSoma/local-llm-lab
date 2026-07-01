---
description: 作業開始時に GitHub Issues を確認し、ブランチ作成まで一括実行する
metadata:
    github-path: skills/start
    github-ref: refs/heads/main
    github-repo: https://github.com/MunehiroSoma/ai-dev-kit
    github-tree-sha: a9941787a8edf6b61d5a95250301b24cec56bc85
name: start
---
# skill: start

新しい作業を始める前に GitHub Issues を確認し、取り掛かる Issue を選んでブランチを切る。

## 使い方

```
/start
```

## 手順

0. 事前チェック（必須）
   ```bash
   command -v gh
   gh auth status
   ```
   - `gh` が未導入、または未ログインの場合は処理を止める
   - `sudo` が必要なインストールや認証操作は、必ずユーザーに実行を依頼する
   - ユーザーの確認なしに API フォールバックや別経路で先に進めない

1. Open な Issue 一覧を取得する
   ```bash
   gh issue list --repo <owner>/<repo> --state open
   ```

2. ラベル・番号を確認して作業候補を提示する

3. ユーザーが取り掛かる Issue を選ぶ

4. 選ばれた Issue の詳細を確認する
   ```bash
   gh issue view <番号> --repo <owner>/<repo>
   ```

5. Issue の種別に応じたブランチを切る
   ```bash
   git checkout main
   git pull origin main
   git checkout -b <prefix>/<issue-slug>
   # 例: feature/db-schema, fix/login-retry
   ```

6. Issue に作業開始コメントを残す（任意）
   ```bash
   gh issue comment <番号> --body "作業開始します。ブランチ: <ブランチ名>"
   ```

## 運用ルール（完了時）

- 対象 Issue の PR をマージしたら、不要になった作業ブランチは削除する
- マージ作業後は `main` に戻る

## 実行エラー時の原則

- 権限不足・コマンド未導入・認証未完了で止まったら、まずユーザーに状況を共有して実行依頼する
- ユーザーが代替手段を明示的に希望した場合のみ、代替フローへ切り替える

## 実行後の改善確認（必須）

スキル実行の最後に、次を必ず人間へ確認する。

1. 今回の進め方の感想（良かった点）
2. 使いにくかった点・迷った点（使い勝手）
3. エージェントからの改善提案（手順 / コマンド / 出力）
4. このスキルを今すぐ更新するか（Yes / No）

### 遷移ルール

- Yes: `/update-skill start` を実行し、改善案を提示して承認後に反映する
- No: 更新見送り理由を 1 行で記録し、次回見直しの条件を確認する
- 関連 Issue がある場合: 確認結果（更新した / 見送った理由）を Issue コメントで共有する
