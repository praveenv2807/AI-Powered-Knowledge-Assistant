import { useMemo, useRef, useState } from "react";
import { askQuestion, uploadDocuments } from "./services/api";

const TEST_QUESTIONS = [
  {
    label: "Direct Query",
    tag: "Exact",
    question: "What is the minimum attendance requirement?",
  },
  {
    label: "Paraphrased",
    tag: "Semantic",
    question: "How much attendance do I need before I can write the exam?",
  },
  {
    label: "Cross-Doc",
    tag: "Multi-Ref",
    question:
      "What is the minimum attendance requirement and what happens below that limit?",
  },
  {
    label: "Unanswerable",
    tag: "Negative",
    question: "What is the Wi-Fi password?",
  },
  {
    label: "Partial Proof",
    tag: "Edge Case",
    question:
      "Does having a medical condition automatically allow attendance below 75 percent?",
  },
];

const styles = {
  app: {
    minHeight: "100vh",
    display: "grid",
    gridTemplateColumns: "350px 1fr",
    background: "#f5f2e9",
    color: "#123f35",
    fontFamily:
      "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  },
  sidebar: {
    background: "#0d5747",
    color: "#fff",
    padding: "30px 22px",
    display: "flex",
    flexDirection: "column",
    gap: "26px",
    minHeight: "100vh",
    boxSizing: "border-box",
  },
  brandRow: {
    display: "flex",
    alignItems: "center",
    gap: "14px",
  },
  logo: {
    width: 44,
    height: 44,
    borderRadius: 10,
    display: "grid",
    placeItems: "center",
    background: "#dcae52",
    color: "#17483d",
    fontWeight: 900,
    fontSize: 17,
  },
  brand: {
    margin: 0,
    fontFamily: "Georgia, serif",
    fontSize: 25,
    letterSpacing: "-0.5px",
  },
  tagline: {
    marginTop: 3,
    fontSize: 12,
    letterSpacing: "0.8px",
    color: "#d8e3db",
  },
  sectionTitle: {
    margin: "0 0 12px",
    fontSize: 13,
    fontWeight: 800,
    color: "#e0a949",
    letterSpacing: "0.5px",
  },
  uploadButton: {
    width: "100%",
    border: "1px dashed #d9aa52",
    borderRadius: 10,
    padding: "14px 12px",
    background: "rgba(255,255,255,0.035)",
    color: "#fff",
    fontWeight: 700,
    cursor: "pointer",
    fontSize: 15,
  },
  hiddenInput: { display: "none" },
  docSummary: {
    marginTop: 14,
    padding: "12px 13px",
    borderRadius: 10,
    background: "rgba(255,255,255,0.06)",
    fontSize: 13,
    lineHeight: 1.55,
  },
  testButton: {
    width: "100%",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    border: "1px solid rgba(255,255,255,0.08)",
    borderRadius: 9,
    padding: "11px 13px",
    marginBottom: 9,
    background: "rgba(255,255,255,0.055)",
    color: "#fff",
    cursor: "pointer",
    textAlign: "left",
  },
  tag: {
    background: "rgba(220,174,82,0.18)",
    color: "#e3ad4f",
    borderRadius: 5,
    padding: "3px 7px",
    fontSize: 11,
    whiteSpace: "nowrap",
  },
  main: {
    minWidth: 0,
    display: "grid",
    gridTemplateRows: "88px 1fr auto",
    minHeight: "100vh",
  },
  header: {
    borderBottom: "1px solid #ded9ca",
    background: "#eeeadf",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "0 36px",
  },
  title: {
    margin: 0,
    fontSize: 18,
    fontWeight: 800,
  },
  subtitle: {
    margin: "5px 0 0",
    color: "#81928b",
    fontSize: 13,
  },
  ready: {
    display: "flex",
    alignItems: "center",
    gap: 8,
    fontSize: 13,
    fontWeight: 800,
  },
  dot: {
    width: 9,
    height: 9,
    borderRadius: "50%",
    background: "#2b9c77",
  },
  workspace: {
    overflowY: "auto",
    padding: "28px 34px",
  },
  empty: {
    minHeight: "58vh",
    display: "grid",
    placeItems: "center",
    textAlign: "center",
  },
  emptyInner: {
    maxWidth: 600,
  },
  hero: {
    fontFamily: "Georgia, serif",
    fontSize: 38,
    margin: "0 0 16px",
  },
  heroText: {
    color: "#71847e",
    lineHeight: 1.5,
    fontSize: 17,
    margin: 0,
  },
  messageList: {
    maxWidth: 1000,
    margin: "0 auto",
  },
  userMessage: {
    marginLeft: "auto",
    maxWidth: "72%",
    background: "#0d5747",
    color: "#fff",
    padding: "14px 18px",
    borderRadius: "18px 18px 4px 18px",
    marginBottom: 12,
    lineHeight: 1.5,
  },
  resultCard: {
    maxWidth: "78%",
    background: "#fff",
    border: "1px solid #e0dbcf",
    borderRadius: "16px 16px 16px 4px",
    padding: 20,
    marginBottom: 24,
    boxShadow: "0 8px 24px rgba(36,52,44,0.05)",
  },
  status: {
    display: "inline-block",
    borderRadius: 999,
    padding: "5px 10px",
    fontSize: 11,
    fontWeight: 900,
    letterSpacing: "0.5px",
    marginBottom: 12,
  },
  answer: {
    fontSize: 16,
    lineHeight: 1.65,
    margin: "0 0 16px",
    whiteSpace: "pre-wrap",
  },
  evidence: {
    marginTop: 16,
    paddingTop: 16,
    borderTop: "1px solid #ece8de",
  },
  evidenceItem: {
    background: "#f6f3ea",
    borderRadius: 10,
    padding: 12,
    marginTop: 9,
    fontSize: 13,
    lineHeight: 1.55,
  },
  source: {
    color: "#55736a",
    fontSize: 12,
    marginTop: 7,
  },
  composer: {
    padding: "16px 34px 22px",
    background: "#eeeadf",
    borderTop: "1px solid #ded9ca",
  },
  composerInner: {
    display: "flex",
    gap: 10,
    background: "#fff",
    border: "1px solid #d8d0c0",
    borderRadius: 13,
    padding: 7,
  },
  input: {
    flex: 1,
    minWidth: 0,
    border: 0,
    outline: 0,
    padding: "12px 16px",
    fontSize: 16,
    color: "#123f35",
    background: "transparent",
  },
  send: {
    border: 0,
    borderRadius: 9,
    padding: "0 24px",
    background: "#0d5747",
    color: "#fff",
    fontWeight: 800,
    cursor: "pointer",
  },
  disabled: {
    opacity: 0.45,
    cursor: "not-allowed",
  },
  notice: {
    marginBottom: 12,
    padding: "11px 14px",
    borderRadius: 9,
    background: "#fff1ed",
    color: "#a53d2e",
    border: "1px solid #f2c9c1",
    fontSize: 13,
  },
};

function statusStyle(status) {
  if (status === "verified") {
    return { background: "#dff4e8", color: "#19734f" };
  }
  if (status === "not_found") {
    return { background: "#fff0d8", color: "#9b6510" };
  }
  return { background: "#ffe4df", color: "#a43c2f" };
}

function statusLabel(status) {
  if (status === "verified") return "VERIFIED";
  if (status === "not_found") return "NOT FOUND";
  return String(status || "ERROR").replaceAll("_", " ").toUpperCase();
}

export default function App() {
  const fileInputRef = useRef(null);

  const [documents, setDocuments] = useState([]);
  const [stats, setStats] = useState(null);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [error, setError] = useState("");
  const [uploading, setUploading] = useState(false);
  const [asking, setAsking] = useState(false);

  const indexed = documents.length > 0;

  const documentNames = useMemo(
    () => documents.map((file) => file.name),
    [documents]
  );

  async function handleUpload(event) {
    const files = Array.from(event.target.files || []);
    if (!files.length) return;

    setError("");
    setUploading(true);

    try {
      const result = await uploadDocuments(files);

      setDocuments(files);
      setStats(result?.stats || null);

      setMessages((prev) => [
        ...prev,
        {
          type: "system",
          text:
            result?.message ||
            `Successfully processed ${files.length} document(s).`,
        },
      ]);
    } catch (err) {
      setError(err?.message || "Failed to upload documents.");
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  }

  function addQuestion(text) {
    setQuestion(text);
    setError("");
  }

  async function handleAsk(event) {
    event?.preventDefault();

    const trimmed = question.trim();

    if (!trimmed) {
      setError("Please enter a question.");
      return;
    }

    // Critical UX guard: never call /api/chat without indexed documents.
    if (!indexed) {
      setError("Please upload at least one document before asking a question.");
      return;
    }

    setError("");
    setAsking(true);

    setMessages((prev) => [
      ...prev,
      {
        type: "user",
        text: trimmed,
      },
    ]);

    setQuestion("");

    try {
      const result = await askQuestion(trimmed);

      setMessages((prev) => [
        ...prev,
        {
          type: "assistant",
          result,
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          type: "error",
          text:
            err?.message ||
            "The request failed. Please check the backend and try again.",
        },
      ]);
    } finally {
      setAsking(false);
    }
  }

  return (
    <div style={styles.app}>
      <aside style={styles.sidebar}>
        <div>
          <div style={styles.brandRow}>
            <div style={styles.logo}>KG</div>
            <div>
              <h1 style={styles.brand}>PROOFLY AI</h1>
              <div style={styles.tagline}>EVIDENCE-FIRST INTELLIGENCE</div>
            </div>
          </div>
        </div>

        <section>
          <h2 style={styles.sectionTitle}>SOURCE KNOWLEDGE</h2>

          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf,.txt,.docx,.md,.markdown,.html,.htm"
            style={styles.hiddenInput}
            onChange={handleUpload}
          />

          <button
            type="button"
            style={{
              ...styles.uploadButton,
              ...(uploading ? styles.disabled : {}),
            }}
            disabled={uploading}
            onClick={() => fileInputRef.current?.click()}
          >
            {uploading ? "Uploading..." : "+ Upload Documents"}
          </button>

          {indexed ? (
            <div style={styles.docSummary}>
              <strong>{documents.length} document(s) indexed</strong>
              <div style={{ marginTop: 6 }}>
                {documentNames.map((name) => (
                  <div key={name}>• {name}</div>
                ))}
              </div>

              {stats && (
                <div style={{ marginTop: 10 }}>
                  {stats.pages_total ?? 0} pages · {stats.chunks_total ?? 0}{" "}
                  chunks
                </div>
              )}
            </div>
          ) : (
            <div
              style={{
                textAlign: "center",
                marginTop: 14,
                color: "#c7d5cf",
                fontSize: 13,
                fontStyle: "italic",
              }}
            >
              No active documents indexed
            </div>
          )}
        </section>

        <section>
          <h2 style={styles.sectionTitle}>RELIABILITY SUITE</h2>

          {TEST_QUESTIONS.map((test) => (
            <button
              key={test.label}
              type="button"
              style={styles.testButton}
              onClick={() => addQuestion(test.question)}
            >
              <span>{test.label}</span>
              <span style={styles.tag}>{test.tag}</span>
            </button>
          ))}
        </section>
      </aside>

      <main style={styles.main}>
        <header style={styles.header}>
          <div>
            <h2 style={styles.title}>Grounded Knowledge Workspace</h2>
            <p style={styles.subtitle}>
              Evidence-first document intelligence
            </p>
          </div>

          <div style={styles.ready}>
            <span style={styles.dot} />
            SYSTEM READY
          </div>
        </header>

        <section style={styles.workspace}>
          {error && <div style={styles.notice}>{error}</div>}

          {!messages.length ? (
            <div style={styles.empty}>
              <div style={styles.emptyInner}>
                <h2 style={styles.hero}>Ask PROOFLY AI</h2>
                <p style={styles.heroText}>
                  Ask a question about your indexed documents. PROOFLY AI
                  retrieves evidence and refuses to guess when the knowledge
                  base does not support an answer.
                </p>
              </div>
            </div>
          ) : (
            <div style={styles.messageList}>
              {messages.map((message, index) => {
                if (message.type === "user") {
                  return (
                    <div key={index} style={styles.userMessage}>
                      {message.text}
                    </div>
                  );
                }

                if (message.type === "system") {
                  return (
                    <div key={index} style={styles.notice}>
                      {message.text}
                    </div>
                  );
                }

                if (message.type === "error") {
                  return (
                    <div key={index} style={styles.resultCard}>
                      <div
                        style={{
                          ...styles.status,
                          ...statusStyle("error"),
                        }}
                      >
                        ERROR
                      </div>
                      <p style={styles.answer}>{message.text}</p>
                    </div>
                  );
                }

                const result = message.result || {};
                const evidence = result.evidence || [];
                const sources = result.sources || [];

                return (
                  <div key={index} style={styles.resultCard}>
                    <div
                      style={{
                        ...styles.status,
                        ...statusStyle(result.status),
                      }}
                    >
                      {statusLabel(result.status)}
                    </div>

                    <p style={styles.answer}>
                      {result.answer || "No answer returned."}
                    </p>

                    {result.reliability && (
                      <div style={{ fontSize: 12, color: "#71847e" }}>
                        Confidence:{" "}
                        {result.reliability.confidence_percent ??
                          Math.round(
                            (result.reliability.confidence || 0) * 100
                          )}
                        %
                        {result.reliability.reason
                          ? ` · ${result.reliability.reason}`
                          : ""}
                      </div>
                    )}

                    {sources.length > 0 && (
                      <div style={styles.evidence}>
                        <strong>SOURCES</strong>
                        {sources.map((source, sourceIndex) => (
                          <div
                            key={`${source.document}-${source.page}-${sourceIndex}`}
                            style={styles.source}
                          >
                            {source.document} · Page {source.page}
                            {source.section
                              ? ` · Section ${source.section}`
                              : ""}
                          </div>
                        ))}
                      </div>
                    )}

                    {evidence.length > 0 && (
                      <div style={styles.evidence}>
                        <strong>EVIDENCE</strong>

                        {evidence.map((item, evidenceIndex) => (
                          <div key={evidenceIndex} style={styles.evidenceItem}>
                            <div>{item.text}</div>

                            <div style={styles.source}>
                              {item.document} · Page {item.page}
                              {item.section
                                ? ` · ${item.section}`
                                : ""}
                              {typeof item.retrieval_score === "number"
                                ? ` · Retrieval ${item.retrieval_score.toFixed(
                                    2
                                  )}`
                                : ""}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </section>

        <form style={styles.composer} onSubmit={handleAsk}>
          <div style={styles.composerInner}>
            <input
              style={styles.input}
              value={question}
              onChange={(event) => {
                setQuestion(event.target.value);
                if (error) setError("");
              }}
              placeholder={
                indexed
                  ? "Ask a question about your documents..."
                  : "Upload a document before asking a question..."
              }
              disabled={asking}
            />

            <button
              type="submit"
              style={{
                ...styles.send,
                ...(!indexed || asking ? styles.disabled : {}),
              }}
              disabled={!indexed || asking}
            >
              {asking ? "Thinking..." : "Send"}
            </button>
          </div>
        </form>
      </main>
    </div>
  );
}
