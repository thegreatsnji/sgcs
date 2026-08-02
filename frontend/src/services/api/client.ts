import axios, { type AxiosError, type InternalAxiosRequestConfig } from "axios";

import { clearStoredAuth, getStoredAuth, setStoredAuth } from "@/utils/auth-storage";

/** Em dev usa o proxy do Vite (`/api`) para evitar falhas de CORS no browser. */
const API_ORIGIN = import.meta.env.DEV
  ? ""
  : import.meta.env.VITE_API_URL || "http://localhost:8000";
const API_ROOT = `${API_ORIGIN}/api/v1`;

export const api = axios.create({
  baseURL: API_ROOT,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const auth = getStoredAuth();
  if (auth?.access) {
    config.headers.Authorization = `Bearer ${auth.access}`;
  }
  return config;
});

let isRefreshing = false;
let refreshQueue: Array<(token: string | null) => void> = [];

function processQueue(token: string | null) {
  refreshQueue.forEach((callback) => callback(token));
  refreshQueue = [];
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };

    if (error.response?.status !== 401 || originalRequest._retry) {
      return Promise.reject(error);
    }

    const auth = getStoredAuth();
    if (!auth?.refresh) {
      clearStoredAuth();
      return Promise.reject(error);
    }

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        refreshQueue.push((token) => {
          if (!token) {
            reject(error);
            return;
          }
          originalRequest.headers.Authorization = `Bearer ${token}`;
          resolve(api(originalRequest));
        });
      });
    }

    originalRequest._retry = true;
    isRefreshing = true;

    try {
      const { data } = await axios.post<{ access: string; refresh?: string }>(
        `${API_ORIGIN}/api/v1/auth/refresh/`,
        { refresh: auth.refresh },
      );

      // Backend rotates refresh tokens — persist the new pair to avoid blacklist failures
      const newTokens = {
        access: data.access,
        refresh: data.refresh ?? auth.refresh,
      };
      setStoredAuth(newTokens);
      processQueue(data.access);
      originalRequest.headers.Authorization = `Bearer ${data.access}`;
      return api(originalRequest);
    } catch (refreshError) {
      clearStoredAuth();
      processQueue(null);
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  },
);

export { API_ORIGIN as API_URL, API_ROOT };
