# Ambio

A light-weight bioinformatics library written in Python. It contains a variety of algorithms and functions that deal with strings.

## Installation

Run the following command in a terminal to install:

```bash
$ pip install ambio
```

## Usage

- The `algs` module contains functions that calculate the Hamming distance between strings, and the Needleman–Wunsch algorithm for alignment, plus other related methods.

```python
from ambio import algs

# returns the hamming distance between two strings,
# if the two strings are not the same length, and Exception is raised.
hamming_distance = algs.hammingDistance("helloworld", "ciaomondo!"))

# returns the alignment score of two strings, using the Needleman–Wunsch algorithm.
score = algs.alignmentScore("sunday", "saturday"))

# it's possible to tweak the weights of the algorithm:
score = algs.alignmentScore(
    "sunday",
    "saturday",
    insertionDeletionWeight=-2,
    substitutionWeight=-1,
    matchWeight=1
)

# get the table with the scores between all the possible substrings.
# it is always possible to tweak the weights.
table = algs.alignmentScoreTable("sunday", "saturday")

# you can also pass an option to get a table of the coordinates of
# the previous cell, this is useful for the backtracking process
table, paths = algs.alignmentScoreTable("sunday", "saturday", paths=True)

# display the necessary edits to go from the first input string to the second.
# again, it's possible to set the weights. In this example,
# s1: "s--unday"
# s2: "saturday"
s1, s2 = distance.showAlignment("sunday", "saturday")
```

## Development

To install `ambio`, along with the tools you need to develop and run tests, run the following command:

```bash
$ pip install -e .
```
