setup:
	git submodule update --init
	pip install -r requirements.txt

apkg: setup ## Generate APKG file
	PYTHONPATH=$(PWD)/anki: python create_apkg.py $(filter-out $@,$(MAKECMDGOALS))

%:
	@true

.PHONY: help

help:
	@echo 'Usage: make <command>'
	@echo
	@echo 'where <command> is one of the following:'
	@echo
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help

