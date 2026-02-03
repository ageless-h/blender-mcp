# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluationCriteria:
    stability_threshold: float
    security_threshold: float


class EvaluationGate:
    def __init__(self, criteria: EvaluationCriteria) -> None:
        self.criteria = criteria

    def check(self, stability_score: float, security_score: float) -> bool:
        return (
            stability_score >= self.criteria.stability_threshold
            and security_score >= self.criteria.security_threshold
        )
