from typing import Any


def generate_answer(
    question: str,
    evidence_result: dict[str, Any],
) -> dict:
    """
    Generate a grounded answer using only extracted evidence.

    The generator is deterministic and does not invent information.

    For list questions, multiple evidence units can be returned.
    For factual questions, the strongest evidence is returned.
    """

    status = evidence_result.get(
        "status",
        "not_found",
    )

    evidence = evidence_result.get(
        "evidence",
        [],
    )

    # --------------------------------------------------
    # No verified evidence
    # --------------------------------------------------

    if status != "verified" or not evidence:
        return {
            "status": "not_found",
            "answer": (
                "I couldn't find this information "
                "in the provided documents."
            ),
            "sources": [],
        }

    # --------------------------------------------------
    # Sort strongest evidence first
    # --------------------------------------------------

    evidence = sorted(
        evidence,
        key=lambda item: item.get(
            "score",
            0.0,
        ),
        reverse=True,
    )

    # --------------------------------------------------
    # Detect list-style questions
    # --------------------------------------------------

    question_lower = question.lower()

    list_question = any(
        phrase in question_lower
        for phrase in [
            "what facilities",
            "what are the facilities",
            "which facilities",
            "what services",
            "what features",
            "what amenities",
            "what programs",
            "what departments",
            "what courses",
            "list",
        ]
    )

    # --------------------------------------------------
    # LIST ANSWER
    # --------------------------------------------------

    if list_question:

        answer_parts = []
        sources = []

        seen_text = set()

        for item in evidence:

            text = str(
                item.get(
                    "text",
                    "",
                )
            ).strip()

            if not text:
                continue

            normalized = text.lower()

            if normalized in seen_text:
                continue

            seen_text.add(normalized)

            answer_parts.append(text)

            sources.append(
                {
                    "document": item.get(
                        "document"
                    ),
                    "page": item.get(
                        "page"
                    ),
                    "section": item.get(
                        "section"
                    ),
                    "score": item.get(
                        "score"
                    ),
                }
            )

        if not answer_parts:
            return {
                "status": "not_found",
                "answer": (
                    "I couldn't find this information "
                    "in the provided documents."
                ),
                "sources": [],
            }

        return {
            "status": status,
            "answer": "\n".join(
                answer_parts
            ),
            "sources": sources,
        }

    # --------------------------------------------------
    # NORMAL FACTUAL ANSWER
    # --------------------------------------------------

    primary = evidence[0]

    answer = str(
        primary.get(
            "text",
            "",
        )
    ).strip()

    source = {
        "document": primary.get(
            "document"
        ),
        "page": primary.get(
            "page"
        ),
        "section": primary.get(
            "section"
        ),
        "score": primary.get(
            "score"
        ),
    }

    return {
        "status": status,
        "answer": answer,
        "sources": [source],
    }