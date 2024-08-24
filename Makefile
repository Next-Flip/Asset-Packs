VERSION := 0.0.0

.PHONY: repack
repack: venv requirements
	./.venv/bin/python3 .utils/repack.py

venv:
	python3 -m venv .venv

.PHONY: requirements
requirements: venv
	./.venv/bin/pip install -q -r requirements.txt

.PHONY: clean
clean:
	rm -rf .venv

.PHONY: lint
lint: venv requirements
	./.venv/bin/black .utils --check

.PHONY: format
format: venv requirements
	./.venv/bin/black .utils
