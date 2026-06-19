.PHONY: install run test

install:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

run:
	bash scripts/run_mac.sh

test:
	. .venv/bin/activate && python -m pytest
