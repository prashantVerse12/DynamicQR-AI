import axios from "axios";

const TOKEN_KEY = "dynamic_qr_token";
const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_URL,
});

export const getToken = () => localStorage.getItem(TOKEN_KEY);

export const setToken = (token) => localStorage.setItem(TOKEN_KEY, token);

export const clearToken = () => localStorage.removeItem(TOKEN_KEY);

api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (
      error.response?.status === 401 &&
      getToken() &&
      window.location.pathname !== "/login"
    ) {
      clearToken();
      window.location.assign("/login");
    }
    return Promise.reject(error);
  },
);

export const registerUser = (email, password) =>
  api.post("/register", { email, password });

export const loginUser = (email, password) =>
  api.post("/login", { email, password });

export const logout = () => clearToken();

export const createQr = (content) => {
  if (typeof content === "string") {
    return api.post("/create-qr", null, {
      params: { content_url: content },
    });
  }

  return api.post("/create-qr", {
    content_type: content.contentType,
    content: content.content,
  });
};

export const getMyQrs = () => api.get("/my-qrs");

export const updateQr = (qrId, content) => {
  if (typeof content === "string") {
    return api.put(`/update-qr/${encodeURIComponent(qrId)}`, {
      destination_url: content,
    });
  }

  return api.put(`/update-qr/${encodeURIComponent(qrId)}`, {
    content_type: content.contentType,
    content: content.content,
  });
};

export const getQrDetails = (qrId) =>
  api.get(`/details/${encodeURIComponent(qrId)}`);