# 観点: インフラ・コンテナ

> [`review`](../../../.claude/skills/review/SKILL.md) スキルの観点別サブエージェントが読む単位。
> 入力範囲: **差分のみ**。
> 想定モデル: 上位モデル。
> **起動条件: `envs/` の Docker/compose 実装を含む差分のときのみ起動する**（現時点で `envs/` は
> `.gitkeep` のみのため未起動。CI/CD総点検資料 §E の先回りチェックリストをそのまま観点化。Issue #46）。

| No | チェック項目 | 区分 | 重要度 | 備考 |
|---|---|:---:|:---:|---|
| 1 | `.env` や秘密を `COPY` でイメージに焼き込んでいない | 手動 | Must | 後の層で `rm` しても前の層に残る |
| 2 | ビルド時の秘密に `--mount=type=secret`（BuildKit）を使い、`ARG` に秘密を渡していない | 手動 | Must | `ARG` は `docker history` に残る |
| 3 | `.dockerignore` が `.gitignore` と同期しており、`.git`/`datasets/golden`/`.env` 等を除外している | 手動 | Must | |
| 4 | ベースイメージが digest でピン留めされている（`:latest` 等のタグ参照でない） | 手動 | Should | `nvidia/cuda@sha256:...` 形式 |
| 5 | `USER` で非root実行になっている | 手動 | Should | 推論サーバはネットワーク露出があるため特に |
| 6 | モデル重みが volume mount で、イメージに焼き込まれていない | 手動 | Should | イメージ肥大化・再ビルド頻発を防ぐ |
| 7 | ポート公開先のバインドが明示され、無認証のまま `0.0.0.0` でLAN公開していない | 手動 | Must | [`web-gui.md`](../web-gui.md) §バインド先と同根 |
| 8 | `healthcheck:` が定義されている | 手動 | Nits | Operations フェーズの回帰検知と接続 |
