# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ServiceState(str, Enum):
    INIT = "init"
    READY = "ready"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class ServiceLifecycle:
    state: ServiceState = ServiceState.INIT
    error_code: int | None = None

    def mark_ready(self) -> None:
        self.state = ServiceState.READY
        self.error_code = None

    def stop(self) -> None:
        self.state = ServiceState.STOPPING
        self.state = ServiceState.STOPPED

    def fail(self, error_code: int) -> None:
        self.state = ServiceState.ERROR
        self.error_code = error_code
