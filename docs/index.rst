.. RegEx4Seq documentation master file, created by
   sphinx-quickstart on Sat Aug 26 10:45:21 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to RegEx4Seq's documentation!
=====================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   regex4seq

.. image:: https://dl.circleci.com/status-badge/img/gh/sfkleach/regex4seq/tree/main.svg?style=svg
        :target: https://dl.circleci.com/status-badge/redirect/gh/sfkleach/regex4seq/tree/main

.. image:: https://readthedocs.org/projects/regex4seq/badge/?version=latest
    :target: https://regex4seq.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

Introduction
============

[WARNING: This is a work in progress as of 3rd Sept 23. I'm still working on the
documentation and unit tests but the API is essentially stable. I have set the
version to 0.3.0 and I have changed the project status to 'Alpha' to reflect 
this.]

RegEx4Seq is a pattern matcher that is inspired by regular expressions. It 
allows you to write patterns that find matches in any sequence of python 
values, such as lists, tuples or even strings. For example, we could detect
whether or not a list is a sequence of strings that contain the letter 'a'.

.. code-block:: python

   # Import the module.
   from regex4seq import *

   # IfItem returns a pattern that only matches a value if the given
   # function returns True for that value. The method repeat simply 
   # iterates that pattern over the sequence.
   pattern = IfItem(lambda s: 'a' in s).repeat()

   # By default '.matches' returns True if the pattern matches the entire
   # sequence of elements. So this will return False because 'dog' does not
   # contain 'a'.
   pattern.matches(['cat', 'dog', 'bat'])
   # False

   # This will return True because the pattern matches the whole sequence.
   pattern.matches(['cat', 'bat', 'ant'])
   # True

Or perhaps match a list of alternating positive and negative numbers. To do 
this we would use the '&' operator to compose two patterns in sequence.

.. code-block:: python

   from regex4seq import IfItem

   # We can use either '&' or '.then' to concatenate two patterns.
   pattern = (IfItem(lambda x: x > 0) & IfItem(lambda x: x < 0)).repeat()

   pattern.matches([1, -1, 2, -2, 3, -3])
   # True
   pattern.matches([1, -1, 2, 3, -3])
   # False

Basic Patterns
==============

Hopefully you have got the rough idea. So now we can now look at the basic 
patterns that can be used to build up more complex patterns. Each of these
correspond to a basic pattern in normal regular expressions:

* :code:`NONE` - matches nothing. This is like the empty pattern ''.
* :code:`ANY` - matches any single item. This correspond to the regex '.'.
* :code:`MANY` - matches zero or more items, like '.*'
* :code:`Item(x)` - matches an item equal to :code:`x`. This is like an ordinary character e.g. 'x'
* :code:`OneOf(x, y, ...)` - matches any of the listed items. This is like a character class e.g. '[xyz]'

Composing patterns
==================

* :code:`p1 & p2` - matches p1 followed by p2. This is like concatenating two patterns e.g. 'xy'
* Alternatively :code:`p1.then(p2)`
* :code:`p1 | p2` - matches either p1 or p2. This is like an alternation e.g. 'x|y'
* Alternatively :code:`p1.otherwise(p2)`
* :code:`p.repeat()` - matches zero or more repetitions of p. This is like the Kleene star e.g. 'x*'
* :code:`p.optional()` - matches zero or one repetitions of p. This is like 'x?'

Convenience functions and methods
=================================

* :code:`Items(\*args)` - matches a sequence of items equal to :code:`\*args`. This is a convenience function that is equivalent to :code:`Item(args[0]) & Item(args[1]) & ...`.
* :code:`IfItems(\*predicates)` - matches a sequence here each items satisfies the correponding predicate function. This is a convenience function that is equivalent to :code:`IfItem(predicates[0]) & IfItem(predicates[1]) & ...`.


* :code:`p.thenAny()` - matches p followed by any single item. This is a convenience method that is equivalent to :code:`p.then(ANY)`.
* :code:`p.thenMany()` - matches p followed by zero or more items. This is a convenience method that is equivalent to :code:`p.then(MANY)`.

* :code:`p.thenItems(\*args)` - matches p followed by a sequence of items equal to :code:`\*args`. This is a convenience method that is equivalent to :code:`p.then(Item(args[0]).then(Item(args[1])...`.
* :code:`p.thenIfItems(\*predicates)` - matches p followed by a sequence here each items satisfies the correponding predicate function. This is a convenience method that is equivalent to :code:`p.then(Item(args[0]).then(Item(args[1])...`.
* :code:`p.thenOneOf(\*args)` - matches p followed by any of the listed items. This is a convenience method that is equivalent to :code:`p.then(OneOf(args[0], args[1], ...))`.




Matching Groups
===============

Matching groups work like capturing groups in regular expressions. They allow us
to extract the matched subsequence:

* :code:`p.var(NAME, suchthat=None, extract=None)` - matches p and binds the match to the name NAME. This is like a capturing group e.g. '(x)'. 

If the optional function argument 'suchthat' is supplied then the match is only 
bound if it returns True. The function suchthat takes three arguments, the 
input-sequence, the lower bound and the upper bound. This can be used to
constrain the match to a particular length or have particular properties.

If the optional function argument 'extract' is supplied then the match variable is
bound to the result of extract. This function also takes three arguments, the 
input-sequence, the lower bound and the upper bound. This can be used to perform
conversions on the matched subsequence, such as forcing to lower case, or to
simply bind to the length of the match.

Adding a match group will change the return value of :code:`matches` from a 
boolean to a namespace object. This is a simple object that has the match 
with the match variables bound as attributes.

Here is an example of using a match group to extract a run of numbers less
than 10.

.. code-block:: python

   from regex4seq import *

   # This pattern matches a sequence of numbers that are all less than 10.
   pattern = IfItem(lambda x: x < 10).repeat().var("numbers") & MANY

   ns = pattern.matches([1,2,3,4,5,10,7,8,9])

   # We can access the match variables as attributes of the namespace.
   ns.numbers
   # [1, 2, 3, 4, 5]

And here is how we could do the same thing using the 'suchthat' argument. This
will be less efficient because it generates possible subsequences and then 
tests them, rather than testing as it goes.

.. code-block:: python

   from regex4seq import *

   # This pattern matches a sequence of numbers that are all less than 10.
   pattern = MANY.var("numbers", suchthat=lambda x, l, u: all(x[i] < 10 for i in range(l, u)))

   # As we will see later, we can call matches with the argument 'end=False' to
   # avoid anchoring the match at the start. This remove the need to append the
   # MANY pattern to the end of the match.
   ns = pattern.matches([1,2,3,4,5,10,7,8,9], end=False)
   ns.numbers
   # [1, 2, 3, 4, 5]

And this is how you would might retrieve the sum of the matched run of numbers
by utilizing the 'extract' argument.

.. code-block:: python

   from regex4seq import *

   def allLessThan10(x, l, u): return all(x[i] < 10 for i in range(l, u))

   def sumAll(x, l, u): return sum(x[i] for i in range(l, u))

   pattern = MANY.var("numbers", suchthat=allLessThan10, extract=sumAll)

   ns = pattern.matches([1,2,3,4,5,10,7,8,9], end=False)
   ns.numbers
   # 15


Conditional patterns
====================

These patterns are used to match items based on some condition. They don't really
have a direct analogue with ordinary regular expressions because the condition
can be arbitrary code.

Constrain current item
----------------------

We can require the next item to satisfy an arbitrary condition by using the 
:code:`IfItem` constructor. This takes a function that takes the current item
and returns True if the item should be matched. We have actualy already used
this in previous examples but we're giong to describe it a bit better here.

* :code:`IfItem(func)` - matches an item if :code:`func(item)` returns True.

For example, we could match only uppercase strings like this:

.. code-block:: python

   from regex4seq import IfItem

   # This pattern matches a sequence of strings that are uppercase.
   pattern = IfItem(lambda x: x.isupper()).repeat()

   pattern.matches(["this", "is", "THE", "ANSWER"])
   # False
   pattern.matches(["ALL", "CAPS"])
   # True


Look-ahead to next item
-----------------------

:code:`IfNext` provides a very limited form of look-ahead. Instead of just testing the
current item, this constructor takes a function that tests the current item and
the following item. For example, we could match the longest ascending sequence
of numbers at the start of a list of numbers just by writing the obvious 
comparison.

.. code-block:: python

   from regex4seq import IfNext

   # This pattern matches the longest ascending sequence of numbers at
   # the start of a list of numbers. The 'var' method names an attribute
   # to bind the match against.
   pattern = IfNext(lambda x, y: x < y).repeat().var("ascending")

   ns = pattern.matches([1,3,4,8,10,9,7,4,6,2], end=False)
   ns
   # namespace(ascending=[1, 3, 4, 8])

Notice that this pattern actually leaves off the last item in the sequence. 
Although that makes sense, you probably want to include it as part of the 
match. The most direct way is to always include one element like this:

.. code-block:: python

   from regex4seq import IfNext

   # `.thenAny()` concatenates a match-any-one item pattern. It is a 
   # convenience method as it could as easily be written as `.then(ANY)`.
   pattern = IfNext(lambda x, y: x < y).repeat().thenAny().var("ascending")

   ns = pattern.matches([1,3,4,8,10,9,7,4,6,2], end=False)
   ns
   # namespace(ascending=[1, 3, 4, 8, 10])

Other Ways to Match
===================

The :code:`matches` method takes four optional arguments that can be used to
alter the way the pattern is matched.

* :code:`pattern.matches(input-sequence, start=True, end=True, namespace=True, history=None)`

In this section we explore the ways to use these arguments.

Anchored and Unanchored matches
-------------------------------

Normally :code:`matches` will only return True if the pattern matches the entire
input-sequence. This is because the search is anchored at both the start and
end. You can change this with the arguments :code:`start` and :code:`end` which
control whether or not the match is anchored at the start of the input-sequence 
and/or the end of the input-sequence, respectively. 

For example,  it is common to only want to match against the 
first part of a sequence. To do this, we would set the optional argument `end` 
to False. We have seen a few examples of this already.

Another common scenario is wanting to find a matching anywhere in the sequence.
To do this, we would set both `start` and `end` to False.

.. code-block:: python

   from regex4seq import *

   # This pattern matches the sequence "a" followed by "b".
   pattern = Item("a") & Item("b")

   pattern.matches("this sequence contains ab somewhere", start=False, end=False)
   # True

Match without binding
---------------------

Because binding match variables can strongly impact performance, we sometimes want
to turn off the binding. We can do this by setting the optional argument
:code:`namespace` to False. Note that the 'suchthat' predicates are still run 
although the 'extract' functions will not be used.

Match with all possible bindings
--------------------------------

A match variable might actually be bound multiple times throughout a match. 
Normally only the first match is returned. But we can find all possible matches
by supplying the `history` option. This is a dictionary that maps variable names
into their counterparts. These counterparts will be bound to a sequence (deque) 
of all the matches made to that variable during a successful match.

.. code-block:: python

   from regex4seq import *

   pattern = Item("a").var("match") & Item("b").var("match")

   ns = pattern.matches("this sequence contains ab somewhere", start=False, end=False, history={'match':'all_matches'})
   ns
   # namespace(match='a', all_matches=deque(['a', 'b']))


Find all possible matches
--------------------------

We can use the method :code:`findAllMatches` to find all possible matches. This
works by returning a generator of namespace objects (or True if there are no 
matches). 

.. code:: python

   from regex4seq import *

   pattern = ((Item("a") & Item("b")) | Item("c")).var("match")

   for ns in pattern.findAllMatches("this sequence contains ab somewhere", start=False, end=False):
      print(ns.match)
   # c
   # c
   # ab



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
