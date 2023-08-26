from abc import ABC, abstractmethod
from typing import Iterator, Sequence, Any, Annotated
from types import SimpleNamespace

from .trail import Trail, DiscardTrail, StartCaptureTrail

class RegEx4Seq(ABC):
    """
    RegEx4Seq is a regular expression pattern that matches against a sequence 
    of items.
    """

    def match(self, inputSeq: Sequence[Any], namespace: bool=False) -> bool | SimpleNamespace:
        """
        Returns truthy if the pattern matches the inputSeq. If namespace is
        set to True, then a namespace object is returned that contains the
        bindings that were captured during the match.
        """
        ns = StartCaptureTrail() if namespace else DiscardTrail()
        for idx, t in self._gobble(inputSeq, 0, ns):
            if idx == len(inputSeq):
                return t.namespace() if namespace else True
        return False

    @abstractmethod
    def _gobble(self, inputSeq: Sequence[Any], idx: int, trail: Trail) -> Iterator[tuple[int, Trail]]:
        """
        This is the heart of the RegEx4Seq pattern matching algorithm. It is
        the method that is recursively called to find matches. It returns a
        generator that will find all matches, returning the index of how far
        the match extends and a trail of bindings. It is implemented for each
        of the subclasses of RegEx4Seq, which are Empty, Item, TestItem, Any,
        Many, Concatenate, Alternate, Repeat, and MatchGroup.
        :meta private:
        """
        ...

    def concatenate(self, Q):
        """
        Given a pattern Q, returns a new pattern that matches the original P
        followed by Q. It is analogous to PQ in regular expressions.
        """
        if isinstance(Q, Empty):
            return self
        return Concatenate(self, Q)

    def alternate(self, *alts):
        """
        Given a sequence of patterns, returns a new pattern that matches the
        original P or any of the patterns in the sequence. It is analogous to
        P|Q|R|... in regular expressions.
        """
        if len(alts) == 0:
            return self
        elif len(alts) == 1 and isinstance(alts[0], Empty):
            return self.optional()
        return Alternate(self, *alts)

    def repeat(self):
        """
        Returns a new pattern that matches zero or more occurences of the
        original pattern P. Analogous to P* in regular expressions.
        """
        return Repeat(self)

    def optional(self):
        """
        Returns a new pattern that matches zero or one occurences of the 
        original pattern P.
        Analogous to P? in regular expressions.
        """
        return Optional(self)

    def addTest(self, predicateFunction):
        """
        Given a predicate-function, returns a new pattern that matches the
        original pattern P followed by an items that satisfies the predicate.
        """
        return self.concatenate(TestItem(predicateFunction))

    def addItem(self, item):
        """
        Given an item, returns a new pattern that matches the
        original pattern P followed by a value that is equal to the item.
        """
        return self.concatenate(Item(item))

    def addAny(self):
        """
        Returns a new pattern that matches the original pattern P followed by
        any item.
        """
        return self.concatenate(TestItem(lambda x: True))


class Empty(RegEx4Seq):
    """Represents a pattern that matches no items."""

    def _gobble(self, inputSeq: Sequence[Any], idx: int, trail: Trail) -> Iterator[tuple[int, Trail]]:
        """:meta private:"""
        yield idx, trail

    def concatenate(self, Q):
        return Q

    def alternate(self, *alts):
        if len(alts) == 0:
            return self
        elif len(alts) == 1:
            return alts[0].optional()
        else:
            return Alternate(self, *alts)

    def repeat(self):
        return self

    def optional(self):
        return self


class Item(RegEx4Seq):
    """
    Wraps an item to create a pattern that matches against that item.
    """

    def __init__(self, item):
        self._item = item

    def _gobble(self, inputSeq: Sequence[Any], idx: int, trail: Trail) -> Iterator[tuple[int, Trail]]:
        """:meta private:"""
        if idx < len(inputSeq):
            if inputSeq[idx] == self._item:
                yield idx + 1, trail


# Predicate is any function that given an inputSeq returns a bool.
class TestItem(RegEx4Seq):
    """Wraps a predicate function to create a pattern that matches against any item that satisfies the predicate."""
    __test__ = False # Ignore this class in pytest.

    def __init__(self, predicateFunction):
        self._pf = predicateFunction

    def _gobble(self, inputSeq, idx: int, trail: Trail) -> Iterator[tuple[int, Trail]]:
        """:meta private:"""
        if idx < len(inputSeq):
            if self._pf(inputSeq[idx]):
                yield idx + 1, trail


class AnyItem(RegEx4Seq):

    def _gobble(self, inputSeq: Sequence[Any], idx: int, trail: Trail) -> Iterator[tuple[int, Trail]]:
        """:meta private:"""
        if idx < len(inputSeq):
            yield idx + 1, trail

    def repeat(self):
        return ManyItems()


class ManyItems(RegEx4Seq):

    def _gobble(self, inputSeq: Sequence[Any], idx: int, trail: Trail) -> Iterator[tuple[int, Trail]]:
        """:meta private:"""
        for i in range(idx, len(inputSeq) + 1):
            yield i, trail

    def repeat(self):
        return self
    
    def optional(self):
        return self


class Optional(RegEx4Seq):

    def __init__(self, original: RegEx4Seq):
        self._original: RegEx4Seq = original

    def _gobble(self, inputSeq: Sequence[Any], idx: int, trail: Trail) -> Iterator[tuple[int, Trail]]:
        """:meta private:"""
        # Either we consume some inputSeq.
        yield from self._original._gobble(inputSeq, idx, trail)
        # Or we don't.
        yield idx, trail

    def optional(self):
        return self

    def repeat(self):
        return self._original.repeat()


class Concatenate(RegEx4Seq):

    def __init__(self, lhs: RegEx4Seq, rhs: RegEx4Seq):
        self._lhs: RegEx4Seq = lhs
        self._rhs: RegEx4Seq = rhs

    def _gobble(self, inputSeq: Sequence[Any], idx: int, trail: Trail) -> Iterator[tuple[int, Trail]]:
        """:meta private:"""
        for idx1, t in self._lhs._gobble(inputSeq, idx, trail):
            yield from self._rhs._gobble(inputSeq, idx1, t)


class Alternate(RegEx4Seq):
    """
    Equivalent to R|S
    Matches against R or matches against S
    Examples:
    a|b   that will match 1 character which is either 'a' or 'b'
    abc|d that will match 3 characters (abc) or 1 character (d)
    """

    def __init__(self, *alts: RegEx4Seq):
        self._alts: tuple[RegEx4Seq, ...] = alts

    def _gobble(self, inputSeq: Sequence[Any], idx, trail: Trail) -> Iterator[tuple[int, Trail]]:
        """:meta private:"""
        for p in self._alts:
            yield from p._gobble(inputSeq, idx, trail)

    def alternate(self, *moreAlts):
        return Alternate(*self._alts, *moreAlts)


class Repeat(RegEx4Seq):

    def __init__(self, original: RegEx4Seq):
        self._original: RegEx4Seq = original

    def _gobble(self, inputSeq: Sequence[Any], idx: int, trail: Trail) -> Iterator[tuple[int, Trail]]:
        """:meta private:"""
        # Is there a non-zero repetition of original pattern?
        for remaining, t in self._original._gobble(inputSeq, idx, trail):
            if remaining > idx:
                # Yes, there is. Recursively iterate more.
                yield from self._gobble(inputSeq, remaining, t)
        # Zero iteration of original RegEx4Seq

        yield idx, trail

    def repeat(self):
        return self


class MatchGroup(RegEx4Seq):
    """
    Creates a named group that can be used to capture a subsequence of the of
    the input sequence. The captured subsequence can be retrieved by using the
    matching attribute from the namespace object returned by the match method.
    """

    def __init__(self, name, original: RegEx4Seq):
        self._name = name
        self._original : RegEx4Seq = original

    def _gobble(self, inputSeq: Sequence[Any], idx: int, trail: Trail) -> Iterator[tuple[int, Trail]]:
        """:meta private:"""
        for r, t in self._original._gobble(inputSeq, idx, trail):
            yield r, t.add(inputSeq, self._name, idx, r)

NONE: Annotated[Empty, """This is a singleton that matches the empty sequence."""] = Empty()
"""This is a singleton that matches the empty sequence."""

ANY = AnyItem()
"""This is a singleton that matches any one item from a sequence."""

# Ahead of it.
MANY = ManyItems()
# This is a singleton that matches any number of items from a sequence.

if __name__ == "__main__":
    pass
