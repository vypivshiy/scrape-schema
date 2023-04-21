DEFAULT: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

# Use poetry or activated venv
interpreter := $(shell hatch env show --ascii > /dev/null 2>&1 && echo "hatch run")

check: ## Run tests and linters
	@echo "flake8"
	@echo "------"
	@$(interpreter) flake8 .
	@echo ; echo "black"
	@echo "-----"
	@$(interpreter) black --check .
	@echo ; echo "isort"
	@echo "----"
	@$(interpreter) isort --check-only .
	@echo ; echo "mypy"
	@echo "----"
	@$(interpreter) mypy .
	@echo ; echo "pytest"
	@echo "------"
	@$(interpreter) pytest

fix:  ## Fix code with black and isort
	@echo "black"
	@echo "-----"
	@$(interpreter) black .
	@echo ; echo "isort"
	@echo "-----"
	@$(interpreter) isort .
