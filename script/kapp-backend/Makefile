.PHONY: help dev

help: ## ヘルプを表示
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

run_server: ## 開発サーバーを起動してSwagger (http://localhost:8000/docs) を開ける状態にする
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000