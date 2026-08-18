import axios from "axios";

// ============================================================
// CONFIGURATION
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

const getAccessToken = () => {
    return localStorage.getItem("access");
};

const getRefreshToken = () => {
    return localStorage.getItem("refresh");
};

const saveAccessToken = (token) => {
    if (token) {
        localStorage.setItem("access", token);
    }
};

// ============================================================
// CLEAR AUTHENTICATION
// ============================================================

const clearTokens = () => {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    localStorage.removeItem("user");
    localStorage.removeItem("role");
    localStorage.removeItem("username");
    localStorage.removeItem("email");
};

// ============================================================
// REDIRECT TO LOGIN
// ============================================================

const redirectToLogin = () => {
    // Avoid repeatedly redirecting if already on login page
    if (window.location.pathname !== "/login") {
        window.location.href = "/login";
    }
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
    (error) => {
        return Promise.reject(error);
    }
);

// ============================================================
// REFRESH TOKEN MANAGEMENT
// ============================================================

// Prevent multiple refresh requests at the same time.
let isRefreshing = false;

let refreshSubscribers = [];

// ============================================================
// ADD REQUEST TO WAITING QUEUE
// ============================================================

const subscribeTokenRefresh = (callback) => {
    refreshSubscribers.push(callback);
};

// ============================================================
// SEND NEW TOKEN TO WAITING REQUESTS
// ============================================================

const onRefreshed = (newToken) => {
    refreshSubscribers.forEach((callback) => {
        callback(newToken);
    });

    refreshSubscribers = [];
};

// ============================================================
// RESPONSE INTERCEPTOR
// ============================================================

api.interceptors.response.use(
    // --------------------------------------------------------
    // SUCCESS
    // --------------------------------------------------------

    (response) => {
        return response;
    },

    // --------------------------------------------------------
    // ERROR
    // --------------------------------------------------------

    async (error) => {
        const originalRequest = error.config;

        // No request configuration
        if (!originalRequest) {
            return Promise.reject(error);
        }

        // ----------------------------------------------------
        // Only handle 401 Unauthorized
        // ----------------------------------------------------

        if (error.response?.status !== 401) {
            return Promise.reject(error);
        }

        // ----------------------------------------------------
        // Never retry the same request repeatedly
        // ----------------------------------------------------

        if (originalRequest._retry) {
            return Promise.reject(error);
        }

        originalRequest._retry = true;

        // ----------------------------------------------------
        // Get refresh token
        // ----------------------------------------------------

        const refreshToken = getRefreshToken();

        if (!refreshToken) {
            clearTokens();
            redirectToLogin();

            return Promise.reject(error);
        }

        // ----------------------------------------------------
        // If another request is already refreshing,
        // wait for the new access token.
        // ----------------------------------------------------

        if (isRefreshing) {
            return new Promise((resolve, reject) => {
                subscribeTokenRefresh((newToken) => {
                    if (!newToken) {
                        reject(error);
                        return;
                    }

                    if (!originalRequest.headers) {
                        originalRequest.headers = {};
                    }

                    originalRequest.headers.Authorization =
                        `Bearer ${newToken}`;

                    resolve(api(originalRequest));
                });
            });
        }

        // ----------------------------------------------------
        // Start token refresh
        // ----------------------------------------------------

        isRefreshing = true;

        try {
            /*
             * IMPORTANT:
             *
             * Do NOT use `api.post()` here.
             *
             * We use axios.post() directly so this request
             * does not trigger our own interceptor again.
             */

            const refreshResponse = await axios.post(
                `${BASE_URL}token/refresh/`,
                {
                    refresh: refreshToken,
                },
                {
                    headers: {
                        Accept: "application/json",
                        "Content-Type":
                            "application/json",
                    },
                }
            );

            const newAccessToken =
                refreshResponse.data?.access;

            // ------------------------------------------------
            // Validate new token
            // ------------------------------------------------

            if (!newAccessToken) {
                throw new Error(
                    "No access token returned from refresh endpoint."
                );
            }

            // ------------------------------------------------
            // Save new access token
            // ------------------------------------------------

            saveAccessToken(newAccessToken);

            // ------------------------------------------------
            // Notify waiting requests
            // ------------------------------------------------

            onRefreshed(newAccessToken);

            // ------------------------------------------------
            // Retry original request
            // ------------------------------------------------

            if (!originalRequest.headers) {
                originalRequest.headers = {};
            }

            originalRequest.headers.Authorization =
                `Bearer ${newAccessToken}`;

            return api(originalRequest);

        } catch (refreshError) {

            // ------------------------------------------------
            // Refresh failed
            // ------------------------------------------------

            console.error(
                "JWT refresh failed:",
                refreshError
            );

            // Reject all waiting requests
            refreshSubscribers.forEach(
                (callback) => {
                    callback(null);
                }
            );

            refreshSubscribers = [];

            clearTokens();
            redirectToLogin();

            return Promise.reject(refreshError);

        } finally {
            isRefreshing = false;
        }
    }
);

// ============================================================
// EXPORT
// ============================================================

export default api;