################################################################################
### Standard Makefile intro
################################################################################

# Important check
MAKEFLAGS+=--warn-undefined-variables

# Causes the commands in a recipe to be issued in the same shell (beware cd commands not executed in a subshell!)
.ONESHELL:
SHELL:=/bin/bash

# When using ONESHELL, we want to exit on error (-e) and error if a command fails in a pipe (-o pipefail)
# When overriding .SHELLFLAGS one must always add a tailing `-c` as this is the default setting of Make.
.SHELLFLAGS:=-e -o pipefail -c

# Invoke the all target when no target is explicitly specified.
.DEFAULT_GOAL:=help

# Delete targets if their recipe exits with a non-zero exit code.
.DELETE_ON_ERROR:


################################################################################
### Main Contents
################################################################################

.PHONY: help
help:
	# Valid targets are:
	#	test 			- runs the unit tests
	#	docs			- builds Sphinx docs locally
	#	clean			- removes artefacts
	#	publish 		- publishes to the PyPi archive.
	#	publish-to-test - publishes to the Pypi Test archive.

# Changes to the way poetry is implemented appears to require an explicit
# look-up for the poetry command to run inside this makefile.
POETRY=$(shell command -v poetry)

.PHONY: docs
docs:
	$(POETRY) run make -C docs html

.PHONY: clean
clean:
	$(POETRY) run make -C docs clean

# Post-installation tests
.PHONY: test
test:
	$(POETRY) run mypy src/regex4seq/regex4seq.py --check-untyped-defs
	$(POETRY) run pytest tests

.PHONY: coverage
coverage:
	$(POETRY) run pytest --cov=src --cov-report=html:coverage

# ATM I do not intend for updates of the PyPI archive to be run automagically.
# So these commands should be run locally before trying to update the PyPI
# archives.
# 	poetry config --local repositories.pypi https://pypi.org/legacy/
# 	poetry config --local pypi-token.pypi <your-token>
# 	poetry config --local repositories.test-pypi https://test.pypi.org/legacy/
# 	poetry config --local pypi-token.test-pypi <your-token>

.PHONY: publish
publish:
	$(POETRY) publish --build

.PHONY: publish-to-test
publish-to-test:
	$(POETRY) publish -r test-pypi --build
