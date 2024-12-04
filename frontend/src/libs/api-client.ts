import axios, { type InternalAxiosRequestConfig } from "axios";

export const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL,
});

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
    config.headers.Accept = "application/json";

    return config;
});