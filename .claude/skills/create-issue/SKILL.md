---
description: GitHub Issue を正しい粒度・構造で登録する
metadata:
    github-path: skills/create-issue
    github-ref: refs/heads/main
    github-repo: https://github.com/MunehiroSoma/ai-dev-kit
    github-tree-sha: 8f2916cf3dbbb45f3b08f880a8c62e4f403b1739
name: create-issue
---
# skill: create-issue

GitHub Issue を正しい粒度・構造で登録する。

## 使い方

```
/create-issue
```

## Issue の種別と使い分け

| 種別 | いつ使うか | Label（例） |
|---|---|---|
| **Task Issue** | 実装タスク単位（1〜3 日で完了する粒度） | フェーズ/種別ラベル |
| **Bug Issue** | コード上の不具合を発見したとき | `bug` + `priority:S/A/B` |
| **Epic Issue** | 複数 Task をまとめる親 Issue | `epic` |

## 登録前レビュー（必須）

`gh issue create` を実行する前に、必ず人間へ次を提示してレビューを受ける。

1. 作成予定タイトル
2. 付与予定ラベル
3. Issue 本文ドラフト（チェックリスト・完了条件を含む）

- 人間の `OK` が出るまで Issue を作成しない
- 修正依頼があれば反映後に再提示し、承認後に作成する

---

## Task Issue テンプレート

```
タイトル: [<番号>] <タスク名>

## 親 Issue
#<番号> <親タスク名>

## タスク
- [ ] タスク1
- [ ] タスク2

## 完了条件
<具体的な動作確認方法>
```

## Bug Issue テンプレート

```
タイトル: [Bug] <問題の概要>

## 概要
<何が問題か・影響範囲>

## 問題箇所
`<ファイルパス>` L<行番号>

## 再現手順
1. ...

## 期待する動作
...

## 関連
- #XX
```

## gh コマンド例

```bash
gh issue create --repo <owner>/<repo> \
  --title "[<番号>] <タイトル>" \
  --body "..." \
  --label "<label>"
```

## 推奨フロー

1. 既存 Issue を確認して重複を回避する
2. 作成する Issue の粒度を決める（必要なら複数に分割）
3. 作成予定のタイトル・ラベル・本文ドラフトを人間へ提示する
4. 人間のレビュー反映後、`gh issue create` を実行する
5. 作成結果 URL を共有する

## 実行後の改善確認（必須）

スキル実行の最後に、次を必ず人間へ確認する。

1. 今回の進め方の感想（良かった点）
2. 使いにくかった点・迷った点（使い勝手）
3. エージェントからの改善提案（手順 / コマンド / 出力）
4. このスキルを今すぐ更新するか（Yes / No）

### 遷移ルール

- Yes: `/update-skill create-issue` を実行し、改善案を提示して承認後に反映する
- No: 更新見送り理由を 1 行で記録し、次回見直しの条件を確認する
