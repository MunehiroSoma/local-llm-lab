#!/usr/bin/env bash
# results/results.csv の「追記のみ」ルールを機械化するガード（guard_golden.sh と同型）。
# 既存行の削除・変更を検出し、末尾への追記だけを許可する。
#
# 比較対象は環境変数で切り替える:
#   GUARD_RESULTS_BASE_REF: 比較元のgit ref（既定: HEAD。CIでは origin/main を渡す）
#   GUARD_RESULTS_SOURCE:   index（既定・pre-commitのステージ内容） | worktree（CIの作業ツリー内容）
set -u
FILE="results/results.csv"
BASE_REF="${GUARD_RESULTS_BASE_REF:-HEAD}"
SOURCE="${GUARD_RESULTS_SOURCE:-index}"

if [ ! -f "$FILE" ]; then
  echo "✅ results guard: $FILE not present, skip"
  exit 0
fi

OLD=$(git show "${BASE_REF}:${FILE}" 2>/dev/null || true)
if [ -z "$OLD" ]; then
  echo "✅ results guard: no prior version at ${BASE_REF}, skip"
  exit 0
fi

if [ "$SOURCE" = "worktree" ]; then
  NEW=$(cat "$FILE")
else
  NEW=$(git show ":${FILE}" 2>/dev/null || cat "$FILE")
fi

OLD_LINE_COUNT=$(printf '%s\n' "$OLD" | wc -l | tr -d ' ')
NEW_HEAD=$(printf '%s\n' "$NEW" | head -n "$OLD_LINE_COUNT")

if [ "$NEW_HEAD" != "$OLD" ]; then
  echo "❌ results/results.csv の既存行が削除・変更されています（追記のみ許可・鉄則4）"
  echo "--- 差分（既存部分のみ） ---"
  diff <(printf '%s\n' "$OLD") <(printf '%s\n' "$NEW_HEAD") || true
  exit 1
fi

echo "✅ results guard OK（既存行は不変・追記のみ）"
exit 0
