---
description: main を最新に同期し、現在のブランチをリベースする
metadata:
    github-path: skills/sync-main
    github-ref: refs/heads/main
    github-repo: https://github.com/MunehiroSoma/ai-dev-kit
    github-tree-sha: 523eee0b76f01fe1400af702354ee951a94a9590
name: sync-main
---
# skill: sync-main

main を最新に同期し、現在のブランチをリベースする。

## 使い方

```
/sync-main
```

## 手順

1. 現在のブランチを記録する
   ```bash
   git branch --show-current
   ```

2. main を最新に更新する
   ```bash
   git fetch origin
   git checkout main
   git pull origin main
   ```

3. 元のブランチに戻ってリベースする
   ```bash
   git checkout <元のブランチ>
   git rebase main
   ```

4. コンフリクトがあれば内容を確認してユーザーに報告する

## 注意

- リベース後は `git push --force-with-lease` が必要になる場合がある
- コンフリクトが複雑な場合はユーザーに確認してから進める

## 実行後の改善確認（必須）

スキル実行の最後に、次を必ず人間へ確認する。

1. 今回の進め方の感想（良かった点）
2. 使いにくかった点・迷った点（使い勝手）
3. エージェントからの改善提案（手順 / コマンド / 出力）
4. このスキルを今すぐ更新するか（Yes / No）

### 遷移ルール

- Yes: `/update-skill sync-main` を実行し、改善案を提示して承認後に反映する
- No: 更新見送り理由を 1 行で記録し、次回見直しの条件を確認する
