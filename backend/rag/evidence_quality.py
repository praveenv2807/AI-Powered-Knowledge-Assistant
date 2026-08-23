import re
from typing import Any


class EvidenceQualityScorer:
    """
    K-GUARD evidence quality scorer.

    Combines semantic similarity and lexical overlap,
    with a small topic/section boost when the retrieved
    section directly matches the question.
    """

    STOPWORDS = {
        "what",
        "when",
        "where",
        "who",
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
        "does",
        "do",
        "did",
        "can",
        "could",
        "please",
        "available",
    }

    def score(
        self,
        question: str,
        result: dict[str, Any],
    ) -> dict[str, Any]:

        text = result.get("text", "")
        section = str(result.get("section", ""))

        semantic_score = float(
            result.get("score", 0.0)
        )

        question_terms = self._extract_terms(question)
        text_terms = self._extract_terms(text)
        section_terms = self._extract_terms(section)

        # --------------------------------------------------
        # Lexical overlap
        # --------------------------------------------------

        if question_terms:

            text_matches = (
                question_terms.intersection(text_terms)
            )

            lexical_score = (
                len(text_matches)
                / len(question_terms)
            )

        else:

            text_matches = set()
            lexical_score = 0.0

        # --------------------------------------------------
        # Section/topic alignment
        # --------------------------------------------------

        if question_terms:

            section_matches = (
                question_terms.intersection(section_terms)
            )

            section_score = (
                len(section_matches)
                / len(question_terms)
            )

        else:

            section_matches = set()
            section_score = 0.0

        # --------------------------------------------------
        # Preserve the proven semantic/lexical weighting
        # --------------------------------------------------

        combined_score = (
            semantic_score * 0.65
            + lexical_score * 0.35
        )

        # --------------------------------------------------
        # Small topic boost
        #
        # Only add this when the section itself contains
        # at least half of the meaningful question terms.
        # --------------------------------------------------

        heading_boost = 0.0

        if section_score >= 0.50:
            heading_boost = 0.05

        combined_score = min(
            combined_score + heading_boost,
            1.0,
        )

        matched_terms = (
            text_matches.union(section_matches)
        )

        return {
            "semantic_score": round(
                semantic_score,
                3,
            ),
            "lexical_score": round(
                lexical_score,
                3,
            ),
            "section_score": round(
                section_score,
                3,
            ),
            "heading_boost": round(
                heading_boost,
                3,
            ),
            "combined_score": round(
                combined_score,
                3,
            ),
            "matched_terms": sorted(
                matched_terms
            ),
        }

    def _extract_terms(
        self,
        text: str,
    ) -> set[str]:

        words = re.findall(
            r"\b[a-zA-Z0-9]+\b",
            text.lower(),
        )

        return {
            word
            for word in words
            if word not in self.STOPWORDS
            and len(word) > 2
        }