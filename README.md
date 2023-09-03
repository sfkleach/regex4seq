# Welcome to RegEx4Seq

[![CircleCI](https://dl.circleci.com/status-badge/img/gh/sfkleach/lazychains/tree/main.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/gh/sfkleach/lazychains/tree/main) [![Documentation Status](https://readthedocs.org/projects/lazychains/badge/?version=latest)](https://lazychains.readthedocs.io/en/latest/?badge=latest)

This is a python library that implements regular-expression based pattern matches for sequences of arbitrary objects. For example you can write pattern to determine if a list is a sequence of alternating 1's and 0's like this:

```py
from regex4seq import Item, Items

# The core is a repetition of alternating 0s and 1s. But we need to
# account for the pattern starting on a 1 or finishing on a zero.
# Analogous to the regex /1?[01]*0?/.
pattern = Item(1).optional() & Items(0, 1).repeat() & Item(0).optional()

pattern.matches( [1, 0, 1, 0, 1, 0, 1])
# True

pattern.matches( [1, 0, 1, 0, 1, 0, 0])
# False

```

To learn more about the library, go to [the documentation](https://regex4seq.readthedocs.io) page on ReadTheDocs.
