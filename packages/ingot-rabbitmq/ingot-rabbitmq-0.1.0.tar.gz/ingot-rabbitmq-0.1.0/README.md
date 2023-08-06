# Ingot Rabbitmq Ingot package.

Provides functionality for working with the RabbitMQ tool

## For consumers

For using the Ingot package just execute the following command:
```bash
pip install ingot_rabbitmq
```
Of course, need to activate a destination virtual environment before:
```bash
source .venv/bin/activate
```
... or to create one, if it hasn't prepared yet:
```bash
python3 -m venv .venv
```

### Bootstrap entrypoint

The Ingot package provides the Bootstrap CLI tool.
It allows to begin working with the Ingot package quickly.
It generates the following skeletons:
TODO. Add builders here after generating their by the `ingots package_bootstrap` tool.

For using the CLI tool just call the following command:
```bash
ingot-rabbitmq-cli <command> --name=<entity_name> --description="The <entity> brief description."
```
Getting help:
```bash
ingot-rabbitmq-cli --help
ingot-rabbitmq-cli <command> --help
```

## For developers

### Prepare the project for working

Clone a repository:
```bash
mkdir ingots-libs
cd ingots-libs
git clone https://github.com/ABKorotky/ingot-rabbitmq.git
cd ingot-rabbitmq
```

Prepare a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Prepare repository hooks
```bash
pip install pre_commit
pre-commit install
```

Configure code-quality tools:
```bash
pip install black flake8 mypy coverage
```

Configure the Sphinx tool

Please, use the following page for configuring the Sphinx documentation generator: [Sphinx](https://www.sphinx-doc.org/en/master/usage/installation.html)
```bash
pip install sphinx
sphinx-build -b html docs docs/build -v
```

### Using the tox tool

The Ingot package allows automation via the `tox` tool.
```bash
pip install tox
```

Use configured tox tool for several activities.

`tox -e reformat` - auto reformat code by the black tool, makes ordering import too.

`tox -e cs` - checks code style by PEP8.

`tox -e ann` - checks annotations of types by the mypy tool.

`tox -e utc` - runs unittests with the coverage tool.

`tox -e report` - builds coverage report for the project.

`tox -e doc` - builds a package documentation.

`tox -e build` - builds a package form current branch / tag / commit. Set the `INGOT_RABBITMQ_VERSION_SUFFIX` virtual variable for specify package suffix.

`tox -e upload` - uploads package to the PyPI index. Set the `PYPI_REPOSITORY_ALIAS` virtual variable for specify PyPI destination.

Calling tox without parameters will execute the following steps: **cs**, **ann**, **utc** and **report**.

### Using package bootstrap locally
Obviously, it's impossible to call the package bootstrap tool via package entry-point.

Use the following command instead:
```bash
python -m ingot_rabbitmq.scripts.ingot_rabbitmq ...
```
