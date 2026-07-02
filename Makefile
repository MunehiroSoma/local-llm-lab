# local-llm-lab — よく使うコマンド集約
# 実装はPoCフェーズで harness/ に追加。ここはインターフェースの雛形。
.DEFAULT_GOAL := help

.PHONY: help env whichllm fit speed capability task onboard validate sync-skills check-skills

help: ## このヘルプを表示
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

env: ## このマシンの環境確認（GPU/RAM/ランタイム）
	bash scripts/check_env.sh

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

onboard: ## 新モデル一括: fit→speed→results追記（MODEL=... ENV=... BASE_URL=...）
	python3 -m harness.run_onboarding --model "$(MODEL)" --env "$(ENV)" --base-url "$(BASE_URL)" --append-results

validate: ## registry の YAML を検証
	@python3 -c "import yaml,sys; [yaml.safe_load(open(f)) for f in ['registry/models.yaml','registry/hardware.yaml']]; print('registry YAML OK')"

sync-skills: ## .agents/skills から .claude/skills へコピー同期
	python3 scripts/sync_agent_skills.py

check-skills: ## .agents/skills と .claude/skills のコピー同期を検証
	python3 scripts/sync_agent_skills.py --check
