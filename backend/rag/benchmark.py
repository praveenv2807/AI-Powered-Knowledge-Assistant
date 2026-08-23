from dataclasses import dataclass
from typing import Any


@dataclass
class BenchmarkCase:
    """
    Defines one benchmark question.

    expected_status:
        verified
        partial
        not_found
    """

    question: str
    expected_status: str


class BenchmarkRunner:
    """
    Runs benchmark cases against the K-GUARD pipeline.

    Measures:

        1. Grounding decision accuracy
        2. Correct refusal behavior
        3. Evidence availability
        4. Confidence
        5. Source attribution

    This keeps the original status-based benchmark compatible
    while exposing richer evaluation metrics.
    """

    def __init__(self, pipeline: Any):
        self.pipeline = pipeline

    def run(
        self,
        cases: list[BenchmarkCase],
    ) -> dict:

        results = []

        for case in cases:

            response = self.pipeline.answer_question(
                case.question
            )

            actual_status = response.get(
                "status",
                "not_found",
            )

            expected_status = case.expected_status

            passed = (
                actual_status == expected_status
            )

            reliability = response.get(
                "reliability",
                {},
            )

            sources = response.get(
                "sources",
                [],
            )

            confidence = reliability.get(
                "confidence",
                0.0,
            )

            evidence_count = reliability.get(
                "evidence_count",
                len(sources),
            )

            # --------------------------------------------------
            # Safety evaluation
            # --------------------------------------------------

            expected_refusal = (
                expected_status == "not_found"
            )

            actual_refusal = (
                actual_status == "not_found"
            )

            correct_refusal = (
                expected_refusal
                and actual_refusal
            )

            # --------------------------------------------------
            # Evidence evaluation
            # --------------------------------------------------

            has_evidence = bool(
                sources
            )

            results.append(
                {
                    "question": case.question,
                    "expected": expected_status,
                    "actual": actual_status,
                    "passed": passed,

                    "confidence": round(
                        float(confidence),
                        3,
                    ),

                    "confidence_percent": round(
                        float(confidence) * 100,
                        1,
                    ),

                    "evidence_count": evidence_count,

                    "has_evidence": has_evidence,

                    "correct_refusal": correct_refusal,

                    "sources": sources,
                }
            )

        # ------------------------------------------------------
        # Aggregate metrics
        # ------------------------------------------------------

        total = len(results)

        passed_count = sum(
            1
            for result in results
            if result["passed"]
        )

        failed_count = (
            total - passed_count
        )

        accuracy = (
            passed_count / total
            if total
            else 0.0
        )

        # ------------------------------------------------------
        # Refusal metrics
        # ------------------------------------------------------

        refusal_cases = [
            result
            for result in results
            if result["expected"] == "not_found"
        ]

        correct_refusals = sum(
            1
            for result in refusal_cases
            if result["correct_refusal"]
        )

        refusal_accuracy = (
            correct_refusals
            / len(refusal_cases)
            if refusal_cases
            else 0.0
        )

        # ------------------------------------------------------
        # Evidence metrics
        # ------------------------------------------------------

        supported_cases = [
            result
            for result in results
            if result["expected"]
            in {
                "verified",
                "partial",
            }
        ]

        supported_with_evidence = sum(
            1
            for result in supported_cases
            if result["has_evidence"]
        )

        evidence_coverage = (
            supported_with_evidence
            / len(supported_cases)
            if supported_cases
            else 0.0
        )

        # ------------------------------------------------------
        # Confidence metrics
        # ------------------------------------------------------

        average_confidence = (
            sum(
                result["confidence"]
                for result in results
            )
            / total
            if total
            else 0.0
        )

        # ------------------------------------------------------
        # Return evaluation report
        # ------------------------------------------------------

        return {
            "total": total,

            "passed": passed_count,

            "failed": failed_count,

            "accuracy": round(
                accuracy,
                3,
            ),

            "accuracy_percent": round(
                accuracy * 100,
                1,
            ),

            "correct_refusals": correct_refusals,

            "refusal_accuracy": round(
                refusal_accuracy,
                3,
            ),

            "refusal_accuracy_percent": round(
                refusal_accuracy * 100,
                1,
            ),

            "evidence_coverage": round(
                evidence_coverage,
                3,
            ),

            "evidence_coverage_percent": round(
                evidence_coverage * 100,
                1,
            ),

            "average_confidence": round(
                average_confidence,
                3,
            ),

            "average_confidence_percent": round(
                average_confidence * 100,
                1,
            ),

            "results": results,
        }