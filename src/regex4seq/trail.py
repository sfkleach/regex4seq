from abc import ABC, abstractmethod
from types import SimpleNamespace

class Trail(ABC):

    @abstractmethod
    def add(self, inputSeq, name, lo, hi):
        ...

    def namespace(self):
        return SimpleNamespace()

class DiscardTrail(Trail):

    def add(self, inputSeq, name, lo, hi):
        return self


class CaptureTrail(Trail):

    def __init__(self, inputSeq, name, lo, hi, trail):
        self._inputSeq = inputSeq
        self._name = name
        self._lo = lo
        self._hi = hi
        self._trail = trail

    def add(self, inputSeq, name, lo, hi) -> 'CaptureTrail':
        return CaptureTrail(inputSeq, name, lo, hi, self)

    def namespace(self) -> SimpleNamespace:
        ns = SimpleNamespace()
        t = self
        while isinstance(t, CaptureTrail):
            setattr(ns, t._name, self._inputSeq[t._lo:t._hi])
            t = t._trail
        return ns

class StartCaptureTrail(Trail):

    def add(self, inputSeq, name, lo, hi):
        return CaptureTrail(inputSeq, name, lo, hi, self)