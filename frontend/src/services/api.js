const API_BASE_URL = "http://127.0.0.1:8000/api";

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file); // Must match UploadFile = File(...) in backend

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Upload failed");
  }

  return await response.json();
}

export async function askQuestion(question) {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Chat request failed");
  }

  return await response.json();
}
