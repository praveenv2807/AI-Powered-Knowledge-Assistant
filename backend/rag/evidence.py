from typing import Any


def assess_evidence(
    question: str,
    results: list[dict[str, Any]],
    minimum_score: float = 0.45,
) -> dict:
    """
    Prepare evidence that has already been accepted by K-GUARD.

    Reliability decisions are handled by ReliabilityEvaluator.
    This function only filters and formats the evidence that
    the generator is allowed to use.

    This prevents multiple conflicting evidence thresholds
    from producing inconsistent decisions.
    """

    if not results:
        return {
            "status": "not_found",
            "evidence": [],
        }

    accepted = []

    for result in results:

        if not isinstance(result, dict):
            continue

        score = result.get("score", 0.0)

        if not isinstance(score, (int, float)):
            continue

        if float(score) < minimum_score:
            continue

        accepted.append(result)

    if not accepted:
        return {
            "status": "not_found",
            "evidence": [],
        }

    accepted.sort(
        key=lambda item: float(
            item.get("score", 0.0)
        ),
        reverse=True,
    )

    return {
        "status": "verified",
        "evidence": accepted,
    }