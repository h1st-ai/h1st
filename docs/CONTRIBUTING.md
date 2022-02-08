# Contributing guidelines

#### General guidelines and philosophy for contribution

* Include unit tests when you contribute new features, as they help to
  - prove that your code works correctly,
  - guard against future breaking changes
* Bug fixes also generally require unit tests, because the presence of bugs usually indicates insufficient test
  coverage.
* Keep API compatibility in mind when you change code in core GraphEngine.
* Tests should follow the basic principles:
  -  Only depend on what you use in your requirements.
  -  All code should have unit tests.
  -  Each class should have its own unit test file.
  -  Smaller tests are better.
  -  Always use seed if you're using any stochastic functions.
  -  Avoid using sleep in multi thread tests.
  -  Avoid using external resource in tests e.g: S3, requests to external services: download model from repos etc.


#### Ready to make a change ?
This project is built using Python 3.9 and [Poetry](https://python-poetry.org/docs/#installation).
Please ensure you have these installed before proceeding further.

1. Execute the following to ensure our pre-commit hooks are set up,
```shell
poetry install
poetry shell
pre-commit install
```
2. After making the desired changes, validate linting and tests,
```shell
poetry run pytest
poetry run pylint h1st/**/*.py **/*.py
```
Note: Changes to code should conform to
[Google Python Style Guide](https://github.com/google/styleguide/blob/gh-pages/pyguide.md)

3. This repository uses [Conventional Commits Specification](https://www.conventionalcommits.org/en/v1.0.0/).
After adding all the changes to git, using git add, ensure your commit message is in this format.
Alternatively, you can use the commandline tool to generate the commit msg,
```shell
poetry shell
cz commit
```

4. Create your PR and follow the discussion on GitHub.
