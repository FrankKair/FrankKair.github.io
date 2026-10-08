PYTHON ?= python3
HUGO ?= hugo

.DEFAULT_GOAL := help
.PHONY: all generate serve build test check help
all: build

generate: ## Regenerate collections from CSV
	$(PYTHON) scripts/generate-markdowns.py

serve: generate ## Preview drafts at http://localhost:1313
	$(HUGO) server --buildDrafts

build: generate ## Build into public/ and remove stale output
	$(HUGO) --gc --minify --cleanDestinationDir

test: ## Run generator tests
	$(PYTHON) -m unittest discover -s tests -v

check: test build ## Test, build, and verify data, links and RSS
	$(PYTHON) scripts/verify-site.py

help: ## Show commands
	@awk -F ':.*## ' \
		'/^[[:alnum:]_-]+:.*## / { printf "  %-12s %s\n", $$1, $$2 }' \
		$(MAKEFILE_LIST)
