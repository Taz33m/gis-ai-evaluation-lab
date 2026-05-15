from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any


@dataclass(frozen=True)
class EvaluationResult:
    task_id: str
    response_id: str
    score: int
    max_score: int
    band: str
    matched_expectations: list[str]
    missed_expectations: list[str]
    triggered_red_flags: list[str]
    feedback: list[str]


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.casefold()).strip()


def contains_any(text: str, terms: list[str]) -> bool:
    normalized = normalize_text(text)
    return any(normalize_text(term) in normalized for term in terms)


def band_for_score(score: int, max_score: int) -> str:
    ratio = score / max_score if max_score else 0
    if ratio >= 0.85:
        return "strong"
    if ratio >= 0.65:
        return "acceptable"
    if ratio >= 0.4:
        return "needs_revision"
    return "fail"


def grade_response(task: dict[str, Any], response: dict[str, Any]) -> EvaluationResult:
    answer = response["answer"]
    expected = task.get("expected_concepts", [])
    red_flags = task.get("red_flags", [])
    max_score = int(task.get("max_score", len(expected) * 2 or 10))
    matched: list[str] = []
    missed: list[str] = []
    feedback: list[str] = []

    for concept in expected:
        label = concept["label"]
        terms = concept["terms"]
        if contains_any(answer, terms):
            matched.append(label)
        else:
            missed.append(label)

    triggered = [
        flag["label"]
        for flag in red_flags
        if contains_any(answer, flag["terms"])
    ]

    score = round((len(matched) / max(1, len(expected))) * max_score)
    if triggered:
        score = max(0, score - min(score, len(triggered) * 2))
        feedback.append(
            "Address red-flag language before approving this answer: "
            + ", ".join(triggered)
            + "."
        )

    if missed:
        feedback.append("Missing expected GIS concepts: " + ", ".join(missed) + ".")

    if not triggered and not missed:
        feedback.append("Answer covers the expected workflow and avoids major risk signals.")

    return EvaluationResult(
        task_id=task["id"],
        response_id=response["id"],
        score=score,
        max_score=max_score,
        band=band_for_score(score, max_score),
        matched_expectations=matched,
        missed_expectations=missed,
        triggered_red_flags=triggered,
        feedback=feedback,
    )
