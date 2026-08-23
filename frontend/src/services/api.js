const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

async function parseResponse(response, fallbackMessage) {
  let data = null;

  try {
    data = await response.json();
  } catch {
    throw new Error(fallbackMessage);
  }

  if (!response.ok) {
    throw new Error(
      data?.detail || data?.message || `${fallbackMessage} (${response.status}).`
    );
  }

  return data;
}

export async function askQuestion(question) {
  const trimmed = String(question || "").trim();

  if (!trimmed) {
    throw new Error("Please enter a question.");
  }

  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question: trimmed }),
  });

  return parseResponse(response, "Chat request failed.");
}

export async function uploadDocuments(files) {
  if (!files || files.length === 0) {
    throw new Error("Please select at least one document.");
  }

  const formData = new FormData();
  for (const file of files) {
    formData.append("files", file);
  }

  const response = await fetch(`${API_BASE_URL}/api/upload`, {
    method: "POST",
    body: formData,
  });

  return parseResponse(response, "Upload failed.");
}

export async function uploadDocument(file) {
  return uploadDocuments([file]);
}

export async function checkBackendHealth() {
  const response = await fetch(`${API_BASE_URL}/`);
  return parseResponse(response, "Backend is not available.");
}
