from typing import Any

from .evaluator import ReliabilityEvaluator


class ReliabilityReport:
    """
    Builds a judge-friendly reliability report from retrieved evidence.
    """

    def __init__(self, evaluator: ReliabilityEvaluator | None = None):
        self.evaluator = evaluator or ReliabilityEvaluator()

    def build(self, results: list[dict[str, Any]]) -> dict:
        evaluation = self.evaluator.evaluate(results)

        sources = []

        for result in results:
            if not isinstance(result, dict):
                continue

            score = result.get("score")

            if not isinstance(score, (int, float)):
                continue

            sources.append({
                "document": result.get("document"),
                "page": result.get("page"),
                "section": result.get("section"),
                "score": round(float(score), 3),
            })

        sources.sort(
            key=lambda source: source["score"],
            reverse=True
        )

        return {
            "status": evaluation.status,
            "confidence": evaluation.confidence,
            "confidence_percent": round(
                evaluation.confidence * 100,
                1
            ),
            "evidence_count": evaluation.evidence_count,
            "reason": evaluation.reason,
            "sources": sources,
        }