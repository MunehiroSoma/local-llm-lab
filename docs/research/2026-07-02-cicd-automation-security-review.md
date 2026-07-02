# CI/CD・自動化・セキュリティ総点検（2026-07-02）

リポジトリ全体（設定ファイル・GitHub設定・スクリプト・規約文書）を対象に、
CI/CD導入候補・自動化の見落とし・セキュリティ対策を棚卸しした指摘資料。
重要度は review-checklist と同じ Must / Should / Nits を使う。

## 調査範囲と現状の良い点

対象: `.github/`（workflows, CODEOWNERS, templates）、`.pre-commit-config.yaml`、`pyproject.toml`、
`Makefile`、`scripts/*.sh`、`registry/*.yaml`、GitHub リポジトリ設定（API経由で確認）、各種規約文書。

先に良い点（維持すべきもの）:

- **Secret scanning + push protection が有効**（公開リポとして最重要の防御が入っている）
- golden data の三重防御（`.gitignore` + pre-commit + CI guard）が設計通り機能している
- `validate.yml` の `permissions: contents: read` 明示、セルフホストランナーのリスクが ADR 0004 / SECURITY.md に文書化済み
- pre-commit に ruff / mypy strict / detect-private-key / 大容量ファイル検知が揃っている
- results.csv 追記のみ・judge固定・ゴールデンセット版固定という再現性ルールが明文化されている

---

## A. GitHubリポジトリ設定（コード外の設定漏れ）

| # | 重要度 | 指摘 | 対応 |
|---|:---:|---|---|
| A-1 | **Must** | **`main` にブランチ保護/ルールセットが無い**。鉄則3「mainへ直push しない」がエージェントの自制のみで、システム的に強制されていない。`--no-verify` + 直pushで全ゲートを素通りできる | Settings→Rules: PR必須・force push禁止・required status check（guard）・削除禁止。公開リポは無料 |
| A-2 | **Must** | **Dependabot alerts / security updates が無効**（API確認: `dependabot_security_updates: disabled`, vulnerability alerts: disabled） | Settings→Security で有効化 + `.github/dependabot.yml` 追加（github-actions / pip） |
| A-3 | Should | **マージ方法が3種とも許可**されている。規約は squash merge のみのはずが、merge commit / rebase も選べる | squash のみ許可に設定変更 |
| A-4 | Should | **`delete_branch_on_merge: false`**。start スキルの運用ルール「マージ後にブランチ削除」が手作業のまま | 自動削除を有効化（スキルの手順も1つ減る） |
| A-5 | Should | **CODEOWNERS が全行コメントアウトのプレースホルダ**（Issue #33 で追跡済みだが未対応） | `* @MunehiroSoma` を有効化。ブランチ保護と組み合わせて初めて効く点に注意 |
| A-6 | Nits | **Private vulnerability reporting が無効**（`enabled: false`）。SECURITY.md は「機密性が高い場合は非公開手段で」と書いているが、その非公開手段が用意されていない | Settings→Security で有効化 |

## B. CI/CD・GitHub Actions

| # | 重要度 | 指摘 | 対応 |
|---|:---:|---|---|
| B-1 | Should | **`actions/checkout@v4` がタグ参照**。タグは書き換え可能なため、サプライチェーン攻撃（tag hijack）に弱い | コミットSHAでピン留め（`actions/checkout@<sha> # v4.x.x`）。Dependabot が SHA も更新してくれる |
| B-2 | Should | **pre-commit の `--no-verify` 回避に対するサーバ側の網が golden guard のみ**。ruff/mypy/yaml検証はローカル専用のため、バイパスされたコードが main に入り得る。ADR 0004 は意図的な決定だが、公開リポは GitHub-hosted 無料なので `pre-commit run --all-files` をCIに足してもコストゼロ | ADR 0004 の改訂候補として検討（「コスト理由」が公開リポでは成立しないため） |
| B-3 | Should | **results.csv の「追記のみ」ルールが機械化されていない**。鉄則4は現状エージェントの自制のみ | CI/pre-commit に「`git diff` で既存行の削除・変更が無いこと」を検査するガードを追加（guard_golden.sh と同型） |
| B-4 | Should | **registry YAML の検証が `yaml.safe_load` のみ**（構文チェックだけ）。スキーマ違反（必須キー欠落、`target_envs` に存在しないマシンID、`profiles` の宣言外タグ等）を検出できない | JSON Schema を書いて `check-jsonschema` pre-commit フックで検証。「オンボード済みモデルは `revision: null` 禁止」もここで強制できる |
| B-5 | Nits | workflow に `timeout-minutes` / `concurrency` が無い（デフォルト6時間。暴走時に無駄に回り続ける） | `timeout-minutes: 5`、`concurrency: {group: ..., cancel-in-progress: true}` を追加 |
| B-6 | Nits | **actionlint / zizmor が未導入**。workflow の構文ミス・セキュリティ設定ミスを検出する仕組みが無い | pre-commit に actionlint（+必要なら zizmor）を追加 |
| B-7 | Nits | `scripts/*.sh` に **shellcheck が掛かっていない** | pre-commit に shellcheck フックを追加 |

## C. サプライチェーン・依存管理・再現性

| # | 重要度 | 指摘 | 対応 |
|---|:---:|---|---|
| C-1 | **Must** | **`uv.lock` がコミットされていない**。pyproject.toml は `[tool.uv]` で「uv でロック」と書いているが、ロックファイル不在のため環境再現ができない。「judge・ゴールデンセット固定」の再現性方針と矛盾 | `uv lock` を実行して uv.lock をコミット。CI/セットアップは `uv sync --frozen` に |
| C-2 | Should | **ツール実行が `@latest` 固定**（`npx promptfoo@latest` / `uvx whichllm@latest`）。eval ツールのバージョンが変わると過去スコアと比較できなくなる。judge 固定と同じ理由でツールも固定が必要 | バージョン明示（例: `npx promptfoo@0.x.y`）。registry/results に eval ツール版の列を足すのも検討 |
| C-3 | Should | **pre-commit フックの rev が手動管理**で更新の仕組みが無い（ruff v0.9.6 は既に古い）。放置すると規約と実際のルール差が開く | 公開リポ無料の pre-commit.ci を有効化するか、定期的に `pre-commit autoupdate` する運用を決める |
| C-4 | Nits | pyproject の `promptfoo; platform_system!='no'` は**常に真の環境マーカー**（ハック）。PyPI の promptfoo は公式ラッパーであることは確認済みだが、この書き方は意図が読めない | マーカーを外すか、npm 側で管理するなら Python 依存から削除してコメントに寄せる |
| C-5 | Nits | **依存追加時のレビュー観点が無い**（typosquatting・メンテ状況・ライセンス確認）。今回 promptfoo の PyPI 実在確認を手動でやったのがまさにこの観点 | review-checklist への観点追加（後述 §F） |

## D. シークレット・データ保護

| # | 重要度 | 指摘 | 対応 |
|---|:---:|---|---|
| D-1 | Should | **ローカルの秘密検知が `detect-private-key` のみ**。秘密鍵形式しか検出せず、APIキー・トークン類（`sk-...`、`ghp_...`等）はローカルでは素通り。サーバ側 push protection が最後の網だが、履歴に載る前にローカルで止めるのが理想 | pre-commit に gitleaks を追加（コンテンツベース検知） |
| D-2 | Should | **guard_golden.sh はパスベース防御のみ**。`datasets/golden/` 以外の場所（docs/ や results/raw/ 等）に実データを置いてしまうケースは検出できない | 完全解決は難しいが、gitleaks の custom rule や「results/raw は無視済み」等の既存防御を SECURITY.md に整理して限界を明記する |
| D-3 | Nits | `.env.example`（キー名だけのテンプレート）が無い。実装フェーズで .env を使い始めたとき、必要な変数が口伝になる | ハーネス実装時に `.env.example` を追加する運用をメモしておく |

## E. 将来の envs/（Docker/compose）向け先回りチェックリスト

現時点で `envs/` は .gitkeep のみだが、実装時に踏みやすい罠を先に列挙する
（「env を COPY すると焼き込まれる」問題を含む）。

| # | 罠 | ルール |
|---|---|---|
| E-1 | **`COPY .env` / `COPY . .` で秘密がイメージ層に焼き込まれる**。後の層で `rm` しても前の層に残り、`docker history` / layer 抽出で読める | .env は絶対に COPY しない。実行時に `--env-file` / compose の `env_file:` で渡す |
| E-2 | **`ARG` で渡した秘密も `docker history` に残る** | ビルド時秘密は `--mount=type=secret`（BuildKit）を使う。ARG は非秘密のみ |
| E-3 | `.dockerignore` が無いと `.git` / `datasets/golden` / `.env` までビルドコンテキストに入る | Dockerfile を書く前に `.dockerignore` を先に書く（.gitignore と同期） |
| E-4 | ベースイメージのタグ参照（`:latest` や `:12.4`）は再現性がない | digest でピン留め（`nvidia/cuda@sha256:...`）。registry の revision 固定と同じ思想 |
| E-5 | root 実行のまま運用 | `USER` で非root化。inference server はネットワーク露出があるため特に |
| E-6 | モデル重みをイメージに焼き込むとイメージが数十GBになり、モデル更新のたびに再ビルド | 重みは volume mount。イメージはランタイムのみ |
| E-7 | compose でポートを `0.0.0.0` に公開すると LAN に推論サーバが露出（認証なしの OpenAI 互換サーバは誰でも叩ける） | `127.0.0.1:8000:8000` のようにバインド先を明示。LAN 公開するなら API キー必須化 |
| E-8 | ヘルスチェックが無いと落ちた推論サーバに気づけない | `healthcheck:` を最初から書く（Operations フェーズの回帰検知とも接続） |

## F. review-checklist に漏れている観点（追加候補一覧）

現在の6観点（基本品質/エラー処理/セキュリティ/テスト/設計整合性/harness-eval-registry）に対し、
今回の総点検で「どの観点にも属さない」ことが判明した領域。
旧チェックリスト（観点分割前）から**分割時に脱落した項目**も含む。

| 候補観点 | 内容 | 備考 |
|---|---|---|
| **CI/CD・サプライチェーン** | Actions の SHA ピン留め、workflow の permissions 最小化、依存追加時の実在・メンテ状況・ライセンス確認、lockfile 更新の妥当性 | 今回の指摘 B-1, C-1, C-5 が該当。現状どの観点も見ない |
| **インフラ・コンテナ** | §E の全項目（秘密の焼き込み、digest固定、非root、ポート公開範囲） | envs/ 実装開始と同時に必要になる |
| **データ操作・リソース管理** | トランザクション、N+1、接続/ファイルの確実な解放、並行処理の競合 | **旧 review スキルの「3. データ操作」が観点分割時に脱落**。ハーネス実装（結果CSV書き込み・並列計測）で必要 |
| **外部API連携** | リトライ、レート制限、エラーレスポンス処理 | **旧「4. 外部API連携」も同様に脱落**（timeout のみセキュリティ観点 S113 に残存）。OpenAI互換クライアント（Issue #7）実装前に復活が必要 |
| **構成管理・シークレット** | .env の扱い、設定値のバリデーション、`.env.example` の同期 | D-1, D-3 が該当 |
| **再現性** | ツール/モデル/データセットのバージョン固定が破られていないか | harness-eval-registry 観点に一部あるが、「ツール版固定」（C-2）は対象外のまま |
| **ドキュメント整合性** | スキル一覧・コマンド表と実体の同期（AGENT.md の古いハット一覧を今日発見・修正したのがこの類型） | 設計整合性観点は「設計書⇔コード」のみで「文書⇔文書」を見ない |
| **後方互換性・スキーマ進化** | results.csv の列変更、registry の schema_version 運用（bump 基準が未定義） | schema_version: 1 は宣言のみで運用ルールが無い |

## 推奨アクションの優先順位

1. **即日（設定変更のみ・コード不要）**: A-1 ブランチ保護 / A-2 Dependabot有効化 / A-3 squashのみ / A-4 自動ブランチ削除 / A-6 private vulnerability reporting
2. **小PR 1本**: C-1 uv.lock コミット / A-5 CODEOWNERS（Issue #33） / B-5 timeout+concurrency / B-1 SHAピン留め
3. **小PR 2本目**: B-3 results.csv 追記ガード / B-4 registry JSON Schema 検証 / D-1 gitleaks / B-6 actionlint / B-7 shellcheck
4. **Issue化して計画的に**: B-2 CI強化（ADR 0004 改訂） / C-2 ツール版固定 / §F の観点追加（review-checklist 更新、ADR 0006 の派生）
5. **envs/ 実装開始時**: §E をチェックリストとして参照（レビュー観点「インフラ・コンテナ」の新設と同時）
