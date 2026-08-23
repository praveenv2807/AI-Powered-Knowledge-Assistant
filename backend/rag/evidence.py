import re
from typing import Literal


EvidenceStatus = Literal[
    "verified",
    "partial",
    "not_found"
]


STOP_WORDS = {
    "what",
    "what's",
    "which",
    "who",
    "where",
    "when",
    "why",
    "how",
    "is",
    "are",
    "was",
    "were",
    "the",
    "a",
    "an",
    "of",
    "on",
    "in",
    "to",
    "for",
    "and",
    "or",
    "do",
    "does",
    "did",
    "can",
    "could",
    "would",
    "should",
    "there",
    "their",
    "this",
    "that",
    "available"
}


def extract_keywords(text: str) -> set[str]:
    """
    Extract meaningful words from a question.
    """

    words = re.findall(r"[a-zA-Z]+", text.lower())

    return {
        word
        for word in words
        if word not in STOP_WORDS and len(word) > 2
    }


def keyword_overlap(question: str, evidence_text: str) -> float:
    """
    Calculate how many important question words
    appear in the retrieved evidence.
    """

    question_keywords = extract_keywords(question)

    if not question_keywords:
        return 0.0

    evidence_words = set(
        re.findall(r"[a-zA-Z]+", evidence_text.lower())
    )

    matched = question_keywords.intersection(evidence_words)

    return len(matched) / len(question_keywords)


def assess_evidence(
    question: str,
    results: list[dict],
    strong_threshold: float = 0.50,
    weak_threshold: float = 0.30
) -> dict:
    """
    Validate retrieved evidence using both:
    1. Semantic similarity score
    2. Keyword overlap with the question

    Returns:
        verified
        partial
        not_found
    """

    if not results:
        return {
            "status": "not_found",
            "evidence": []
        }

    evaluated = []

    for result in results:
        text = result.get("text", "")

        score = result.get("score", 0.0)

        overlap = keyword_overlap(
            question,
            text
        )

        evaluated.append(
            {
                **result,
                "keyword_overlap": overlap
            }
        )

    strong_results = [
        result
        for result in evaluated
        if (
            result["score"] >= strong_threshold
            and result["keyword_overlap"] >= 0.50
        )
    ]

    partial_results = [
        result
        for result in evaluated
        if (
            result["score"] >= weak_threshold
            and result["keyword_overlap"] >= 0.30
        )
    ]

    if strong_results:
        return {
            "status": "verified",
            "evidence": strong_results
        }

    if partial_results:
        return {
            "status": "partial",
            "evidence": partial_results
        }

    return {
        "status": "not_found",
        "evidence": []
    }