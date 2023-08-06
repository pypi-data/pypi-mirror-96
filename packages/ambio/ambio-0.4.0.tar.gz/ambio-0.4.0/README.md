# Ambio

A light-weight bioinformatics library written in Python. It contains a variety of algorithms and functions that deal with strings.

## Installation

Run the following command in a terminal to install:

```bash
$ pip install ambio
```

## Usage

- The `distance` module contains functions that calculate the Edit and Hamming distance between strings, plus other related methods.

```python
from ambio import distance

# returns the hamming distance between two strings,
# if the two strings are not the same length, and Exception is raised
print(distance.hammingDistance("helloworld", "ciaomondo!"))

# returns the edit distance between the two strings
print(distance.editDistance("sunday", "saturday"))

# get the table with all the edit
# distances between the possible substrings
table = distance.generateEditDistanceTable("sunday", "saturday")

# you can also pass an option to get a table of the coordinates of
# the previous cell, this is useful for the backtracking process
table, paths = distance.generateEditDistanceTable("sunday", "saturday", paths=True)

# display the necessary edits to go from the first input string to the second. In this example,
# s1: "s--unday"
# s2: "saturday"
s1, s2 = distance.displayEdits("sunday", "saturday")

# by setting the 'compact' option to False, a list containing all the iterations
# that go from the first string to the second is returned instead
# in this case: ['sunday', 'saunday', 'satunday', 'saturday']
steps = distance.displayEdits("sunday", "saturday", compact=False)
```

## Development

To install `ambio`, along with the tools you need to develop and run tests, run the following command:

```bash
$ pip install -e .[dev]
```
