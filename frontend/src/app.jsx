import React, { useState } from "react";
import { askQuestion, uploadDocument } from "./services/api";

const RELIABILITY_TESTS = [
  {
    label: "Test 1: Direct Question",
    q: "What is the minimum attendance requirement?",
  },
  {
    label: "Test 2: Paraphrased Query",
    q: "How much attendance do I need before I can write the exam?",
  },
  {
    label: "Test 3: Cross-Document",
    q: "Can a student with 70% attendance appear for the exam?",
  },
  { label: "Test 4: Unanswerable", q: "What is the hostel Wi-Fi password?" },
  {
    label: "Test 5: Partial Evidence",
    q: "Does a medical condition allow attendance below the required percentage?",
  },
];

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [selectedSource, setSelectedSource] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSend = async (queryText) => {
    const q = queryText || input;
    if (!q.trim()) return;

    const userMsg = { role: "user", text: q };
    setMessages((prev) => [...prev, userMsg]);
    if (!queryText) setInput("");
    setLoading(true);

    try {
      const data = await askQuestion(q);
      const botMsg = {
        role: "bot",
        status: data.status,
        answer: data.answer,
        strength: data.evidence_strength,
        sources: data.sources || [],
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          status: "error",
          answer: "Failed to connect to K-GUARD backend.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    try {
      await uploadDocument(file);
      alert(`File "${file.name}" uploaded successfully!`);
    } catch (err) {
      alert("Failed to upload file.");
    } finally {
      setUploading(false);
    }
  };

  const renderStatusBadge = (status) => {
    switch (status) {
      case "verified":
        return (
          <span style={{ color: "#10B981", fontWeight: "bold" }}>
            🟢 VERIFIED
          </span>
        );
      case "partially_supported":
      case "partial":
        return (
          <span style={{ color: "#F59E0B", fontWeight: "bold" }}>
            🟡 PARTIALLY SUPPORTED
          </span>
        );
      default:
        return (
          <span style={{ color: "#EF4444", fontWeight: "bold" }}>
            🔴 NOT FOUND
          </span>
        );
    }
  };

  return (
    <div
      style={{
        display: "flex",
        height: "100vh",
        fontFamily: "sans-serif",
        background: "#0f172a",
        color: "#f8fafc",
      }}
    >
      {/* Sidebar */}
      <div
        style={{
          width: "280px",
          background: "#1e293b",
          padding: "20px",
          borderRight: "1px solid #334155",
          display: "flex",
          flexDirection: "column",
          gap: "20px",
        }}
      >
        <h2>K-GUARD</h2>
        <div
          style={{
            padding: "8px 12px",
            background: "#064e3b",
            color: "#34d399",
            borderRadius: "6px",
            fontSize: "0.85rem",
            fontWeight: "bold",
          }}
        >
          ● SYSTEM READY
        </div>

        <div>
          <h4>Knowledge Base</h4>
          <input
            type="file"
            onChange={handleFileUpload}
            disabled={uploading}
            style={{ width: "100%", fontSize: "0.8rem", color: "#94a3b8" }}
          />
          {uploading && (
            <p style={{ fontSize: "0.8rem", color: "#94a3b8" }}>Uploading...</p>
          )}
        </div>

        <div>
          <h4>Reliability Test Mode</h4>
          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            {RELIABILITY_TESTS.map((test, i) => (
              <button
                key={i}
                onClick={() => handleSend(test.q)}
                style={{
                  background: "#334155",
                  color: "#fff",
                  border: "none",
                  padding: "8px",
                  borderRadius: "4px",
                  textAlign: "left",
                  cursor: "pointer",
                  fontSize: "0.75rem",
                }}
              >
                {test.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Chat Interface */}
      <div
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          padding: "20px",
        }}
      >
        <div
          style={{
            flex: 1,
            overflowY: "auto",
            display: "flex",
            flexDirection: "column",
            gap: "15px",
          }}
        >
          {messages.map((m, idx) => (
            <div
              key={idx}
              style={{
                alignSelf: m.role === "user" ? "flex-end" : "flex-start",
                maxWidth: "75%",
                background: m.role === "user" ? "#2563eb" : "#1e293b",
                padding: "12px 16px",
                borderRadius: "8px",
              }}
            >
              {m.role === "bot" && (
                <div
                  style={{
                    marginBottom: "8px",
                    display: "flex",
                    justifyContent: "space-between",
                    fontSize: "0.8rem",
                  }}
                >
                  {renderStatusBadge(m.status)}
                  {m.strength && (
                    <span>Evidence Score: {Math.round(m.strength * 100)}%</span>
                  )}
                </div>
              )}
              <p style={{ margin: 0, lineHeight: "1.5" }}>
                {m.text || m.answer}
              </p>

              {m.sources && m.sources.length > 0 && (
                <div
                  style={{
                    marginTop: "10px",
                    paddingTop: "10px",
                    borderTop: "1px solid #334155",
                  }}
                >
                  <small style={{ color: "#94a3b8" }}>Sources:</small>
                  <div
                    style={{
                      display: "flex",
                      gap: "5px",
                      marginTop: "5px",
                      flexWrap: "wrap",
                    }}
                  >
                    {m.sources.map((src, sIdx) => (
                      <button
                        key={sIdx}
                        onClick={() => setSelectedSource(src)}
                        style={{
                          background: "#0f172a",
                          color: "#60a5fa",
                          border: "1px solid #3b82f6",
                          padding: "4px 8px",
                          borderRadius: "4px",
                          cursor: "pointer",
                          fontSize: "0.75rem",
                        }}
                      >
                        📄 {src.document} (p. {src.page})
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div style={{ color: "#94a3b8" }}>
              K-GUARD is processing query...
            </div>
          )}
        </div>

        {/* Input Bar */}
        <div style={{ display: "flex", gap: "10px", marginTop: "15px" }}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Ask a question..."
            style={{
              flex: 1,
              padding: "12px",
              borderRadius: "6px",
              border: "1px solid #334155",
              background: "#1e293b",
              color: "#fff",
            }}
          />
          <button
            onClick={() => handleSend()}
            style={{
              padding: "12px 24px",
              background: "#2563eb",
              color: "#fff",
              border: "none",
              borderRadius: "6px",
              cursor: "pointer",
              fontWeight: "bold",
            }}
          >
            Send
          </button>
        </div>
      </div>

      {/* Source Evidence Inspection Drawer */}
      {selectedSource && (
        <div
          style={{
            position: "fixed",
            top: 0,
            right: 0,
            width: "360px",
            height: "100%",
            background: "#1e293b",
            borderLeft: "1px solid #334155",
            padding: "20px",
            boxShadow: "-5px 0 15px rgba(0,0,0,0.5)",
            display: "flex",
            flexDirection: "column",
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <h3 style={{ margin: 0 }}>SOURCE EVIDENCE</h3>
            <button
              onClick={() => setSelectedSource(null)}
              style={{
                background: "none",
                border: "none",
                color: "#fff",
                cursor: "pointer",
                fontSize: "1.2rem",
              }}
            >
              ✕
            </button>
          </div>
          <hr style={{ borderColor: "#334155", margin: "15px 0" }} />
          <p>
            <strong>Document:</strong> {selectedSource.document}
          </p>
          <p>
            <strong>Page:</strong> {selectedSource.page}
          </p>
          <p>
            <strong>Section:</strong> {selectedSource.section || "General"}
          </p>
          <div
            style={{
              marginTop: "10px",
              background: "#0f172a",
              padding: "12px",
              borderRadius: "6px",
              fontSize: "0.85rem",
              lineHeight: "1.4",
            }}
          >
            <em>"{selectedSource.text}"</em>
          </div>
        </div>
      )}
    </div>
  );
}
