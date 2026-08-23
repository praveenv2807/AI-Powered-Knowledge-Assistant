from pathlib import Path

from .ingest import extract_pdf
from .chunker import create_chunks
from .retriever import VectorRetriever
from .evidence import assess_evidence
from .generator import generate_answer


class KnowledgePipeline:
    """
    Complete document-question answering pipeline.

    Flow:
        documents
        -> ingestion
        -> chunking
        -> embeddings + FAISS
        -> retrieval
        -> evidence validation
        -> grounded answer
    """

    def __init__(self):
        self.retriever = VectorRetriever()
        self.chunks = []
        self.documents_loaded = False

    def load_documents(self, document_paths: list[str]):
        """
        Load and index the provided documents.
        """

        all_pages = []

        for document_path in document_paths:

            path = Path(document_path)

            if not path.exists():
                raise FileNotFoundError(
                    f"Document not found: {document_path}"
                )

            if path.suffix.lower() != ".pdf":
                raise ValueError(
                    f"Unsupported document type: {path.suffix}"
                )

            pages = extract_pdf(str(path))

            all_pages.extend(pages)

        if not all_pages:
            raise ValueError("No text could be extracted from documents.")

        self.chunks = create_chunks(all_pages)

        if not self.chunks:
            raise ValueError("No chunks were created from documents.")

        self.retriever.build_index(self.chunks)

        self.documents_loaded = True

        return {
            "documents": len(document_paths),
            "pages": len(all_pages),
            "chunks": len(self.chunks)
        }

    def answer_question(
        self,
        question: str,
        top_k: int = 5
    ) -> dict:
        """
        Answer a question using only the loaded documents.
        """

        if not self.documents_loaded:
            raise RuntimeError(
                "No documents have been loaded yet."
            )

        if not question.strip():
            return {
                "status": "not_found",
                "answer": "Please enter a question.",
                "sources": []
            }

        results = self.retriever.search(
            question,
            top_k=top_k
        )

        evidence = assess_evidence(
            question,
            results
        )

        response = generate_answer(
            question,
            evidence
        )

        return response