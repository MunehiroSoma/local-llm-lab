---
description: スキル/テンプレの改善を公開リポジトリへ反映し、新バージョンとして配布する
metadata:
    github-path: skills/release-kit
    github-ref: refs/heads/main
    github-repo: https://github.com/MunehiroSoma/ai-dev-kit
    github-tree-sha: c09fddf396dca37737fbce87517b1814676a6fc8
name: release-kit
---
# skill: release-kit

`ai-dev-kit` プラグイン（標準スキル・テンプレ集）の改善を、公開している GitHub リポジトリへ
反映してリリースする。これにより、各プロジェクト・各受講者の環境が
`/plugin update` で最新スキルを受け取れるようになる。

> このスキルは `update-skill`（個々のスキルを改善）の後工程。
> update-skill で磨いた内容を、ここで**配布物として公開**する。

## 使い方

```
/release-kit <変更概要>
例: /release-kit ship に worktree 退避手順を追記
```

## 前提

- このリポジトリが `<owner>/<repo>` として GitHub に公開（または共有）済みであること
- `gh auth status` が通っていること

## 手順

0. 事前チェック
   ```bash
   gh auth status
   git status --short        # 反映したい変更が揃っているか確認
   ```

1. マニフェストの妥当性を検証する
   ```bash
   claude plugin validate .
   ```
   - `marketplace.json` とスキル frontmatter のエラーがないことを確認する

2. バージョンを上げる（必須）
   - `plugins/ai-dev-kit/.claude-plugin/plugin.json` の `version` を SemVer で上げる
   - スキル追加 = minor、文言修正 = patch、互換性のない構成変更 = major
   - ※ `version` を据え置くと、既存ユーザーには更新が届かない

3. 変更履歴を残す
   - `CHANGELOG.md` に `## <version> (YYYY-MM-DD)` 節を追記する

4. コミットしてタグを打つ
   ```bash
   git add -A
   git commit -m "release: ai-dev-kit v<version> — <変更概要>"
   git tag v<version>
   ```

5. push する
   ```bash
   git push origin main
   git push origin v<version>
   ```

6. 受講者・利用者への周知（導入方式に応じて）
   - `gh skill` で入れている場合:
     ```
     gh skill update
     ```
   - Claude プラグインで入れている場合:
     ```
     /plugin marketplace update ai-dev-training
     /plugin update ai-dev-kit@ai-dev-training
     /reload-plugins
     ```

## 注意

- `version` は `plugin.json` 側だけで管理する（`marketplace.json` 側には書かない。両方に書くと plugin.json が優先され混乱する）
- 公開リポジトリへの push は外向きの不可逆操作。push 前に変更内容をユーザーへ提示して承認を得る
- 秘匿情報（`.env` / 鍵 / 社内固有値）が含まれていないか push 前に必ず確認する

## 実行後の改善確認（必須）

スキル実行の最後に、次を必ず人間へ確認する。

1. 今回の進め方の感想（良かった点）
2. 使いにくかった点・迷った点（使い勝手）
3. エージェントからの改善提案（手順 / コマンド / 出力）
4. このスキルを今すぐ更新するか（Yes / No）

### 遷移ルール

- Yes: `/update-skill release-kit` を実行し、改善案を提示して承認後に反映する
- No: 更新見送り理由を 1 行で記録し、次回見直しの条件を確認する
