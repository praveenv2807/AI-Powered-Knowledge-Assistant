from dataclasses import dataclass
from typing import Any

from .evidence_quality import EvidenceQualityScorer


@dataclass
class EvaluationResult:
    status: str
    confidence: float
    evidence_count: int
    reason: str


class ReliabilityEvaluator:
    """
    K-GUARD reliability evaluator.

    Determines whether retrieved evidence is strong enough
    to support an answer.

    Evidence quality is evaluated using:
        1. Semantic similarity
        2. Lexical overlap
        3. Combined evidence quality
        4. Number of supporting evidence items

    The evaluator intentionally prefers strong lexical +
    semantic agreement over raw semantic similarity alone.
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

        self.quality_scorer = EvidenceQualityScorer()

    def evaluate(
        self,
        results: list[dict[str, Any]],
        question: str | None = None,
    ) -> EvaluationResult:

        if not results:
            return EvaluationResult(
                status="not_found",
                confidence=0.0,
                evidence_count=0,
                reason="No supporting evidence was retrieved.",
            )

        # --------------------------------------------------
        # 1. Calculate evidence quality
        # --------------------------------------------------

        if question:

            quality_results = []

            for result in results:

                quality = self.quality_scorer.score(
                    question,
                    result,
                )

                quality_results.append(
                    {
                        **result,
                        "quality": quality,
                    }
                )

            scores = [
                result["quality"]["combined_score"]
                for result in quality_results
            ]

            supporting = [
                result
                for result in quality_results
                if result["quality"]["combined_score"]
                >= self.minimum_score
            ]

        else:

            # Backward-compatible mode.

            valid_results = [
                result
                for result in results
                if isinstance(
                    result.get("score"),
                    (int, float),
                )
            ]

            if not valid_results:
                return EvaluationResult(
                    status="not_found",
                    confidence=0.0,
                    evidence_count=0,
                    reason=(
                        "Retrieved results contained "
                        "no valid confidence scores."
                    ),
                )

            scores = [
                max(
                    0.0,
                    min(
                        1.0,
                        float(result["score"]),
                    ),
                )
                for result in valid_results
            ]

            supporting = [
                result
                for result in valid_results
                if float(result["score"])
                >= self.minimum_score
            ]

            quality_results = valid_results

        # --------------------------------------------------
        # 2. No usable evidence
        # --------------------------------------------------

        if not scores:
            return EvaluationResult(
                status="not_found",
                confidence=0.0,
                evidence_count=0,
                reason="No valid evidence scores were available.",
            )

        strongest_score = max(scores)

        # --------------------------------------------------
        # 3. Minimum evidence gate
        # --------------------------------------------------

        if len(supporting) < self.minimum_evidence:
            return EvaluationResult(
                status="not_found",
                confidence=round(
                    strongest_score,
                    3,
                ),
                evidence_count=len(supporting),
                reason=(
                    "Retrieved evidence is below "
                    "the minimum reliability threshold."
                ),
            )

        # --------------------------------------------------
        # 4. Determine reliability level
        # --------------------------------------------------

        if question:

            best = max(
                quality_results,
                key=lambda item: item["quality"]["combined_score"],
            )

            quality = best["quality"]

            semantic_score = quality["semantic_score"]
            lexical_score = quality["lexical_score"]
            combined_score = quality["combined_score"]
            matched_terms = quality["matched_terms"]

            # ----------------------------------------------
            # Strong hybrid evidence
            #
            # Example:
            # semantic ≈ 0.55
            # lexical  = 1.00
            #
            # This is often stronger evidence than a
            # semantically similar but lexically unrelated
            # passage.
            # ----------------------------------------------

            strong_hybrid_evidence = (
                semantic_score >= 0.50
                and lexical_score >= 0.75
                and combined_score >= self.minimum_score
                and len(matched_terms) >= 1
            )

            if (
                combined_score >= self.strong_score
                or strong_hybrid_evidence
            ):
                status = "verified"

                reason = (
                    "Strong semantic and lexical evidence "
                    "supports the answer."
                )

            else:
                status = "partial"

                reason = (
                    "Relevant evidence was retrieved, "
                    "but confidence is limited."
                )

        else:

            if strongest_score >= self.strong_score:
                status = "verified"

                reason = (
                    "Strong supporting evidence was retrieved."
                )

            else:
                status = "partial"

                reason = (
                    "Some relevant evidence was retrieved, "
                    "but confidence is limited."
                )

        # --------------------------------------------------
        # 5. Calculate confidence
        # --------------------------------------------------

        confidence = self._calculate_confidence(
            scores
        )

        return EvaluationResult(
            status=status,
            confidence=confidence,
            evidence_count=len(supporting),
            reason=reason,
        )

    def _calculate_confidence(
        self,
        scores: list[float],
    ) -> float:

        strongest = max(scores)

        supporting = [
            score
            for score in scores
            if score >= self.minimum_score
        ]

        if not supporting:
            return round(
                strongest,
                3,
            )

        # Strongest evidence receives the greatest influence.

        weighted = (
            strongest * 0.70
            + (
                sum(supporting)
                / len(supporting)
            ) * 0.30
        )

        return round(
            min(weighted, 1.0),
            3,
        )