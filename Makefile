# local-llm-lab — よく使うコマンド集約
# 実装はPoCフェーズで harness/ に追加。ここはインターフェースの雛形。
.DEFAULT_GOAL := help

.PHONY: help env env-mac-check env-mac-ollama env-mac-smoke env-mac-llamacpp env-mac-vllm-metal whichllm fit speed capability task onboard validate sync-skills check-skills

help: ## このヘルプを表示
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

env: ## このマシンの環境確認（GPU/RAM/ランタイム）
	bash scripts/check_env.sh

env-mac-check: ## Mac M4 Pro のランタイム確認（Ollama/MLX-VLM）
	bash envs/mac/check.sh

env-mac-ollama: ## Mac の Ollama(OpenAI互換)を起動/確認（OLLAMA_MODEL=...）
	bash envs/mac/serve-ollama.sh

env-mac-smoke: ## Mac Ollama のOpenAI互換APIを疎通確認（MODEL=... BASE_URL=...）
	bash envs/mac/smoke-ollama.sh

env-mac-llamacpp: ## Mac の llama.cpp Metal build を導入/確認
	bash envs/mac/setup-llamacpp-metal.sh

env-mac-vllm-metal: ## Mac の vLLM Metal venv を導入/確認
	bash envs/mac/setup-vllm-metal.sh

whichllm: ## WhichLLMで候補モデルを機械抽出（PROFILE=coding 等）
	bash scripts/whichllm_scan.sh $(PROFILE)

fit: ## 載る/載らない判定（MODEL=... ENV=... BASE_URL=...）
	python3 -m harness.fit.openai --model "$(MODEL)" --env "$(ENV)" --base-url "$(BASE_URL)" --append-results

speed: ## tok/s計測（MODEL=... ENV=... BASE_URL=...）
	python3 -m harness.speed.openai --model "$(MODEL)" --env "$(ENV)" --base-url "$(BASE_URL)" --append-results

capability: ## 標準ベンチ（MODEL=... ENV=... BENCH=... SCORE=...）
	python3 -m harness.capability.run --model "$(MODEL)" --env "$(ENV)" --bench "$(BENCH)" --score "$(SCORE)" --append-results

task: ## 自前タスク評価ヘルパー（OUTPUT='{"summary":"...","tags":["..."]}'）
	python3 -m harness.task.promptfoo.evaluate_json --output '$(OUTPUT)'

onboard: ## 新モデル一括: fit→speed→capability/task→row作成（MODEL=... ENV=... BASE_URL=...）
	python3 -m harness.run_onboarding --model "$(MODEL)" --env "$(ENV)" --base-url "$(BASE_URL)" $(ONBOARD_ARGS)

validate: ## registry の YAML を検証
	@python3 -c "import yaml,sys; [yaml.safe_load(open(f)) for f in ['registry/models.yaml','registry/hardware.yaml']]; print('registry YAML OK')"

sync-skills: ## .agents/skills から .claude/skills へコピー同期
	python3 scripts/sync_agent_skills.py

check-skills: ## .agents/skills と .claude/skills のコピー同期を検証
	python3 scripts/sync_agent_skills.py --check
