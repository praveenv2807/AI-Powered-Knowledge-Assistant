from pathlib import Path

from .ingest import extract_pdf
from .chunker import create_chunks
from .retriever import VectorRetriever
from .evidence import assess_evidence
from .generator import generate_answer
from .evaluator import ReliabilityEvaluator
from .reliability import ReliabilityReport


class KnowledgePipeline:
    """
    Complete document-question answering pipeline.

    Flow:
        documents
        -> ingestion
        -> chunking
        -> embeddings + FAISS
        -> K-GUARD reliability evaluation
        -> evidence validation
        -> grounded answer / safe refusal
    """

    def __init__(self):
        self.retriever = VectorRetriever()
        self.evaluator = ReliabilityEvaluator()

        self.reliability_report = ReliabilityReport(
            self.evaluator
        )

        self.chunks = []
        self.documents_loaded = False

    def load_documents(
        self,
        document_paths: list[str],
    ):
        """
        Load and index the provided PDF documents.
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
            raise ValueError(
                "No text could be extracted from documents."
            )

        self.chunks = create_chunks(all_pages)

        if not self.chunks:
            raise ValueError(
                "No chunks were created from documents."
            )

        self.retriever.build_index(self.chunks)

        self.documents_loaded = True

        return {
            "documents": len(document_paths),
            "pages": len(all_pages),
            "chunks": len(self.chunks),
        }

    def answer_question(
        self,
        question: str,
        top_k: int = 5,
    ) -> dict:
        """
        Answer a question using only the loaded documents.

        K-GUARD evaluates evidence before generation.
        If evidence is insufficient, the system refuses
        to answer instead of guessing.
        """

        if not self.documents_loaded:
            raise RuntimeError(
                "No documents have been loaded yet."
            )

        if not question.strip():
            return {
                "status": "not_found",
                "answer": "Please enter a question.",
                "sources": [],
            }

        # --------------------------------------------------
        # 1. Retrieve candidate evidence
        # --------------------------------------------------

        results = self.retriever.search(
            question,
            top_k=top_k,
        )

        # --------------------------------------------------
        # 2. K-GUARD reliability evaluation
        # --------------------------------------------------

        evaluation = self.evaluator.evaluate(
            results,
            question,
        )

        reliability = {
            "status": evaluation.status,
            "confidence": evaluation.confidence,
            "confidence_percent": round(
                evaluation.confidence * 100,
                1,
            ),
            "evidence_count": evaluation.evidence_count,
            "reason": evaluation.reason,
        }

        # --------------------------------------------------
        # 3. Safe refusal
        # --------------------------------------------------

        if evaluation.status == "not_found":
            return {
                "status": "not_found",
                "answer": (
                    "I couldn't find this information "
                    "in the provided documents."
                ),
                "sources": [],
                "reliability": reliability,
            }

        # --------------------------------------------------
        # 4. Keep only evidence accepted by K-GUARD
        # --------------------------------------------------

        accepted_results = []

        for result in results:
            quality = self.evaluator.quality_scorer.score(
                question,
                result,
            )

            if (
                quality["combined_score"]
                >= self.evaluator.minimum_score
            ):
                enriched_result = {
                    **result,
                    "score": quality["combined_score"],
                    "semantic_score": quality["semantic_score"],
                    "lexical_score": quality["lexical_score"],
                    "matched_terms": quality["matched_terms"],
                }

                accepted_results.append(
                    enriched_result
                )

        # --------------------------------------------------
        # 5. Validate accepted evidence
        # --------------------------------------------------

        evidence = assess_evidence(
            question,
            accepted_results,
            minimum_score=self.evaluator.minimum_score,
        )

        # --------------------------------------------------
        # 6. Generate grounded answer
        # --------------------------------------------------

        response = generate_answer(
            question,
            evidence,
        )

        # --------------------------------------------------
        # 7. K-GUARD remains the final authority
        # --------------------------------------------------

        response["status"] = evaluation.status
        response["reliability"] = reliability

        return response