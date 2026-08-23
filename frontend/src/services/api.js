import axios from "axios";

const API_BASE = "http://127.0.0.1:8000/api";

export const askQuestion = async (question) => {
  const response = await axios.post(`${API_BASE}/chat`, { question });
  return response.data;
};

export const uploadDocument = async (file) => {
  const formData = new FormData();
  formData.append("file", file);
  const response = await axios.post(`${API_BASE}/documents/upload`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
};
