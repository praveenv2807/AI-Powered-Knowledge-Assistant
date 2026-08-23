from dataclasses import dataclass
from typing import Any


@dataclass
class EvaluationResult:
    status: str
    confidence: float
    evidence_count: int
    reason: str


class ReliabilityEvaluator:
    """
    Evaluates whether retrieved evidence is strong enough
    to support an answer.
    """

    def __init__(
        self,
        minimum_score: float = 0.45,
        strong_score: float = 0.60,
        minimum_evidence: int = 1,
    ):
        self.minimum_score = minimum_score
        self.strong_score = strong_score
        self.minimum_evidence = minimum_evidence

    def evaluate(self, results: list[dict[str, Any]]) -> EvaluationResult:
        if not results:
            return EvaluationResult(
                status="not_found",
                confidence=0.0,
                evidence_count=0,
                reason="No supporting evidence was retrieved.",
            )

        valid_results = [
            result
            for result in results
            if isinstance(result.get("score"), (int, float))
        ]

        if not valid_results:
            return EvaluationResult(
                status="not_found",
                confidence=0.0,
                evidence_count=0,
                reason="Retrieved results contained no valid confidence scores.",
            )

        scores = [
            max(0.0, min(1.0, float(result["score"])))
            for result in valid_results
        ]

        strongest_score = max(scores)

        supporting = [
            result
            for result in valid_results
            if float(result["score"]) >= self.minimum_score
        ]

        if len(supporting) < self.minimum_evidence:
            return EvaluationResult(
                status="not_found",
                confidence=round(strongest_score, 3),
                evidence_count=len(supporting),
                reason="Retrieved evidence is below the minimum reliability threshold.",
            )

        if strongest_score >= self.strong_score:
            status = "verified"
        else:
            status = "partial"

        confidence = self._calculate_confidence(scores)

        return EvaluationResult(
            status=status,
            confidence=confidence,
            evidence_count=len(supporting),
            reason=(
                "Strong supporting evidence was retrieved."
                if status == "verified"
                else "Some relevant evidence was retrieved, but confidence is limited."
            ),
        )

    def _calculate_confidence(self, scores: list[float]) -> float:
        strongest = max(scores)

        supporting = [
            score for score in scores
            if score >= self.minimum_score
        ]

        if not supporting:
            return round(strongest, 3)

        # Give the strongest evidence the greatest influence.
        weighted = (
            strongest * 0.70
            + (sum(supporting) / len(supporting)) * 0.30
        )

        return round(min(weighted, 1.0), 3)