import axios from "axios";

const TOKEN_KEY = "dynamic_qr_token";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
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

export const createQr = (contentUrl) =>
  api.post("/create-qr", null, {
    params: { content_url: contentUrl },
  });

export const getMyQrs = () => api.get("/my-qrs");

export const updateQr = (qrId, destinationUrl) =>
  api.put(`/update-qr/${encodeURIComponent(qrId)}`, {
    destination_url: destinationUrl,
  });

export const getQrDetails = (qrId) =>
  api.get(`/details/${encodeURIComponent(qrId)}`);