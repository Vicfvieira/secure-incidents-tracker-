import axios from "axios";

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export function extractErrorMessage(error, fallback = "Ocorreu um erro inesperado.") {
  const detail = error?.response?.data?.detail;
  if (typeof detail === "string") return detail;
  if (error?.response?.status === 429) return "Muitas tentativas. Aguarde um minuto e tente novamente.";
  if (Array.isArray(detail) && detail.length > 0) return detail[0].msg || fallback;
  return fallback;
}
