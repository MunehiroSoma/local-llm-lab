#!/usr/bin/env bash
# 公開リポジトリ保護: datasets/golden/ に実評価データ（自前の仕様書等）が
# 混入していないか検査。samples/ と .gitignore のみ許可。
# pre-commit（ステージ済）と CI（追跡済）の両方で機能するよう和集合を見る。
set -u
FILES=$( { git diff --cached --name-only 2>/dev/null; git ls-files 'datasets/golden' 2>/dev/null; } | sort -u )
BAD=$(printf '%s\n' "$FILES" | grep -E '^datasets/golden/' | grep -vE '^datasets/golden/(\.gitignore$|samples/)' || true)
if [ -n "$BAD" ]; then
  echo "❌ 公開してはいけない golden データが含まれています:"
  printf '   %s\n' $BAD
  echo "→ datasets/golden/ は samples/ のみ公開。実データは別保管にしてください。"
  exit 1
fi
echo "✅ golden data guard OK"
exit 0
