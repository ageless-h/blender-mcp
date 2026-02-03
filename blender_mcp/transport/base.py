# -*- coding: utf-8 -*-
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable


class TransportAdapter(ABC):
    @abstractmethod
    def start(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def send(self, message: bytes) -> None:
        raise NotImplementedError

    @abstractmethod
    def receive(self) -> Iterable[bytes]:
        raise NotImplementedError
