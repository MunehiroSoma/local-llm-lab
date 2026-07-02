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

fit: ## 載る/載らない判定（MODEL=... ENV=...）  ※harness/fit で実装予定
	@echo "TODO: harness/fit — MODEL=$(MODEL) ENV=$(ENV)"

speed: ## tok/s計測（MODEL=... ENV=...）        ※harness/speed で実装予定
	@echo "TODO: harness/speed — MODEL=$(MODEL) ENV=$(ENV)"

capability: ## 標準ベンチ（足切り）             ※harness/capability で実装予定
	@echo "TODO: harness/capability"

task: ## 自前タスク評価（promptfoo/DeepEval）    ※harness/task で実装予定
	@echo "TODO: harness/task"

onboard: ## 新モデル一括: fit→speed→task→results追記（MODEL=...）
	@echo "TODO: harness/run_onboarding.py — MODEL=$(MODEL)"

validate: ## registry の YAML を検証
	@python3 -c "import yaml,sys; [yaml.safe_load(open(f)) for f in ['registry/models.yaml','registry/hardware.yaml']]; print('registry YAML OK')"

sync-skills: ## .agents/skills から .claude/skills へコピー同期
	python3 scripts/sync_agent_skills.py

check-skills: ## .agents/skills と .claude/skills のコピー同期を検証
	python3 scripts/sync_agent_skills.py --check
