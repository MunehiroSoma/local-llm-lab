#!/usr/bin/env bash
# results/results.csv の「追記のみ」ルールを機械化するガード（guard_golden.sh と同型）。
# 既存行の削除・変更を検出し、末尾への追記だけを許可する。
#
# 比較対象は環境変数で切り替える:
#   GUARD_RESULTS_BASE_REF: 比較元のgit ref（既定: HEAD。CIでは push イベントの直前SHA等を渡す）
#   GUARD_RESULTS_SOURCE:   index（既定・pre-commitのステージ内容） | worktree（CIの作業ツリー内容）
set -u
FILE="results/results.csv"
BASE_REF="${GUARD_RESULTS_BASE_REF:-HEAD}"
SOURCE="${GUARD_RESULTS_SOURCE:-index}"

if [ ! -f "$FILE" ]; then
  echo "✅ results guard: $FILE not present, skip"
  exit 0
fi

# push イベントの `before`（ブランチ新規作成時は全ゼロSHA）は比較対象が存在しないため skip
case "$BASE_REF" in
  0000000000000000000000000000000000000000|"")
    echo "✅ results guard: BASE_REF is unset/zero (new branch), skip"
    exit 0
    ;;
esac

# BASE_REF 自体が解決できない場合はガード設定ミスとして明示的に失敗させる
# （「差分なし」と区別せず握りつぶすと、比較そのものが機能しないまま素通りしてしまう）
if ! git rev-parse --verify --quiet "${BASE_REF}^{commit}" >/dev/null; then
  echo "❌ results guard: BASE_REF '${BASE_REF}' を解決できません（fetch不足・typo等を確認してください）"
  exit 1
fi

TMP_OLD=$(mktemp)
TMP_NEW=$(mktemp)
trap 'rm -f "$TMP_OLD" "$TMP_NEW"' EXIT

if ! git cat-file -e "${BASE_REF}:${FILE}" 2>/dev/null; then
  echo "✅ results guard: ${BASE_REF} に $FILE は存在しない（新規ファイル）、skip"
  exit 0
fi
git show "${BASE_REF}:${FILE}" > "$TMP_OLD"

if [ "$SOURCE" = "worktree" ]; then
  cp "$FILE" "$TMP_NEW"
elif git cat-file -e ":${FILE}" 2>/dev/null; then
  git show ":${FILE}" > "$TMP_NEW"
else
  cp "$FILE" "$TMP_NEW"
fi

OLD_LINE_COUNT=$(wc -l < "$TMP_OLD" | tr -d ' ')
if ! head -n "$OLD_LINE_COUNT" "$TMP_NEW" | diff -q - "$TMP_OLD" >/dev/null; then
  echo "❌ results/results.csv の既存行が削除・変更されています（追記のみ許可・鉄則4）"
  echo "--- 差分（既存部分のみ） ---"
  diff <(head -n "$OLD_LINE_COUNT" "$TMP_NEW") "$TMP_OLD" || true
  exit 1
fi

echo "✅ results guard OK（既存行は不変・追記のみ）"
exit 0
