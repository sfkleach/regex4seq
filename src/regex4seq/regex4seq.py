from abc import ABC, abstractmethod
from typing import Iterator, Sequence, Any, Annotated
from types import SimpleNamespace

from .trail import Trail, DiscardTrail, StartCaptureTrail

class RegEx4Seq(ABC):
    """
    RegEx4Seq is a regular expression pattern that matches against a sequence
    of items.
    """

    def matches(self, inputSeq: Sequence[Any], namespace: bool=True, start=True, end=True) -> bool | SimpleNamespace:
        """
        Returns truthy if the pattern matches the inputSeq. If namespace is
        set to True, then a namespace object is returned that contains the
        bindings that were captured during the match.

        If start is truthy then the pattern is anchored at the start. If end
        is truthy then the pattern is anchored at the end. If both start and
        end are truthy then the pattern must match the entire inputSeq.
        """
        ns = StartCaptureTrail() if namespace else DiscardTrail()
        for start_idx in range(0, 1 if start else len(inputSeq) + 1):
            for idx, t in self._gobble(inputSeq, start_idx, ns):
                if not(end) or idx == len(inputSeq):
                    return t.namespace(inputSeq)
        return False

    def findAllMatches(self, inputSeq: Sequence[Any]) -> Iterator[SimpleNamespace]:
        """
        Returns a generator that will find all matches of the pattern in the
        inputSeq. Each match is returned as a namespace object that contains
        the bindings that were captured during the match.
        """
        ns = StartCaptureTrail()
        for idx, t in self._gobble(inputSeq, 0, ns):
            if idx == len(inputSeq):
                yield t.namespace(inputSeq)

    @abstractmethod
    def _gobble(self, inputSeq: Sequence[Any], idx: int, trail: Trail) -> Iterator[tuple[int, Trail]]:
        """
        This is the heart of the RegEx4Seq pattern matching algorithm. It is
        the method that is recursively called to find matches. It returns a
        generator that will find all matches, returning the index of how far
        the match extends and a trail of bindings. It is implemented for each
        of the subclasses of RegEx4Seq, which are Empty, Item, IfItem, Any,
        Many, Concatenate, Alternate, Repeat, and MatchGroup.
        :meta private:
        """
        ...

    def then(self, Q):
        """
        Given a pattern Q, returns a new pattern that matches the original P
        followed by Q. It is analogous to PQ in regular expressions.
        """
        if isinstance(Q, Empty):
            return self
        return Then(self, Q)

    def otherwise(self, Q):
        """
        Given a pattern Q, returns a new pattern that matches the
        original P or Q. It is analogous to P|Q in regular expressions.
        """
        if isinstance(Q, Empty):
            return self.optional()
        return Otherwise(self, Q)

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

    def thenIfItem(self, predicateFunction):
        """
        Given a predicate-function, returns a new pattern that matches the
        original pattern P followed by an items that satisfies the predicate.
        """
        return self.then(IfItem(predicateFunction))

    def thenItem(self, item):
        """
        Given an item, returns a new pattern that matches the
        original pattern P followed by a value that is equal to the item.
        """
        return self.then(Item(item))

    def thenAny(self):
        """
        Returns a new pattern that matches the original pattern P followed by
        any item.
        """
        return self.then(IfItem(lambda x: True))

    def var(self, name, suchthat=None, extract=None):
        return MatchGroup(name, self, suchthat=suchthat, extract=extract)

    def __and__(self, Q):
        return self.then(Q)

    def __or__(self, Q):
        return self.otherwise(Q)


class Empty(RegEx4Seq):
    """Represents a pattern that matches no items."""

    def _gobble(self, inputSeq: Sequence[Any], idx: int, trail: Trail) -> Iterator[tuple[int, Trail]]:
        """:meta private:"""
        yield idx, trail

    def then(self, Q):
        return Q

    def otherwise(self, Q):
        return Q.optional()
        
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

    def otherwise(self, Q):
        if isinstance(Q, Item):
            return OneOf(self, Q)
        elif isinstance(Q, OneOf):
            return Q.otherwise(self)
        else:
            return Otherwise(self, Q)

class OneOf(RegEx4Seq):

    def __init__(self, *items):
        self._items = set(items)

    def _gobble(self, inputSeq: Sequence[Any], idx: int, trail: Trail) -> Iterator[tuple[int, Trail]]:
        """:meta private:"""
        if idx < len(inputSeq):
            if inputSeq[idx] in self._items:
                yield idx + 1, trail

    def otherwise(self, Q):
        if isinstance(Q, Item):
            return OneOf(Q, self._items)
        elif isinstance(Q, OneOf):
            return OneOf(*self._items, *Q._items)
        else:
            return Otherwise(self, Q)


class IfNext(RegEx4Seq):

    def __init__(self, predicateFunction):
        self._pf = predicateFunction

    def _gobble(self, inputSeq: Sequence[Any], idx: int, trail: Trail) -> Iterator[tuple[int, Trail]]:
        """:meta private:"""
        if idx + 1 < len(inputSeq):
            if self._pf(inputSeq[idx], inputSeq[idx + 1]):
                yield idx + 1, trail


# Predicate is any function that given an inputSeq returns a bool.
class IfItem(RegEx4Seq):
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
        for i in range( len(inputSeq), idx - 1, -1): #range(idx, len(inputSeq) + 1):
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


class Then(RegEx4Seq):

    def __init__(self, lhs: RegEx4Seq, rhs: RegEx4Seq):
        self._lhs: RegEx4Seq = lhs
        self._rhs: RegEx4Seq = rhs

    def _gobble(self, inputSeq: Sequence[Any], idx: int, trail: Trail) -> Iterator[tuple[int, Trail]]:
        """:meta private:"""
        for idx1, t in self._lhs._gobble(inputSeq, idx, trail):
            yield from self._rhs._gobble(inputSeq, idx1, t)


class Otherwise(RegEx4Seq):
    """
    Equivalent to R|S
    Matches against R or matches against S
    Examples:
    a|b   that will match 1 character which is either 'a' or 'b'
    abc|d that will match 3 characters (abc) or 1 character (d)
    """

    def __init__(self, P: RegEx4Seq, Q: RegEx4Seq):
        self._lhs = P
        self._rhs = Q
        
    def _gobble(self, inputSeq: Sequence[Any], idx, trail: Trail) -> Iterator[tuple[int, Trail]]:
        """:meta private:"""
        yield from self._lhs._gobble(inputSeq, idx, trail)
        yield from self._rhs._gobble(inputSeq, idx, trail)



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

    def __init__(self, name, original: RegEx4Seq, suchthat=None, extract=None):
        self._name = name
        self._original : RegEx4Seq = original
        self._extract = extract
        self._suchthat = suchthat

    def _gobble(self, inputSeq: Sequence[Any], idx: int, trail: Trail) -> Iterator[tuple[int, Trail]]:
        """:meta private:"""
        for r, t in self._original._gobble(inputSeq, idx, trail):
            if self._suchthat is None or self._suchthat(inputSeq, idx, r):
                yield r, t.add(self._name, idx, r, self._extract)

NONE: Annotated[Empty, """This is a singleton that matches the empty sequence."""] = Empty()
"""This is a singleton that matches the empty sequence."""

ANY = AnyItem()
"""This is a singleton that matches any one item from a sequence."""

# Ahead of it.
MANY = ManyItems()
# This is a singleton that matches any number of items from a sequence.

if __name__ == "__main__":
    pass
