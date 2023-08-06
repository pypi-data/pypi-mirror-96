# docstring-to-markdown

[![tests](https://github.com/krassowski/docstring-to-markdown/workflows/tests/badge.svg)](https://github.com/krassowski/docstring-to-markdown/actions?query=workflow%3A%22tests%22)
![CodeQL](https://github.com/krassowski/docstring-to-markdown/workflows/CodeQL/badge.svg)
[![pypi-version](https://img.shields.io/pypi/v/docstring-to-markdown.svg)](https://python.org/pypi/docstring-to-markdown)

On the fly conversion of Python docstrings to markdown

- Python 3.6+
- currently can recognise reStructuredText and convert multiple of its features to Markdown
- in the future will be able to convert Google docstrings too

### Installation

```bash
pip install docstring-to-markdown
```


### Example

Convert reStructuredText:

```python
>>> import docstring_to_markdown
>>> docstring_to_markdown.convert(':math:`\\sum`')
'$\\sum$'
```

When given the format cannot be recognised an exception will be raised:

```python
>>> docstring_to_markdown.convert('\\sum')
Traceback (most recent call last):
    raise UnknownFormatError()
docstring_to_markdown.UnknownFormatError
```

### Development

```bash
pip install -e .
pytest
```
