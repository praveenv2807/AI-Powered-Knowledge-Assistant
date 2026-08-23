import faiss
import numpy as np

from .embeddings import generate_embeddings


class VectorRetriever:
    """
    Stores document chunk embeddings in FAISS
    and retrieves the most relevant chunks for a question.
    """

    def __init__(self):
        self.index = None
        self.chunks = []

    def build_index(self, chunks: list[dict]):
        """
        Create a FAISS index from document chunks.
        """

        if not chunks:
            raise ValueError("Cannot build an index with no chunks.")

        texts = [chunk["text"] for chunk in chunks]

        embeddings = generate_embeddings(texts)

        embeddings = np.asarray(embeddings, dtype="float32")

        dimension = embeddings.shape[1]

        # Inner product works well with normalized embeddings.
        self.index = faiss.IndexFlatIP(dimension)

        self.index.add(embeddings)

        self.chunks = chunks

    def search(self, question: str, top_k: int = 5) -> list[dict]:
        """
        Retrieve the most relevant chunks for a question.
        """

        if self.index is None:
            raise RuntimeError("FAISS index has not been built yet.")

        if not question.strip():
            return []

        question_embedding = generate_embeddings([question])

        question_embedding = np.asarray(
            question_embedding,
            dtype="float32"
        )

        actual_k = min(top_k, len(self.chunks))

        scores, indices = self.index.search(
            question_embedding,
            actual_k
        )

        results = []

        for score, index in zip(scores[0], indices[0]):
            if index < 0:
                continue

            chunk = self.chunks[index].copy()

            chunk["score"] = float(score)

            results.append(chunk)

        return results