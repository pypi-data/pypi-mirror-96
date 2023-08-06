# Hello World

This is an example project demostrating how to publish a Python module to PyPI.

## Installation

Run the following to install:

```python
pip install helloworld-praalinepy
```

## Usage

```python
from helloworld import say_hello

# Generate "Hello, World!"
say_hello()

# Generate "Hello, Everybody!"
say_hello("Everybody")
```

## Development

To install the development tools for testing, run the following in a virtualenv:

```bash
$ pip install -e .[dev]
```
