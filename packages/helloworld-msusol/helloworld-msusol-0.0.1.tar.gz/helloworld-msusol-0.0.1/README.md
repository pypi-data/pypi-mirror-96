# Hello World

Just working through the "Hello World" example on how to publish a python module to PyPI from
[Publishing (Perfect) Python Packages on PyPi](https://www.youtube.com/watch?v=GIF3LaRqgXo)

Source Code: https://github.com/judy2k/publishing_python_packages_talk

## Installation

Run the following to install:

```python
pip install helloworld
```

## Usage

```python
from helloworld import say_hello

# Generate "Hello, World!"
say_hello()

# Generate "Hello, Everybody!"
say_hello("Everybody")
```

## Build the pip package

```bash
pipenv install -e .
pipenv install --dev 'pytest>=3.7'
pipenv shell
# (helloworld)
pytest
```

## Source Distribution

```bash
# (helloworld)
python setup.py sdist
..writes dist/helloworld-0.0.1.tar.gz

tar tzf dist/helloworld-0.0.1.tar.gz
helloworld-0.0.1/
helloworld-0.0.1/LICENSE
helloworld-0.0.1/MANIFEST.in
helloworld-0.0.1/PKG-INFO
helloworld-0.0.1/Pipfile
helloworld-0.0.1/Pipfile.lock
helloworld-0.0.1/README.md
helloworld-0.0.1/pyproject.toml
helloworld-0.0.1/setup.cfg
helloworld-0.0.1/setup.py
helloworld-0.0.1/src/
helloworld-0.0.1/src/helloworld.py
helloworld-0.0.1/src/helloworld.egg-info/
helloworld-0.0.1/src/helloworld.egg-info/PKG-INFO
helloworld-0.0.1/src/helloworld.egg-info/SOURCES.txt
helloworld-0.0.1/src/helloworld.egg-info/dependency_links.txt
helloworld-0.0.1/src/helloworld.egg-info/requires.txt
helloworld-0.0.1/src/helloworld.egg-info/top_level.txt
helloworld-0.0.1/test_helloworld.py
helloworld-0.0.1/tox.ini
```

## Publish to pypi

```bash
(helloworld)$ python -m pip --version
(helloworld)$ python -m pip install --upgrade pip setuptools wheel
(helloworld)$ python -m pip install --upgrade helloworld 

```

