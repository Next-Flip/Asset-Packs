VERSION := 0.0.0

# If the first argument is "repack"...
ifeq (repack,$(firstword $(MAKECMDGOALS)))
  # use the rest as arguments for "repack"
  REPACK_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  # ...and turn them into do-nothing targets
  $(eval $(REPACK_ARGS):;@:)
endif

.PHONY: repack
repack: venv requirements
	./.venv/bin/python3 .utils/repack.py $(REPACK_ARGS)

# If the first argument is "check"...
ifeq (check,$(firstword $(MAKECMDGOALS)))
  # use the rest as arguments for "check"
  CHECK_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  # ...and turn them into do-nothing targets
  $(eval $(CHECK_ARGS):;@:)
endif

.PHONY: check
check: venv requirements
	./.venv/bin/python3 .utils/check.py $(CHECK_ARGS)

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
