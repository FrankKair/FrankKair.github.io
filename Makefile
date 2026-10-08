PYTHON ?= python3
HUGO ?= hugo

.PHONY: all generate serve build test check
all: build

generate:
	$(PYTHON) generate-markdowns.py

serve: generate
	$(HUGO) server --buildDrafts

build: generate
	$(HUGO) --gc --minify --cleanDestinationDir

test:
	$(PYTHON) -m unittest discover -s tests -v

check: test build
	$(PYTHON) scripts/verify-site.py
