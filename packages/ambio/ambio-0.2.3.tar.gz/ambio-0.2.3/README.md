# Ambio

A light-weight bioinformatics library written in Python.

## Installation

Run the following command in a terminal to install:

```bash
$ pip install ambio
```

## Usage

You can import the `EditDistance` module to calculate the edit distance between two strings of your choice, and get the table used for this computation.

```python
from ambio.EditDistance import EditDistance

d = EditDistance("saturday", "sunday")

# get the edit distance between the two strings
print(d.getDistance())

# get the table with all the edit
# distances between the possible substrings
print(d.getTable())
```

## Development

To install `ambio`, along with the tools you need to develop and run tests, run the following command:

```bash
$ pip install -e .[dev]
```
