from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class BenchmarkCase:
    question: str
    expected_status: str


class BenchmarkRunner:
    """
    Runs a set of questions against the K-GUARD pipeline
    and measures whether the system made the expected
    grounding decision.
    """

    def __init__(self, pipeline: Any):
        self.pipeline = pipeline

    def run(
        self,
        cases: list[BenchmarkCase],
    ) -> dict:
        results = []

        for case in cases:
            response = self.pipeline.answer_question(case.question)

            actual_status = response.get(
                "status",
                "not_found"
            )

            passed = actual_status == case.expected_status

            results.append({
                "question": case.question,
                "expected": case.expected_status,
                "actual": actual_status,
                "passed": passed,
            })

        total = len(results)
        passed_count = sum(
            1 for result in results
            if result["passed"]
        )

        accuracy = (
            passed_count / total
            if total
            else 0.0
        )

        return {
            "total": total,
            "passed": passed_count,
            "failed": total - passed_count,
            "accuracy": round(accuracy, 3),
            "accuracy_percent": round(
                accuracy * 100,
                1
            ),
            "results": results,
        }