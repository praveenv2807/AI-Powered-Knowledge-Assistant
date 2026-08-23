import React, { useState } from "react";
import { askQuestion, uploadDocuments } from "./services/api";

const RELIABILITY_TESTS = [
  {
    label: "Direct Query",
    q: "What is the minimum attendance requirement?",
    tag: "Exact",
  },
  {
    label: "Paraphrased",
    q: "How much attendance do I need before I can write the exam?",
    tag: "Semantic",
  },
  {
    label: "Cross-Doc",
    q: "Can a student with 70% attendance appear for the exam?",
    tag: "Multi-Ref",
  },
  {
    label: "Unanswerable",
    q: "What is the hostel Wi-Fi password?",
    tag: "Negative",
  },
  {
    label: "Partial Proof",
    q: "Does a medical condition allow attendance below the required percentage?",
    tag: "Edge Case",
  },
];

const ACCEPTED_TYPES =
  ".pdf,.docx,.txt,.html,.htm,.md,.markdown";

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [selectedSource, setSelectedSource] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [knowledgeStats, setKnowledgeStats] = useState(null);
  const [uploadError, setUploadError] = useState("");

  const handleSend = async (queryText) => {
    const q = queryText || input;

    if (!q.trim() || loading) return;

    const userMsg = {
      role: "user",
      text: q,
    };

    setMessages((prev) => [...prev, userMsg]);

    if (!queryText) {
      setInput("");
    }

    setLoading(true);

    try {
      const data = await askQuestion(q);

      const confidence =
        data?.reliability?.confidence ??
        null;

      const botMsg = {
        role: "bot",
        status: data?.status || "not_found",
        answer:
          data?.answer ||
          "I couldn't find this information in the provided documents.",
        confidence,
        confidencePercent:
          data?.reliability?.confidence_percent ?? null,
        reason:
          data?.reliability?.reason || "",
        sources: data?.sources || [],
        evidence: data?.evidence || [],
        reliability: data?.reliability || null,
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          status: "error",
          answer:
            "Unable to connect to the PROOFLY AI backend. Please make sure the API server is running.",
          sources: [],
          evidence: [],
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const selectedFiles = Array.from(e.target.files || []);

    if (selectedFiles.length === 0) return;

    setUploading(true);
    setUploadError("");

    try {
      const response = await uploadDocuments(selectedFiles);

      const newFiles = selectedFiles.map((file) => ({
        name: file.name,
        size: `${(file.size / 1024).toFixed(1)} KB`,
        timestamp: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
      }));

      setUploadedFiles((prev) => [...newFiles, ...prev]);

      if (response?.stats) {
        setKnowledgeStats(response.stats);
      }
    } catch (err) {
      setUploadError(
        err?.message || "Failed to upload documents."
      );
    } finally {
      setUploading(false);

      // Allows selecting the same file again later.
      e.target.value = "";
    }
  };

  const renderBadge = (status) => {
    switch (status) {
      case "verified":
        return (
          <span className="badge badge-verified">
            VERIFIED SOURCE
          </span>
        );

      case "partially_supported":
      case "partial":
        return (
          <span className="badge badge-partial">
            PARTIAL MATCH
          </span>
        );

      case "not_found":
        return (
          <span className="badge badge-notfound">
            NO EVIDENCE
          </span>
        );

      default:
        return (
          <span className="badge badge-notfound">
            ERROR
          </span>
        );
    }
  };

  return (
    <div className="peacock-root">
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

        * {
          box-sizing: border-box;
        }

        body {
          margin: 0;
        }

        .peacock-root {
          display: flex;
          height: 100vh;
          width: 100vw;
          font-family: 'Plus Jakarta Sans', sans-serif;
          background-color: #f5f2eb;
          color: #1a2e26;
          overflow: hidden;
        }

        .sidebar {
          width: 320px;
          flex-shrink: 0;
          background: #0f4c3a;
          color: #f5f2eb;
          padding: 24px 20px;
          display: flex;
          flex-direction: column;
          gap: 20px;
          border-right: 1px solid #0b382b;
          box-shadow: 4px 0 20px rgba(0, 0, 0, 0.08);
          overflow-y: auto;
        }

        .brand {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .brand-icon {
          width: 38px;
          height: 38px;
          background: #d4a359;
          border-radius: 10px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #0f4c3a;
          font-weight: 800;
          font-size: 1.1rem;
        }

        .brand-title {
          font-family: 'Playfair Display', serif;
          font-size: 1.3rem;
          font-weight: 700;
          color: #f5f2eb;
          margin: 0;
        }

        .upload-btn {
          display: block;
          width: 100%;
          padding: 12px;
          background: rgba(245, 242, 235, 0.08);
          border: 1px dashed rgba(212, 163, 89, 0.5);
          color: #f5f2eb;
          border-radius: 10px;
          text-align: center;
          cursor: pointer;
          font-size: 0.85rem;
          font-weight: 600;
          transition: all 0.2s ease;
        }

        .upload-btn:hover {
          background: rgba(212, 163, 89, 0.15);
          border-color: #d4a359;
        }

        .upload-btn.disabled {
          opacity: 0.6;
          cursor: wait;
        }

        .file-list {
          display: flex;
          flex-direction: column;
          gap: 8px;
          margin-top: 10px;
          max-height: 180px;
          overflow-y: auto;
        }

        .file-item {
          background: rgba(20, 89, 69, 0.7);
          border: 1px solid #1c6b54;
          padding: 10px 12px;
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 10px;
        }

        .file-info {
          display: flex;
          flex-direction: column;
          gap: 2px;
          overflow: hidden;
        }

        .file-name {
          font-size: 0.8rem;
          font-weight: 600;
          color: #f5f2eb;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
          max-width: 190px;
        }

        .file-meta {
          font-size: 0.68rem;
          color: #a8c5bb;
        }

        .file-status {
          font-size: 0.65rem;
          background: rgba(212, 163, 89, 0.2);
          color: #d4a359;
          padding: 2px 6px;
          border-radius: 4px;
          font-weight: 700;
        }

        .stats-box {
          margin-top: 10px;
          padding: 12px;
          border: 1px solid #1c6b54;
          background: rgba(20, 89, 69, 0.55);
          border-radius: 9px;
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 6px;
          text-align: center;
        }

        .stat-value {
          display: block;
          font-size: 1rem;
          font-weight: 700;
          color: #d4a359;
        }

        .stat-label {
          display: block;
          font-size: 0.58rem;
          color: #a8c5bb;
          text-transform: uppercase;
        }

        .upload-error {
          margin-top: 8px;
          padding: 8px;
          background: rgba(161, 35, 24, 0.15);
          border: 1px solid rgba(252, 219, 216, 0.35);
          border-radius: 7px;
          color: #ffd6d2;
          font-size: 0.7rem;
        }

        .test-card {
          background: #145945;
          border: 1px solid #1c6b54;
          padding: 10px 14px;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.2s ease;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .test-card:hover {
          background: #196f58;
          border-color: #d4a359;
          transform: translateX(3px);
        }

        .canvas {
          flex: 1;
          min-width: 0;
          display: flex;
          flex-direction: column;
          background: #f5f2eb;
        }

        .canvas-header {
          padding: 20px 32px;
          border-bottom: 1px solid #e2dbcd;
          background: #ede8dc;
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 20px;
        }

        .status-indicator {
          display: flex;
          align-items: center;
          gap: 7px;
          font-size: 0.72rem;
          color: #0f4c3a;
          font-weight: 700;
        }

        .status-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: #2c9b71;
        }

        .chat-stream {
          flex: 1;
          overflow-y: auto;
          padding: 32px;
          display: flex;
          flex-direction: column;
          gap: 20px;
        }

        .empty-state {
          margin: auto;
          max-width: 500px;
          text-align: center;
          color: #7a8a80;
        }

        .empty-title {
          font-family: 'Playfair Display', serif;
          color: #0f4c3a;
          font-size: 2rem;
          margin-bottom: 8px;
        }

        .bubble-user {
          align-self: flex-end;
          max-width: 65%;
          background: #0f4c3a;
          color: #f5f2eb;
          padding: 16px 20px;
          border-radius: 18px 18px 4px 18px;
          box-shadow: 0 4px 12px rgba(15, 76, 58, 0.15);
        }

        .bubble-bot {
          align-self: flex-start;
          max-width: 78%;
          background: #ffffff;
          border: 1px solid #e2dbcd;
          padding: 20px;
          border-radius: 18px 18px 18px 4px;
          box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
        }

        .badge {
          padding: 4px 10px;
          border-radius: 20px;
          font-size: 0.7rem;
          font-weight: 700;
          letter-spacing: 0.5px;
        }

        .badge-verified {
          background: #d2ebe0;
          color: #0f4c3a;
        }

        .badge-partial {
          background: #faebd0;
          color: #8a580c;
        }

        .badge-notfound {
          background: #fcdbd8;
          color: #a12318;
        }

        .confidence {
          font-size: 0.75rem;
          color: #5d6e65;
          font-weight: 700;
        }

        .source-pill {
          background: #f5f2eb;
          border: 1px solid #c9bfae;
          color: #0f4c3a;
          padding: 5px 12px;
          border-radius: 6px;
          font-size: 0.78rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .source-pill:hover {
          background: #0f4c3a;
          color: #f5f2eb;
          border-color: #0f4c3a;
        }

        .evidence-block {
          margin-top: 14px;
          padding-top: 12px;
          border-top: 1px solid #e2dbcd;
        }

        .evidence-title {
          font-size: 0.7rem;
          font-weight: 700;
          color: #0f4c3a;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          margin-bottom: 8px;
        }

        .evidence-snippet {
          background: #f8f6f1;
          border-left: 3px solid #d4a359;
          padding: 9px 11px;
          border-radius: 0 7px 7px 0;
          font-size: 0.75rem;
          color: #42564c;
          line-height: 1.5;
        }

        .input-bar-container {
          padding: 20px 32px;
          background: #ede8dc;
          border-top: 1px solid #e2dbcd;
        }

        .input-bar {
          display: flex;
          background: #ffffff;
          border: 1px solid #c9bfae;
          border-radius: 12px;
          padding: 6px;
          box-shadow: 0 2px 6px rgba(0,0,0,0.02);
        }

        .input-bar input {
          flex: 1;
          border: none;
          background: transparent;
          padding: 10px 16px;
          outline: none;
          font-size: 0.95rem;
          color: #1a2e26;
        }

        .send-btn {
          background: #0f4c3a;
          color: #f5f2eb;
          border: none;
          padding: 0 24px;
          border-radius: 8px;
          font-weight: 700;
          cursor: pointer;
          transition: background 0.2s;
        }

        .send-btn:hover {
          background: #145945;
        }

        .send-btn:disabled {
          opacity: 0.5;
          cursor: wait;
        }

        .inspector-drawer {
          position: fixed;
          top: 0;
          right: 0;
          width: 380px;
          height: 100%;
          background: #ede8dc;
          border-left: 1px solid #dcd3c1;
          padding: 28px;
          box-shadow: -10px 0 30px rgba(0, 0, 0, 0.08);
          z-index: 100;
          overflow-y: auto;
        }

        .drawer-close {
          border: none;
          background: none;
          cursor: pointer;
          color: #5d6e65;
          font-size: 1.2rem;
        }

        @media (max-width: 850px) {
          .sidebar {
            width: 250px;
          }

          .canvas-header {
            padding: 16px 20px;
          }

          .chat-stream {
            padding: 20px;
          }

          .input-bar-container {
            padding: 14px 20px;
          }
        }

        @media (max-width: 650px) {
          .sidebar {
            display: none;
          }

          .bubble-user,
          .bubble-bot {
            max-width: 95%;
          }

          .inspector-drawer {
            width: 100%;
          }
        }
      `}</style>

      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">KG</div>

          <div>
            <h1 className="brand-title">
               PROOFLY AI
            </h1>

            <span
              style={{
                fontSize: "0.72rem",
                color: "#a8c5bb",
                letterSpacing: "0.5px",
              }}
            >
              EVIDENCE-FIRST INTELLIGENCE
            </span>
          </div>
        </div>

        <div>
          <span
            style={{
              fontSize: "0.75rem",
              color: "#d4a359",
              fontWeight: "700",
              textTransform: "uppercase",
              letterSpacing: "0.5px",
              display: "block",
              marginBottom: "10px",
            }}
          >
            Source Knowledge
          </span>

          <input
            type="file"
            id="document-upload"
            accept={ACCEPTED_TYPES}
            multiple
            onChange={handleFileUpload}
            disabled={uploading}
            style={{ display: "none" }}
          />

          <label
            htmlFor="document-upload"
            className={`upload-btn ${
              uploading ? "disabled" : ""
            }`}
          >
            {uploading
              ? "Indexing Documents..."
              : "+ Upload Documents"}
          </label>

          {uploadError && (
            <div className="upload-error">
              {uploadError}
            </div>
          )}

          <div className="file-list">
            {uploadedFiles.length === 0 ? (
              <span
                style={{
                  fontSize: "0.72rem",
                  color: "#a8c5bb",
                  fontStyle: "italic",
                  textAlign: "center",
                  display: "block",
                  padding: "6px",
                }}
              >
                No active documents indexed
              </span>
            ) : (
              uploadedFiles.map((file, i) => (
                <div key={`${file.name}-${i}`} className="file-item">
                  <div className="file-info">
                    <span
                      className="file-name"
                      title={file.name}
                    >
                      📄 {file.name}
                    </span>

                    <span className="file-meta">
                      {file.size} • {file.timestamp}
                    </span>
                  </div>

                  <span className="file-status">
                    ACTIVE
                  </span>
                </div>
              ))
            )}
          </div>

          {knowledgeStats && (
            <div className="stats-box">
              <div>
                <span className="stat-value">
                  {knowledgeStats.documents_total ?? 0}
                </span>
                <span className="stat-label">
                  Documents
                </span>
              </div>

              <div>
                <span className="stat-value">
                  {knowledgeStats.pages_total ?? 0}
                </span>
                <span className="stat-label">
                  Pages
                </span>
              </div>

              <div>
                <span className="stat-value">
                  {knowledgeStats.chunks_total ?? 0}
                </span>
                <span className="stat-label">
                  Chunks
                </span>
              </div>
            </div>
          )}
        </div>

        <div
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            gap: "8px",
          }}
        >
          <span
            style={{
              fontSize: "0.75rem",
              color: "#d4a359",
              fontWeight: "700",
              textTransform: "uppercase",
              letterSpacing: "0.5px",
              marginBottom: "4px",
              display: "block",
            }}
          >
            Reliability Suite
          </span>

          {RELIABILITY_TESTS.map((test, idx) => (
            <div
              key={idx}
              className="test-card"
              onClick={() => handleSend(test.q)}
            >
              <span
                style={{
                  fontSize: "0.82rem",
                  fontWeight: "500",
                  color: "#f5f2eb",
                }}
              >
                {test.label}
              </span>

              <span
                style={{
                  fontSize: "0.68rem",
                  color: "#d4a359",
                  background: "rgba(212, 163, 89, 0.15)",
                  padding: "2px 6px",
                  borderRadius: "4px",
                }}
              >
                {test.tag}
              </span>
            </div>
          ))}
        </div>
      </aside>

      <main className="canvas">
        <header className="canvas-header">
          <div>
            <span
              style={{
                display: "block",
                fontWeight: "700",
                fontSize: "0.95rem",
                color: "#0f4c3a",
              }}
            >
              Grounded Knowledge Workspace
            </span>

            <span
              style={{
                fontSize: "0.7rem",
                color: "#7a8a80",
              }}
            >
              Evidence-first document intelligence
            </span>
          </div>

          <div className="status-indicator">
            <span className="status-dot" />
            SYSTEM READY
          </div>
        </header>

        <div className="chat-stream">
          {messages.length === 0 && (
            <div className="empty-state">
              <div className="empty-title">
                Ask PROOFLY AI
              </div>

              <p>
                Ask a question about your indexed documents.
                PROOFLY AI retrieves evidence and refuses to
                guess when the knowledge base does not support
                an answer.
              </p>
            </div>
          )}

          {messages.map((m, idx) => (
            <div
              key={idx}
              className={
                m.role === "user"
                  ? "bubble-user"
                  : "bubble-bot"
              }
            >
              {m.role === "bot" && (
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    marginBottom: "12px",
                    gap: "8px",
                    flexWrap: "wrap",
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      gap: "8px",
                      alignItems: "center",
                    }}
                  >
                    {renderBadge(m.status)}
                  </div>

                  {m.confidencePercent !== null &&
                    m.confidencePercent !== undefined && (
                      <span className="confidence">
                        Confidence:{" "}
                        {m.confidencePercent.toFixed(1)}%
                      </span>
                    )}
                </div>
              )}

              <p
                style={{
                  margin: 0,
                  lineHeight: "1.6",
                  fontSize: "0.95rem",
                }}
              >
                {m.text || m.answer}
              </p>

              {m.sources && m.sources.length > 0 && (
                <div
                  style={{
                    marginTop: "14px",
                    paddingTop: "12px",
                    borderTop: "1px solid #e2dbcd",
                    display: "flex",
                    gap: "8px",
                    flexWrap: "wrap",
                  }}
                >
                  {m.sources.map((src, sIdx) => (
                    <button
                      key={sIdx}
                      onClick={() =>
                        setSelectedSource({
                          ...src,
                          evidence:
                            m.evidence?.filter(
                              (e) =>
                                e.document ===
                                  src.document &&
                                e.page === src.page
                            ) || [],
                        })
                      }
                      className="source-pill"
                    >
                      📄 {src.document || "Document"}{" "}
                      (p. {src.page || 1})
                    </button>
                  ))}
                </div>
              )}

              {m.evidence && m.evidence.length > 0 && (
                <div className="evidence-block">
                  <div className="evidence-title">
                    Retrieved Evidence
                  </div>

                  <div className="evidence-snippet">
                    {m.evidence[0].text}
                  </div>
                </div>
              )}

              {m.status === "not_found" && (
                <div className="evidence-block">
                  <div className="evidence-snippet">
                    No supporting evidence was found in the
                    indexed documents.
                  </div>
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div
              style={{
                color: "#0f4c3a",
                fontSize: "0.88rem",
                fontWeight: "600",
              }}
            >
              Reading indexed documents and validating
              evidence...
            </div>
          )}
        </div>

        <div className="input-bar-container">
          <div className="input-bar">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  handleSend();
                }
              }}
              placeholder="Ask a question about your documents..."
              disabled={loading}
            />

            <button
              onClick={() => handleSend()}
              className="send-btn"
              disabled={loading || !input.trim()}
            >
              {loading ? "..." : "Send"}
            </button>
          </div>
        </div>
      </main>

      {selectedSource && (
        <div className="inspector-drawer">
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <h3
              style={{
                margin: 0,
                fontSize: "0.95rem",
                color: "#0f4c3a",
                fontWeight: "700",
              }}
            >
              SOURCE PROOF
            </h3>

            <button
              onClick={() => setSelectedSource(null)}
              className="drawer-close"
            >
              ✕
            </button>
          </div>

          <hr
            style={{
              borderColor: "#c9bfae",
              margin: "16px 0",
            }}
          />

          <div
            style={{
              fontSize: "0.85rem",
              color: "#1a2e26",
              display: "flex",
              flexDirection: "column",
              gap: "10px",
            }}
          >
            <div>
              <strong>Document:</strong>{" "}
              {selectedSource.document || "Source File"}
            </div>

            <div>
              <strong>Page:</strong>{" "}
              {selectedSource.page || 1}
            </div>

            {selectedSource.section && (
              <div>
                <strong>Section:</strong>{" "}
                {selectedSource.section}
              </div>
            )}

            {selectedSource.score !== undefined && (
              <div>
                <strong>Evidence Score:</strong>{" "}
                {selectedSource.score}
              </div>
            )}

            <div
              style={{
                marginTop: "12px",
                background: "#ffffff",
                border: "1px solid #c9bfae",
                padding: "16px",
                borderRadius: "10px",
                lineHeight: "1.6",
              }}
            >
              {selectedSource.evidence?.length > 0
                ? selectedSource.evidence.map(
                    (item, index) => (
                      <div
                        key={index}
                        style={{
                          marginBottom:
                            index <
                            selectedSource.evidence.length -
                              1
                              ? "14px"
                              : "0",
                        }}
                      >
                        {item.text}
                      </div>
                    )
                  )
                : selectedSource.text ||
                  "No direct evidence passage available."}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
