import re

import faiss
import numpy as np

from .embeddings import generate_embeddings


class VectorRetriever:
    """
    Hybrid document retriever.

    Retrieval strategy:
        1. Semantic retrieval using FAISS
        2. Lexical retrieval using term overlap
        3. Reciprocal-style score fusion
        4. Return reranked evidence

    The returned `score` remains a semantic score so that
    the existing K-GUARD evidence-quality layer can continue
    working with the retrieved evidence.
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

    def __init__(self):
        self.index = None
        self.chunks = []
        self.embeddings = None

    # --------------------------------------------------
    # INDEX BUILDING
    # --------------------------------------------------

    def build_index(self, chunks: list[dict]):
        """
        Create a FAISS semantic index from document chunks.
        """

        if not chunks:
            raise ValueError(
                "Cannot build an index with no chunks."
            )

        texts = [
            chunk["text"]
            for chunk in chunks
        ]

        embeddings = generate_embeddings(texts)

        embeddings = np.asarray(
            embeddings,
            dtype="float32",
        )

        if embeddings.ndim != 2:
            raise ValueError(
                "Embeddings must be a 2D matrix."
            )

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(
            dimension
        )

        self.index.add(embeddings)

        self.embeddings = embeddings
        self.chunks = chunks

    # --------------------------------------------------
    # SEARCH
    # --------------------------------------------------

    def search(
        self,
        question: str,
        top_k: int = 5,
    ) -> list[dict]:
        """
        Perform hybrid retrieval.

        Semantic similarity:
            FAISS cosine-style inner product

        Lexical similarity:
            meaningful query-term overlap

        Final ranking:
            weighted semantic + lexical score
        """

        if self.index is None:
            raise RuntimeError(
                "FAISS index has not been built yet."
            )

        if not question.strip():
            return []

        if not self.chunks:
            return []

        actual_k = min(
            max(top_k * 2, top_k),
            len(self.chunks),
        )

        # --------------------------------------------------
        # 1. Semantic retrieval
        # --------------------------------------------------

        question_embedding = generate_embeddings(
            [question]
        )

        question_embedding = np.asarray(
            question_embedding,
            dtype="float32",
        )

        semantic_scores, indices = (
            self.index.search(
                question_embedding,
                actual_k,
            )
        )

        semantic_results = {}

        for score, index in zip(
            semantic_scores[0],
            indices[0],
        ):

            if index < 0:
                continue

            semantic_results[int(index)] = float(
                score
            )

        # --------------------------------------------------
        # 2. Lexical retrieval
        # --------------------------------------------------

        question_terms = self._extract_terms(
            question
        )

        lexical_scores = {}

        for index, chunk in enumerate(
            self.chunks
        ):

            text = chunk.get(
                "text",
                "",
            )

            text_terms = self._extract_terms(
                text
            )

            if not question_terms:
                lexical_score = 0.0
            else:
                matches = question_terms.intersection(
                    text_terms
                )

                lexical_score = (
                    len(matches)
                    / len(question_terms)
                )

            lexical_scores[index] = lexical_score

        # --------------------------------------------------
        # 3. Candidate pool
        # --------------------------------------------------

        candidates = set(
            semantic_results.keys()
        )

        # Add lexically strong chunks even if their
        # semantic rank was lower.
        lexical_candidates = sorted(
            lexical_scores,
            key=lexical_scores.get,
            reverse=True,
        )[:actual_k]

        candidates.update(
            lexical_candidates
        )

        # --------------------------------------------------
        # 4. Score fusion
        # --------------------------------------------------

        ranked = []

        for index in candidates:

            semantic_score = semantic_results.get(
                index,
                0.0,
            )

            lexical_score = lexical_scores.get(
                index,
                0.0,
            )

            # Semantic retrieval remains dominant.
            fused_score = (
                semantic_score * 0.75
                + lexical_score * 0.25
            )

            chunk = self.chunks[index].copy()

            chunk["score"] = float(
                semantic_score
            )

            chunk["semantic_score"] = round(
                semantic_score,
                3,
            )

            chunk["lexical_score"] = round(
                lexical_score,
                3,
            )

            chunk["retrieval_score"] = round(
                fused_score,
                3,
            )

            ranked.append(
                chunk
            )

        # --------------------------------------------------
        # 5. Final reranking
        # --------------------------------------------------

        ranked.sort(
            key=lambda item: item[
                "retrieval_score"
            ],
            reverse=True,
        )

        return ranked[:top_k]

    # --------------------------------------------------
    # TERM EXTRACTION
    # --------------------------------------------------

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