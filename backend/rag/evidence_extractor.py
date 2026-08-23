import re
from typing import Any

from .query_intent import QueryIntentDetector


class EvidenceExtractor:
    """
    K-GUARD Evidence Intelligence Extractor.

    Extracts the strongest evidence from retrieved document chunks.

    Features:
        - query intent awareness
        - lexical overlap
        - retrieval confidence
        - keyword proximity
        - temporal signals
        - numeric signals
        - list detection
        - section alignment
        - heading detection
        - structured numbered-list preservation

    The extractor is deterministic and does not use an LLM.
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
        "would",
        "should",
        "please",
        "available",
    }

    LIST_TERMS = {
        "facilities",
        "facility",
        "campus",
        "amenities",
        "services",
        "features",
        "resources",
        "playground",
        "gymnasium",
        "canteen",
        "health",
        "library",
        "hostel",
        "transport",
        "auditorium",
        "laboratory",
        "alumni",
    }

    def __init__(
        self,
        max_evidence: int = 2,
        minimum_score: float = 0.20,
    ):
        self.max_evidence = max_evidence
        self.minimum_score = minimum_score
        self.intent_detector = QueryIntentDetector()

    def extract(
        self,
        question: str,
        results: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Extract the strongest evidence supporting the question.
        """

        if not question.strip() or not results:
            return []

        intent = self.intent_detector.detect(question)

        question_terms = self._extract_terms(question)

        candidates = []

        for result in results:

            text = str(
                result.get("text", "")
            ).strip()

            if not text:
                continue

            retrieval_score = float(
                result.get("score", 0.0)
            )

            section = str(
                result.get("section", "")
            )

            # --------------------------------------------------
            # LIST INTENT
            #
            # For list questions, preserve the structured list
            # instead of splitting every item into sentences.
            # --------------------------------------------------

            if intent == "list":

                structured_unit = self._extract_structured_list(
                    text
                )

                if structured_unit:

                    candidate = self._score_unit(
                        question=question,
                        question_terms=question_terms,
                        unit=structured_unit,
                        result=result,
                        section=section,
                        retrieval_score=retrieval_score,
                        intent=intent,
                        position=0,
                    )

                    if candidate is not None:
                        candidates.append(candidate)

                        # The complete structured list is better
                        # evidence than individual list fragments.
                        continue

            # --------------------------------------------------
            # NORMAL EVIDENCE EXTRACTION
            # --------------------------------------------------

            units = self._split_evidence_units(text)

            for position, unit in enumerate(units):

                candidate = self._score_unit(
                    question=question,
                    question_terms=question_terms,
                    unit=unit,
                    result=result,
                    section=section,
                    retrieval_score=retrieval_score,
                    intent=intent,
                    position=position,
                )

                if candidate is not None:
                    candidates.append(candidate)

        if not candidates:
            return []

        # --------------------------------------------------
        # Rank evidence
        # --------------------------------------------------

        candidates.sort(
            key=lambda item: (
                item["score"],
                item["lexical_score"],
                item["retrieval_score"],
            ),
            reverse=True,
        )

        # --------------------------------------------------
        # Remove duplicates
        # --------------------------------------------------

        selected = []
        seen = set()

        for candidate in candidates:

            normalized = self._normalize(
                candidate["text"]
            )

            if normalized in seen:
                continue

            seen.add(normalized)

            selected.append(candidate)

            if len(selected) >= self.max_evidence:
                break

        return selected

    # ======================================================
    # Candidate scoring
    # ======================================================

    def _score_unit(
        self,
        question: str,
        question_terms: set[str],
        unit: str,
        result: dict[str, Any],
        section: str,
        retrieval_score: float,
        intent: str,
        position: int,
    ) -> dict[str, Any] | None:

        unit = unit.strip()

        if len(unit) < 15:
            return None

        unit_terms = self._extract_terms(unit)

        # --------------------------------------------------
        # Lexical score
        # --------------------------------------------------

        if question_terms:

            matched_terms = (
                question_terms.intersection(
                    unit_terms
                )
            )

            lexical_score = (
                len(matched_terms)
                / len(question_terms)
            )

        else:

            matched_terms = set()
            lexical_score = 0.0

        # --------------------------------------------------
        # Base score
        # --------------------------------------------------

        evidence_score = (
            lexical_score * 0.45
            + retrieval_score * 0.25
        )

        # --------------------------------------------------
        # Proximity
        # --------------------------------------------------

        evidence_score += self._proximity_bonus(
            question_terms,
            unit,
        )

        # --------------------------------------------------
        # Intent bonus
        # --------------------------------------------------

        evidence_score += self._intent_bonus(
            intent,
            unit,
            section,
        )

        # --------------------------------------------------
        # Section relevance
        # --------------------------------------------------

        evidence_score += self._section_bonus(
            intent,
            question_terms,
            section,
        )

        # --------------------------------------------------
        # List-specific bonus
        #
        # A complete structured list should receive a strong
        # bonus when the query asks for facilities/resources.
        # --------------------------------------------------

        if intent == "list":

            list_score = self._list_quality_score(
                unit,
                section,
            )

            evidence_score += list_score

        # --------------------------------------------------
        # Heading detection
        # --------------------------------------------------

        heading_penalty = self._heading_penalty(
            unit
        )

        # Never return a standalone heading.
        if heading_penalty >= 0.25:
            return None

        evidence_score -= heading_penalty

        evidence_score = max(
            0.0,
            min(
                evidence_score,
                1.0,
            ),
        )

        if evidence_score < self.minimum_score:
            return None

        return {
            "text": unit,
            "document": result.get(
                "document"
            ),
            "page": result.get(
                "page"
            ),
            "section": section,
            "score": round(
                evidence_score,
                3,
            ),
            "retrieval_score": round(
                retrieval_score,
                3,
            ),
            "lexical_score": round(
                lexical_score,
                3,
            ),
            "intent": intent,
            "matched_terms": sorted(
                matched_terms
            ),
            "position": position,
        }

    # ======================================================
    # Structured list extraction
    # ======================================================

    def _extract_structured_list(
        self,
        text: str,
    ) -> str | None:
        """
        Detect a numbered structured list.

        Example:

            5 Other Facilities on the Campus:
            1. Playground: ...
            2. State-of-the-Art Gymnasium: ...
            3. Canteen: ...
            4. Health: ...
            5. Vibrant Alumni: ...

        Returns the complete list as one evidence unit.

        This prevents the extractor from selecting only one
        arbitrary facility.
        """

        normalized = re.sub(
            r"\s+",
            " ",
            text,
        ).strip()

        if not normalized:
            return None

        # Must contain at least two numbered items.
        matches = list(
            re.finditer(
                r"(?:^|\s)(\d+)\.\s+",
                normalized,
            )
        )

        if len(matches) < 2:
            return None

        # Find a likely list heading.
        heading_match = re.search(
            r"\b(?:other\s+)?facilities\b"
            r"[^:]{0,80}:",
            normalized,
            re.IGNORECASE,
        )

        if not heading_match:
            return None

        start = heading_match.start()

        list_text = normalized[start:].strip()

        # Make sure the result actually contains several
        # meaningful numbered entries.
        item_matches = list(
            re.finditer(
                r"(?:^|\s)(\d+)\.\s+([A-Z][^:]{0,100}):",
                list_text,
            )
        )

        if len(item_matches) < 2:
            return None

        return list_text

    # ======================================================
    # Evidence splitting
    # ======================================================

    def _split_evidence_units(
        self,
        text: str,
    ) -> list[str]:

        text = re.sub(
            r"\s+",
            " ",
            text,
        ).strip()

        if not text:
            return []

        # --------------------------------------------------
        # Preserve numbered list items.
        # --------------------------------------------------

        numbered_parts = re.split(
            r"(?=\b\d+\.\s+[A-Z])",
            text,
        )

        units = []

        for part in numbered_parts:

            part = part.strip()

            if not part:
                continue

            sentences = re.split(
                r"(?<=[.!?])\s+",
                part,
            )

            for sentence in sentences:

                sentence = sentence.strip()

                if len(sentence) < 15:
                    continue

                units.append(sentence)

        return units

    # ======================================================
    # Intent scoring
    # ======================================================

    def _intent_bonus(
        self,
        intent: str,
        text: str,
        section: str,
    ) -> float:

        normalized = text.lower()
        normalized_section = section.lower()

        # --------------------------------------------------
        # Temporal
        # --------------------------------------------------

        if intent == "temporal":

            if self._contains_year(text):
                return 0.35

            if self._contains_date(text):
                return 0.30

            temporal_words = {
                "established",
                "founded",
                "started",
                "opened",
                "created",
                "launched",
                "introduced",
            }

            if any(
                word in normalized
                for word in temporal_words
            ):
                return 0.15

            return 0.0

        # --------------------------------------------------
        # Numeric
        # --------------------------------------------------

        if intent == "numeric":

            if self._contains_number(text):
                return 0.30

            return 0.0

        # --------------------------------------------------
        # List
        # --------------------------------------------------

        if intent == "list":

            score = 0.0

            # Actual numbered facility item.
            if re.search(
                r"^\d+\.\s*",
                text,
            ):
                score += 0.40

            facility_terms = {
                "playground",
                "gymnasium",
                "canteen",
                "dispensary",
                "health",
                "library",
                "hostel",
                "auditorium",
                "laboratory",
                "transport",
                "alumni",
            }

            matches = sum(
                1
                for term in facility_terms
                if term in normalized
            )

            if matches >= 4:
                score += 0.30

            elif matches >= 2:
                score += 0.20

            elif matches == 1:
                score += 0.12

            # Dedicated facilities section.
            if (
                "facilities" in normalized_section
                or "other facilities" in normalized_section
            ):
                score += 0.20

            return score

        # --------------------------------------------------
        # Definition
        # --------------------------------------------------

        if intent == "definition":

            definition_patterns = [
                "refers to",
                "is a",
                "is an",
                "means",
                "defined as",
                "purpose",
                "role",
                "function",
                "responsible for",
                "helps",
                "provides",
                "designed to",
                "used for",
            ]

            if any(
                pattern in normalized
                for pattern in definition_patterns
            ):
                return 0.20

            return 0.0

        return 0.0

    # ======================================================
    # List quality
    # ======================================================

    def _list_quality_score(
        self,
        text: str,
        section: str,
    ) -> float:
        """
        Score how strongly a candidate represents a complete
        list rather than an isolated sentence.
        """

        normalized = text.lower()

        numbered_items = len(
            re.findall(
                r"(?:^|\s)\d+\.\s+",
                text,
            )
        )

        facility_matches = sum(
            1
            for term in self.LIST_TERMS
            if term in normalized
        )

        score = 0.0

        if numbered_items >= 5:
            score += 0.20
        elif numbered_items >= 3:
            score += 0.15
        elif numbered_items >= 2:
            score += 0.10

        if facility_matches >= 4:
            score += 0.15
        elif facility_matches >= 2:
            score += 0.10

        if (
            "facilities" in normalized
            or "other facilities" in normalized
        ):
            score += 0.10

        return score

    # ======================================================
    # Section bonus
    # ======================================================

    def _section_bonus(
        self,
        intent: str,
        question_terms: set[str],
        section: str,
    ) -> float:

        if not section:
            return 0.0

        section_terms = self._extract_terms(
            section
        )

        if not question_terms:
            return 0.0

        matches = (
            question_terms.intersection(
                section_terms
            )
        )

        overlap = (
            len(matches)
            / len(question_terms)
        )

        if intent == "list":

            section_lower = section.lower()

            if (
                "facilities" in section_lower
                or "other facilities" in section_lower
            ):
                return 0.25

        if overlap >= 0.50:
            return 0.05

        return 0.0

    # ======================================================
    # Heading detection
    # ======================================================

    def _heading_penalty(
        self,
        text: str,
    ) -> float:

        stripped = text.strip()

        words = stripped.split()

        # Short heading-like fragments.
        if len(words) <= 8:

            if re.match(
                r"^\d+\.\s*",
                stripped,
            ):
                return 0.0

            if not re.search(
                r"[.!?]",
                stripped,
            ):
                return 0.25

        # Numbered section heading.
        if re.match(
            r"^\d+\s+[A-Z][^:]{0,70}:$",
            stripped,
        ):
            return 0.25

        # Normal heading ending in colon.
        if re.match(
            r"^[A-Z][A-Za-z\s-]{2,60}:$",
            stripped,
        ):
            return 0.25

        return 0.0

    # ======================================================
    # Number detection
    # ======================================================

    def _contains_number(
        self,
        text: str,
    ) -> bool:

        if re.search(
            r"\b\d+(?:,\d{3})*(?:\.\d+)?\b",
            text,
        ):
            return True

        number_words = {
            "zero",
            "one",
            "two",
            "three",
            "four",
            "five",
            "six",
            "seven",
            "eight",
            "nine",
            "ten",
            "hundred",
            "thousand",
            "million",
            "crore",
            "lakh",
        }

        terms = self._extract_terms(text)

        return bool(
            terms.intersection(
                number_words
            )
        )

    # ======================================================
    # Year detection
    # ======================================================

    def _contains_year(
        self,
        text: str,
    ) -> bool:

        return bool(
            re.search(
                r"\b(?:18|19|20)\d{2}\b",
                text,
            )
        )

    # ======================================================
    # Date detection
    # ======================================================

    def _contains_date(
        self,
        text: str,
    ) -> bool:

        patterns = [
            r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
            r"\b\d{1,2}\s+"
            r"(?:January|February|March|April|May|June|July|"
            r"August|September|October|November|December)"
            r"\s+\d{4}\b",
        ]

        return any(
            re.search(
                pattern,
                text,
                re.IGNORECASE,
            )
            for pattern in patterns
        )

    # ======================================================
    # Proximity
    # ======================================================

    def _proximity_bonus(
        self,
        question_terms: set[str],
        text: str,
    ) -> float:

        if not question_terms:
            return 0.0

        words = re.findall(
            r"\b[a-zA-Z0-9]+\b",
            text.lower(),
        )

        positions = []

        for index, word in enumerate(words):

            if word in question_terms:
                positions.append(index)

        if len(positions) < 2:
            return 0.0

        distance = (
            max(positions)
            - min(positions)
        )

        if distance <= 8:
            return 0.08

        if distance <= 15:
            return 0.04

        return 0.0

    # ======================================================
    # Term extraction
    # ======================================================

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

    # ======================================================
    # Normalization
    # ======================================================

    def _normalize(
        self,
        text: str,
    ) -> str:

        return re.sub(
            r"\s+",
            " ",
            text.lower().strip(),
        )