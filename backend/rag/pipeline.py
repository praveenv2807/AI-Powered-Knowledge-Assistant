from pathlib import Path

from .ingest import extract_document
from .chunker import create_chunks
from .retriever import VectorRetriever
from .evidence import assess_evidence
from .generator import generate_answer
from .evaluator import ReliabilityEvaluator
from .reliability import ReliabilityReport
from .evidence_extractor import EvidenceExtractor


class KnowledgePipeline:
    """
    Complete document-question answering pipeline.

    Supports a persistent multi-document knowledge base.

    Supported document formats:
        PDF
        DOCX
        TXT
        Markdown
        HTML

    Flow:
        documents
        -> ingestion
        -> chunking
        -> embeddings + FAISS
        -> hybrid retrieval
        -> K-GUARD reliability evaluation
        -> evidence quality validation
        -> exact evidence extraction
        -> grounded answer / safe refusal

    Multiple calls to load_documents() add new documents
    to the existing knowledge base instead of replacing it.
    """

    def __init__(self):
        self.retriever = VectorRetriever()

        self.evaluator = ReliabilityEvaluator()

        self.reliability_report = ReliabilityReport(
            self.evaluator
        )

        self.evidence_extractor = EvidenceExtractor()

        self.chunks = []

        self.loaded_documents = set()

        self.documents_loaded = False

    # --------------------------------------------------
    # DOCUMENT LOADING
    # --------------------------------------------------

    def load_documents(
        self,
        document_paths: list[str],
    ):
        """
        Add one or more documents to the existing
        knowledge base.

        Already-loaded documents are skipped.

        The FAISS index is rebuilt using all known
        chunks after new documents are added.
        """

        if not document_paths:
            raise ValueError(
                "No document paths were provided."
            )

        new_pages = []
        new_documents = []

        for document_path in document_paths:
            path = Path(document_path)

            if not path.exists():
                raise FileNotFoundError(
                    f"Document not found: {document_path}"
                )

            resolved_path = str(
                path.resolve()
            )

            # Avoid indexing the same file twice.
            if resolved_path in self.loaded_documents:
                continue

            pages = extract_document(
                str(path)
            )

            if pages:
                new_pages.extend(pages)

                new_documents.append(
                    resolved_path
                )

        if not new_pages:

            if self.documents_loaded:
                return {
                    "documents_added": 0,
                    "documents_total": len(
                        self.loaded_documents
                    ),
                    "pages_added": 0,
                    "pages_total": self._page_count(),
                    "chunks_added": 0,
                    "chunks_total": len(
                        self.chunks
                    ),
                }

            raise ValueError(
                "No text could be extracted from documents."
            )

        # --------------------------------------------------
        # Create chunks for new documents
        # --------------------------------------------------

        new_chunks = create_chunks(
            new_pages
        )

        if not new_chunks:
            raise ValueError(
                "No chunks were created from documents."
            )

        # --------------------------------------------------
        # Make chunk IDs globally unique
        # --------------------------------------------------

        existing_count = len(
            self.chunks
        )

        for index, chunk in enumerate(
            new_chunks,
            start=existing_count + 1,
        ):
            chunk["chunk_id"] = (
                f"chunk_{index}"
            )

        # --------------------------------------------------
        # Add new chunks to knowledge base
        # --------------------------------------------------

        self.chunks.extend(
            new_chunks
        )

        self.loaded_documents.update(
            new_documents
        )

        # --------------------------------------------------
        # Rebuild complete FAISS index
        # --------------------------------------------------

        self.retriever.build_index(
            self.chunks
        )

        self.documents_loaded = True

        return {
            "documents_added": len(
                new_documents
            ),
            "documents_total": len(
                self.loaded_documents
            ),
            "pages_added": len(
                new_pages
            ),
            "pages_total": self._page_count(),
            "chunks_added": len(
                new_chunks
            ),
            "chunks_total": len(
                self.chunks
            ),
        }

    # --------------------------------------------------
    # QUESTION ANSWERING
    # --------------------------------------------------

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
                "evidence": [],
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
                "evidence": [],
                "reliability": reliability,
            }

        # --------------------------------------------------
        # 4. Keep only K-GUARD accepted evidence
        # --------------------------------------------------

        accepted_results = []

        for result in results:

            quality = (
                self.evaluator.quality_scorer.score(
                    question,
                    result,
                )
            )

            if (
                quality["combined_score"]
                >= self.evaluator.minimum_score
            ):
                enriched_result = {
                    **result,
                    "score": quality[
                        "combined_score"
                    ],
                    "semantic_score": quality[
                        "semantic_score"
                    ],
                    "lexical_score": quality[
                        "lexical_score"
                    ],
                    "section_score": quality[
                        "section_score"
                    ],
                    "heading_boost": quality[
                        "heading_boost"
                    ],
                    "matched_terms": quality[
                        "matched_terms"
                    ],
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
            minimum_score=(
                self.evaluator.minimum_score
            ),
        )

        # --------------------------------------------------
        # 6. Extract exact supporting evidence
        # --------------------------------------------------

        exact_evidence = (
            self.evidence_extractor.extract(
                question,
                accepted_results,
            )
        )

        # --------------------------------------------------
        # 7. Generate grounded answer
        # --------------------------------------------------

        generation_evidence = {
            **evidence,
            "evidence": exact_evidence,
        }

        response = generate_answer(
            question,
            generation_evidence,
        )

        # --------------------------------------------------
        # 8. Attach evidence
        # --------------------------------------------------

        response["evidence"] = (
            exact_evidence
        )

        # --------------------------------------------------
        # 9. K-GUARD final authority
        # --------------------------------------------------

        response["status"] = (
            evaluation.status
        )

        response["reliability"] = (
            reliability
        )

        return response

    # --------------------------------------------------
    # KNOWLEDGE BASE INFORMATION
    # --------------------------------------------------

    def get_knowledge_base_stats(
        self,
    ) -> dict:
        """
        Return current knowledge-base statistics.
        """

        return {
            "documents": len(
                self.loaded_documents
            ),
            "pages": self._page_count(),
            "chunks": len(
                self.chunks
            ),
            "documents_loaded": (
                self.documents_loaded
            ),
        }

    def get_loaded_documents(
        self,
    ) -> list[str]:
        """
        Return loaded document paths.
        """

        return sorted(
            self.loaded_documents
        )

    # --------------------------------------------------
    # INTERNAL HELPERS
    # --------------------------------------------------

    def _page_count(self) -> int:
        """
        Count unique document/page combinations
        represented in the current chunks.
        """

        pages = set()

        for chunk in self.chunks:

            document = chunk.get(
                "document"
            )

            page = chunk.get(
                "page"
            )

            pages.add(
                (
                    document,
                    page,
                )
            )

        return len(pages)