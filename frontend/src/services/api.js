import axios from "axios";

// ============================================================
// CONFIG
// ============================================================

const BASE_URL = "http://127.0.0.1:8000/api/";

const api = axios.create({
    baseURL: BASE_URL,
    headers: {
        Accept: "application/json",
    },
});

// ============================================================
// TOKEN HELPERS
// ============================================================

const getAccessToken = () =>
    localStorage.getItem("access");

const getRefreshToken = () =>
    localStorage.getItem("refresh");

const saveAccessToken = (token) => {
    localStorage.setItem("access", token);
};

const clearTokens = () => {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
};

const redirectToLogin = () => {
    window.location.href = "/login";
};

// ============================================================
// REQUEST INTERCEPTOR
// ============================================================

api.interceptors.request.use(
    (config) => {
        const accessToken = getAccessToken();

        if (!config.headers) {
            config.headers = {};
        }

        if (accessToken) {
            config.headers.Authorization =
                `Bearer ${accessToken}`;
        }

        return config;
    },
    (error) => Promise.reject(error)
);

// ============================================================
// REFRESH TOKEN STATE
// Prevent multiple refresh requests
// ============================================================

let isRefreshing = false;
let refreshSubscribers = [];

const subscribeTokenRefresh = (callback) => {
    refreshSubscribers.push(callback);
};

const onRefreshed = (token) => {
    refreshSubscribers.forEach((callback) =>
        callback(token)
    );

    refreshSubscribers = [];
};

// ============================================================
// RESPONSE INTERCEPTOR
// ============================================================

api.interceptors.response.use(
    (response) => response,

    async (error) => {
        const originalRequest = error.config;

        if (!originalRequest) {
            return Promise.reject(error);
        }

        if (originalRequest._retry) {
            return Promise.reject(error);
        }

        if (error.response?.status !== 401) {
            return Promise.reject(error);
        }

        originalRequest._retry = true;

        const refreshToken = getRefreshToken();

        if (!refreshToken) {
            clearTokens();
            redirectToLogin();

            return Promise.reject(error);
        }

        // ----------------------------------------------------
        // Wait if another refresh request is already running
        // ----------------------------------------------------

        if (isRefreshing) {
            return new Promise((resolve) => {
                subscribeTokenRefresh((token) => {
                    if (!originalRequest.headers) {
                        originalRequest.headers = {};
                    }

                    originalRequest.headers.Authorization =
                        `Bearer ${token}`;

                    resolve(api(originalRequest));
                });
            });
        }

        isRefreshing = true;

        try {
            const response = await axios.post(
                `${BASE_URL}token/refresh/`,
                {
                    refresh: refreshToken,
                }
            );

            const newAccessToken =
                response.data.access;

            saveAccessToken(newAccessToken);

            onRefreshed(newAccessToken);

            if (!originalRequest.headers) {
                originalRequest.headers = {};
            }

            originalRequest.headers.Authorization =
                `Bearer ${newAccessToken}`;

            return api(originalRequest);
        } catch (refreshError) {
            clearTokens();
            redirectToLogin();

            return Promise.reject(refreshError);
        } finally {
            isRefreshing = false;
        }
    }
);

export default api;