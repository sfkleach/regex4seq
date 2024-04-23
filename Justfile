# List available commands
help:
    just --list

docs:
	poetry run make -C docs html

clean:
	poetry run make -C docs clean

# Post-installation tests
test:
	poetry run mypy src/regex4seq/regex4seq.py --check-untyped-defs
	poetry run pytest tests

coverage:
	poetry run pytest --cov=src --cov-report=html:coverage

# ATM I do not intend for updates of the PyPI archive to be run automagically.
# So these commands should be run locally before trying to update the PyPI
# archives.
# 	poetry config --local repositories.pypi https://pypi.org/legacy/
# 	poetry config --local pypi-token.pypi <your-token>
# 	poetry config --local repositories.test-pypi https://test.pypi.org/legacy/
# 	poetry config --local pypi-token.test-pypi <your-token>

publish:
	poetry publish --build

publish-to-test:
	poetry publish -r test-pypi --build
