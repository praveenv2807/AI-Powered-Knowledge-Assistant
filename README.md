# CLARITY RAG 

### Evidence-First Document Intelligence

PROOFLY AI is an AI-powered knowledge assistant that answers questions using only information found in user-provided documents.

Instead of guessing when information is missing, PROOFLY AI retrieves relevant evidence, evaluates its reliability, and clearly indicates when the available documents do not support an answer.

---

## Problem

Traditional AI chatbots can generate confident answers even when the required information is not present in the provided knowledge base.

This creates a major problem for document-based systems:

- Unsupported answers can appear trustworthy
- Sources may not be visible
- Important evidence can be missed
- Users cannot easily verify where an answer came from

PROOFLY AI addresses this by making evidence the foundation of every response.

---

## Solution

PROOFLY AI follows an evidence-first workflow:

```text
User Documents
      ↓
Document Ingestion
      ↓
Text & Page Extraction
      ↓
Chunking
      ↓
Semantic + Keyword Retrieval
      ↓
Evidence Extraction
      ↓
Evidence Quality Validation
      ↓
Reliability Evaluation
      ↓
Grounded Response
      ↓
Answer + Sources + Evidence

If sufficient evidence cannot be found, the system refuses to guess.

Key Features
Multi-Document Knowledge Base

Upload supported documents and build a temporary knowledge base from their contents.

Supported formats include:

PDF
DOCX
TXT
Markdown
HTML
Hybrid Retrieval

PROOFLY AI combines semantic retrieval with lexical/keyword matching to improve evidence discovery.

Evidence-First Answers

Answers are generated from retrieved evidence rather than unsupported assumptions.

Reliability Classification

Responses can be classified as:

VERIFIED
PARTIAL / PARTIALLY SUPPORTED
NOT FOUND
Source Traceability

Responses provide source information such as:

Document name
Page
Section
Retrieval score
Evidence Display

Relevant passages are shown alongside answers so users can verify the response.

Refusal to Guess

If the knowledge base does not contain sufficient evidence, PROOFLY AI responds that the information could not be found instead of inventing an answer.

Reliability Test Suite

The interface provides test scenarios for:

Direct questions
Paraphrased questions
Cross-document questions
Unanswerable questions
Partial-evidence questions
System Architecture
                    ┌─────────────────────┐
                    │    React + Vite      │
                    │      Frontend        │
                    └──────────┬──────────┘
                               │
                         HTTP / REST API
                               │
                    ┌──────────▼──────────┐
                    │       FastAPI       │
                    │       Backend       │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Knowledge Pipeline │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
        Ingestion         Retrieval        Evidence
              │                │                │
              ▼                ▼                ▼
        PDF/DOCX/etc.    Semantic +       Quality &
                         Keyword Search    Reliability
                               │
                               ▼
                       Grounded Response
Technology Stack
Layer	Technology
Frontend	React
Build Tool	Vite
Backend	Python
API Framework	FastAPI
Document Processing	PyMuPDF / python-docx
Retrieval	Semantic + Keyword Retrieval
Embeddings	Sentence Transformers
AI / NLP	Transformer-based models
Communication	REST API
State	In-memory knowledge pipeline
API
Health Check
GET /

Example response:

{
  "status": "Backend running successfully"
}
Upload Documents
POST /api/upload

Multipart field:

files

The endpoint accepts multiple documents and adds them to the knowledge pipeline.

Ask a Question
POST /api/chat

Request:

{
  "question": "What information is available in the document?"
}

A response contains the answer, reliability information, sources, and evidence.

Example Response
{
  "status": "verified",
  "answer": "Answer supported by the provided document.",
  "sources": [
    {
      "document": "handbook.pdf",
      "page": 2,
      "section": "1"
    }
  ],
  "evidence": [],
  "reliability": {
    "status": "verified",
    "confidence": 0.81
  }
}
Reliability Model

PROOFLY AI does not treat retrieval alone as proof.

The system evaluates retrieved evidence using factors such as:

Semantic relevance
Lexical relevance
Query intent
Evidence quality
Retrieval confidence
Supporting evidence count

This allows the system to distinguish between strong evidence, partial evidence, and unsupported information.

Running Locally
1. Clone the repository
git clone <repository-url>
cd Cipher-pol-HS2026-045-
2. Start the backend

From the project root:

python -m uvicorn backend.main:app --reload --port 8000

The backend will run at:

http://127.0.0.1:8000
3. Start the frontend

Open another terminal:

cd frontend
npm install
npm run dev

The frontend will normally run at:

http://127.0.0.1:5173
Usage
Open PROOFLY AI.
Upload one or more supported documents.
Wait for the documents to be indexed.
Ask a natural-language question.
Review the answer.
Check the reliability status.
Inspect the cited sources and evidence.
If the information is unavailable, the system refuses to guess.
Reliability Test Examples
Direct Question
Ask a question whose answer is explicitly present
in the supplied document.

Expected:

VERIFIED
Paraphrased Question

Ask the same information using different wording.

Expected:

VERIFIED
Unanswerable Question

Ask for information that is not present in the documents.

Expected:

NOT FOUND

The system should not invent an answer.

Partial Evidence

Ask a question where the documents provide some relevant information but do not establish the complete claim.

Expected:

PARTIAL
Project Structure
Cipher-pol-HS2026-045-
│
├── backend/
│   ├── api/
│   │   ├── chat.py
│   │   ├── upload.py
│   │   └── deps.py
│   │
│   ├── rag/
│   │   ├── pipeline.py
│   │   ├── ingest.py
│   │   ├── chunker.py
│   │   ├── embeddings.py
│   │   ├── retriever.py
│   │   ├── evidence.py
│   │   ├── evidence_extractor.py
│   │   ├── evidence_quality.py
│   │   ├── reliability.py
│   │   ├── evaluator.py
│   │   └── benchmark.py
│   │
│   └── main.py
│
├── frontend/
│   ├── src/
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── app.jsx
│   │   └── main.jsx
│   │
│   ├── index.html
│   └── package.json
│
└── README.md
Design Philosophy

PROOFLY AI follows three principles:

1. Evidence Before Answers

The system first retrieves and evaluates evidence before producing an answer.

2. Traceability

Users should be able to understand where an answer came from.

3. Refuse Rather Than Guess

When the supplied knowledge base cannot support an answer, the system should clearly say so.

Why PROOFLY AI?

PROOFLY AI is designed for environments where correctness and traceability matter more than simply generating fluent responses.

The goal is not:

Generate an answer at any cost.

The goal is:

Generate an answer only when the available evidence supports it.

Project Status

PROOFLY AI is a working prototype demonstrating:

Multi-document ingestion
Hybrid retrieval
Evidence extraction
Evidence validation
Reliability evaluation
Source traceability
Grounded question answering
Unsupported-answer refusal
React/FastAPI integration
License

This project was developed as a hackathon project.

##This project is yet to finish.
### Put this into your README

Since you don't want a manual process, from the **project root** you can replace the README using VS Code:
