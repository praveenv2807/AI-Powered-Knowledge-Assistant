import re
from typing import Literal


QueryIntent = Literal[
    "temporal",
    "numeric",
    "list",
    "definition",
    "general",
]


class QueryIntentDetector:
    """
    Detects what type of evidence is required to answer
    a user's question.

    K-GUARD uses this information to prioritize evidence
    that actually answers the question instead of evidence
    that is merely semantically similar.

    Supported intents:
        temporal
        numeric
        list
        definition
        general
    """

    # --------------------------------------------------
    # Temporal questions
    # --------------------------------------------------

    TEMPORAL_TERMS = {
        "when",
        "established",
        "founded",
        "started",
        "created",
        "introduced",
        "launched",
        "opened",
        "year",
        "date",
        "history",
    }

    # --------------------------------------------------
    # Numeric / quantity questions
    # --------------------------------------------------

    NUMERIC_TERMS = {
        "how many",
        "how much",
        "number",
        "count",
        "strength",
        "population",
        "total",
        "capacity",
        "percentage",
        "percent",
        "marks",
        "score",
        "amount",
        "size",
        "duration",
        "years",
        "students",
        "staff",
        "lecturers",
    }

    # --------------------------------------------------
    # List / collection questions
    # --------------------------------------------------

    LIST_TERMS = {
        "what facilities",
        "facilities",
        "features",
        "services",
        "types",
        "kinds",
        "departments",
        "courses",
        "programs",
        "options",
        "available",
        "list",
        "amenities",
        "resources",
        "components",
        "items",
    }

    # --------------------------------------------------
    # Definition / explanation questions
    # --------------------------------------------------

    DEFINITION_TERMS = {
        "what is",
        "what are",
        "define",
        "meaning",
        "explain",
        "describe",
        "purpose",
        "role",
        "function",
        "significance",
    }

    # --------------------------------------------------
    # Sensitive / credential-like questions
    #
    # These should NOT be classified as definitions simply
    # because they begin with "what is".
    # --------------------------------------------------

    PASSWORD_TERMS = {
        "password",
        "wifi",
        "wi-fi",
        "passcode",
        "credentials",
        "login",
        "username",
        "access code",
        "security code",
    }

    def detect(
        self,
        question: str,
    ) -> QueryIntent:
        """
        Detect the evidence type required by a question.

        Priority matters.

        For example:

            "What is the Wi-Fi password?"

        contains "what is", but it is not a definition
        question. Credential-related terms therefore get
        checked before definition terms.
        """

        normalized = question.lower().strip()

        if not normalized:
            return "general"

        # --------------------------------------------------
        # 1. Credential / password questions
        # --------------------------------------------------

        if self._contains_any(
            normalized,
            self.PASSWORD_TERMS,
        ):
            return "general"

        # --------------------------------------------------
        # 2. Temporal questions
        # --------------------------------------------------

        if self._contains_any(
            normalized,
            self.TEMPORAL_TERMS,
        ):
            return "temporal"

        # --------------------------------------------------
        # 3. Numeric questions
        # --------------------------------------------------

        if self._contains_phrase(
            normalized,
            "how many",
        ) or self._contains_phrase(
            normalized,
            "how much",
        ):
            return "numeric"

        if self._contains_any(
            normalized,
            self.NUMERIC_TERMS,
        ):
            return "numeric"

        # --------------------------------------------------
        # 4. List / collection questions
        # --------------------------------------------------

        if self._contains_any(
            normalized,
            self.LIST_TERMS,
        ):
            return "list"

        # --------------------------------------------------
        # 5. Definition / explanation questions
        # --------------------------------------------------

        if self._contains_any(
            normalized,
            self.DEFINITION_TERMS,
        ):
            return "definition"

        # --------------------------------------------------
        # 6. Default
        # --------------------------------------------------

        return "general"

    def _contains_any(
        self,
        text: str,
        terms: set[str],
    ) -> bool:
        """
        Check whether the text contains at least one
        complete word or phrase from the provided terms.
        """

        for term in terms:

            if " " in term:
                if term in text:
                    return True

            else:

                if re.search(
                    rf"\b{re.escape(term)}\b",
                    text,
                ):
                    return True

        return False

    def _contains_phrase(
        self,
        text: str,
        phrase: str,
    ) -> bool:
        """
        Check for an exact phrase.
        """

        return phrase.lower() in text