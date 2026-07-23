import { getBaseUrl } from "./api.config";
import { ROUTES } from "../constants/routes";
import axios, { AxiosError, AxiosRequestConfig } from "axios";

export const apiInstance = axios.create({
  baseURL: getBaseUrl(),
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
});

interface QueueItem {
  resolve: (value: string | PromiseLike<string>) => void;
  reject: (reason?: unknown) => void;
}

let isRefreshing = false;
let failedQueue: QueueItem[] = [];

const processQueue = (error: unknown, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token!);
    }
  });
  failedQueue = [];
};

apiInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response.status === 401 && !originalRequest._retry && !originalRequest.url?.includes('/auth/sign-in')) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({resolve, reject});
        }).then((token) => {
          originalRequest.headers['Authorization'] = `Bearer ${token}`;
          return apiInstance(originalRequest);
        }).catch((err) => Promise.reject(err));
      }
      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const { data } = await apiInstance.post('/auth/refresh-token');
        processQueue(null, data.accessToken);
        originalRequest.headers['Authorization'] = `Bearer ${data.accessToken}`;
        return apiInstance(originalRequest);
      } catch (err) {
        console.log("Refresh token error: ", err);
        processQueue(err, null);
        window.location.href = ROUTES.SIGN_IN(window.location.href);
        return Promise.reject(err);
      } finally {
        isRefreshing = false;
      }
    }
    return Promise.reject(error)
  }
);

export const createInstance = async <T>(
  config: AxiosRequestConfig,
  options?: AxiosRequestConfig,
): Promise<T> => {
  const r = await apiInstance({
    ...config,
    ...options,
  });
  return r.data;
};

export const createInstanceWithFile = async <T>(
  config: AxiosRequestConfig,
  options?: AxiosRequestConfig,
): Promise<T> => {
  if (!config.data) {
    console.error("API-INSTANCE: Ошибка - данные не переданы");
    throw new Error("No data provided");
  }

  let formData: FormData;

  if (config.data instanceof FormData) {
    formData = config.data;
  } else if (config.data instanceof File) {
    formData = new FormData();
    formData.append("file", config.data);
  } else {
    formData = new FormData();
    if (typeof config.data === "object") {
      Object.keys(config.data).forEach((key) => {
        formData.append(key, config.data[key]);
      });
    }
  }

  const r = await apiInstance({
    ...config,
    ...options,
    headers: {
      ...config.headers,
      "Content-Type": "multipart/form-data",
    },
    data: formData,
  });

  return r.data;
};

export type BodyType<Data> = Data;

export type ErrorType<Error> = AxiosError<Error>;
