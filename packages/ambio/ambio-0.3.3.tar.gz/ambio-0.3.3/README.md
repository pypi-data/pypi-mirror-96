# Ambio

A light-weight bioinformatics library written in Python.

## Installation

Run the following command in a terminal to install:

```bash
$ pip install ambio
```

## Usage

You can import the `distance` module to calculate the edit distance between two strings of your choice, and get the table used for this computation.

```python
from ambio.distance import editDistance, generateEditDistanceTable

# get the edit distance between the two strings
print(editDistance("sunday", "saturday"))

# get the table with all the edit
# distances between the possible substrings
print(generateEditDistanceTable("sunday", "saturday"))
```

## Development

To install `ambio`, along with the tools you need to develop and run tests, run the following command:

```bash
$ pip install -e .[dev]
```
