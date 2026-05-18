# Load the .env file if it exists, so that environment variables are available to the justfile.
# Only relevant when releasing from a local machine - which is not required any more.
set dotenv-load

# Lists available commands
@default:
    just --list

# Builds the documentation
docs:
	uv run make -C docs html

# Cleans the docs directory and dist/
clean:
	uv run make -C docs clean
	rm -rf dist

# ATM I do not intend for updates of the PyPI archive to be run automagically.
# So these commands should be run locally before trying to update the PyPI
# archives.
# 	export UV_PUBLISH_TOKEN=<your-pypi-token>
# 	export UV_PUBLISH_TOKEN=<your-test-pypi-token>  (for test-pypi)

# Publishes the package to PyPI
publish:
	uv build && uv publish

# Publishes the package to the test PyPI
publish-to-test:
	uv build && uv publish --publish-url https://test.pypi.org/legacy/


# Checks the project is ready to release
pre-release: test
	bash scripts/pre-release-check.sh

# Post-installation tests
test: type_check unit_test

# Type checks the code
type_check:
	uv run mypy --check-untyped-defs src/regex4seq/regex4seq.py
	MYPYPATH=src uv run mypy --check-untyped-defs tests/test_regex4seq.py

# ut = unit tests
#	If this fails because it cannot find the regex4seq package, check
#	that you have done a local uv sync.
# Runs unit tests
unit_test:
	uv run pytest tests

# Runs unit tests with coverage report
coverage:
	uv run pytest --cov=src --cov-report=html:coverage
