from abc import ABC, abstractmethod
from types import SimpleNamespace
from collections import deque

class Trail(ABC):

    @abstractmethod
    def add(self, name, lo, hi, call):
        ...

    def namespace(self, inputSeq, all_prefix=None) -> bool | SimpleNamespace:
        return True

    def isCapture(self) -> bool:
        return False


class DiscardTrail(Trail):

    def add(self, name, lo, hi, call):
        return self


class CaptureTrail(Trail):

    def __init__(self, name, lo, hi, call, trail):
        self._name = name
        self._lo = lo
        self._hi = hi
        self._trail = trail
        self._call = call

    def isCapture(self) -> bool:
        return True

    def add(self, name, lo, hi, call) -> 'CaptureTrail':
        return CaptureTrail(name, lo, hi, call, self)

    def namespace(self, inputSeq, all_prefix=None) -> bool | SimpleNamespace:
        ns = SimpleNamespace()
        t = self
        while t.isCapture():
            if self._call:
                value = self._call(inputSeq, t._lo, t._hi)
            else:
                value = inputSeq[t._lo:t._hi]
            setattr(ns, t._name, value)
            if all_prefix is not None:
                name = all_prefix + t._name
                if not hasattr(ns, name):
                    setattr(ns, name, deque())
                q = getattr(ns, name, [])
                q.appendleft(value)
                setattr(ns, name, q)
            t = t._trail
        return ns

class StartCaptureTrail(Trail):

    def add(self, name, lo, hi, call):
        return CaptureTrail(name, lo, hi, call, self)
