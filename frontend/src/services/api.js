const API_BASE_URL = "http://127.0.0.1:8000";

/**
 * Ask a question against the indexed knowledge base.
 */
export async function askQuestion(question) {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      question: question.trim(),
    }),
  });

  let data;

  try {
    data = await response.json();
  } catch {
    throw new Error("Backend returned an invalid response.");
  }

  if (!response.ok) {
    throw new Error(
      data?.detail ||
        data?.message ||
        `Chat request failed (${response.status}).`
    );
  }

  return data;
}

/**
 * Upload multiple documents to the knowledge base.
 *
 * The backend expects the multipart field name: "files"
 */
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

  let data;

  try {
    data = await response.json();
  } catch {
    throw new Error("Upload returned an invalid response.");
  }

  if (!response.ok) {
    throw new Error(
      data?.detail ||
        data?.message ||
        `Upload failed (${response.status}).`
    );
  }

  return data;
}

/**
 * Backward-compatible single-document helper.
 */
export async function uploadDocument(file) {
  return uploadDocuments([file]);
}

/**
 * Backend health check.
 */
export async function checkBackendHealth() {
  const response = await fetch(`${API_BASE_URL}/`);

  if (!response.ok) {
    throw new Error("Backend is not available.");
  }

  return response.json();
}