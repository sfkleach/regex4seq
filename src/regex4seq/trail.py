from abc import ABC, abstractmethod
from types import SimpleNamespace

class Trail(ABC):

    @abstractmethod
    def add(self, name, lo, hi, call):
        ...

    def namespace(self, inputSeq):
        return True

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

    def add(self, name, lo, hi, call) -> 'CaptureTrail':
        return CaptureTrail(name, lo, hi, call, self)

    def namespace(self, inputSeq) -> SimpleNamespace:
        ns = SimpleNamespace()
        t = self
        while isinstance(t, CaptureTrail):
            if self._call:
                value = self._call(inputSeq, t._lo, t._hi)
            else:
                value = inputSeq[t._lo:t._hi]
            setattr(ns, t._name, value)
            t = t._trail
        return ns

class StartCaptureTrail(Trail):

    def add(self, name, lo, hi, call):
        return CaptureTrail(name, lo, hi, call, self)
