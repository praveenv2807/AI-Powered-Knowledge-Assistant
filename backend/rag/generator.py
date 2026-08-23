def generate_answer(
    question: str,
    evidence_result: dict
) -> dict:
    """
    Generate a grounded answer using only retrieved evidence.

    If evidence is insufficient, refuse to answer.
    """

    status = evidence_result.get("status", "not_found")
    evidence = evidence_result.get("evidence", [])

    # Never answer when there is no supporting evidence.
    if status == "not_found" or not evidence:
        return {
            "status": "not_found",
            "answer": (
                "I couldn't find this information "
                "in the provided documents."
            ),
            "sources": []
        }

    # Use the strongest evidence first.
    best_evidence = sorted(
        evidence,
        key=lambda item: item.get("score", 0.0),
        reverse=True
    )

    primary = best_evidence[0]

    answer = primary.get("text", "").strip()

    source = {
        "document": primary.get("document"),
        "page": primary.get("page"),
        "section": primary.get("section"),
        "score": primary.get("score"),
    }

    return {
        "status": status,
        "answer": answer,
        "sources": [source]
    }