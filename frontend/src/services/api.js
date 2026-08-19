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

const clearAuthentication = () => {
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

let isRefreshing = false;

let refreshSubscribers = [];

// ============================================================
// SUBSCRIBE REQUEST
// ============================================================

const subscribeTokenRefresh = (callback) => {
    refreshSubscribers.push(callback);
};

// ============================================================
// NOTIFY WAITING REQUESTS
// ============================================================

const notifyTokenRefresh = (newToken) => {
    refreshSubscribers.forEach((callback) => {
        callback(newToken);
    });

    refreshSubscribers = [];
};

// ============================================================
// RESPONSE INTERCEPTOR
// ============================================================

api.interceptors.response.use(

    // ========================================================
    // SUCCESS
    // ========================================================

    (response) => {
        return response;
    },

    // ========================================================
    // ERROR
    // ========================================================

    async (error) => {
        const originalRequest = error.config;

        // ----------------------------------------------------
        // No request information
        // ----------------------------------------------------

        if (!originalRequest) {
            return Promise.reject(error);
        }

        // ----------------------------------------------------
        // Only handle 401
        // ----------------------------------------------------

        if (error.response?.status !== 401) {
            return Promise.reject(error);
        }

        // ----------------------------------------------------
        // Prevent infinite retry loop
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
            clearAuthentication();
            redirectToLogin();

            return Promise.reject(error);
        }

        // ====================================================
        // ANOTHER REQUEST IS ALREADY REFRESHING
        // ====================================================

        if (isRefreshing) {
            return new Promise(
                (resolve, reject) => {

                    subscribeTokenRefresh(
                        (newToken) => {

                            if (!newToken) {
                                reject(error);
                                return;
                            }

                            if (
                                !originalRequest.headers
                            ) {
                                originalRequest.headers = {};
                            }

                            originalRequest
                                .headers
                                .Authorization =
                                `Bearer ${newToken}`;

                            resolve(
                                api(originalRequest)
                            );
                        }
                    );
                }
            );
        }

        // ====================================================
        // START REFRESH
        // ====================================================

        isRefreshing = true;

        try {

            /*
             * IMPORTANT
             *
             * Django URL:
             *
             * /api/auth/refresh/
             *
             * Therefore:
             *
             * ${BASE_URL}auth/refresh/
             */

            const refreshResponse =
                await axios.post(
                    `${BASE_URL}auth/refresh/`,
                    {
                        refresh: refreshToken,
                    },
                    {
                        headers: {
                            Accept:
                                "application/json",

                            "Content-Type":
                                "application/json",
                        },
                    }
                );

            // ------------------------------------------------
            // GET NEW ACCESS TOKEN
            // ------------------------------------------------

            const newAccessToken =
                refreshResponse.data?.access;

            // ------------------------------------------------
            // VALIDATE TOKEN
            // ------------------------------------------------

            if (!newAccessToken) {
                throw new Error(
                    "Refresh endpoint did not return an access token."
                );
            }

            // ------------------------------------------------
            // SAVE NEW ACCESS TOKEN
            // ------------------------------------------------

            saveAccessToken(
                newAccessToken
            );

            // ------------------------------------------------
            // NOTIFY WAITING REQUESTS
            // ------------------------------------------------

            notifyTokenRefresh(
                newAccessToken
            );

            // ------------------------------------------------
            // UPDATE ORIGINAL REQUEST
            // ------------------------------------------------

            if (!originalRequest.headers) {
                originalRequest.headers = {};
            }

            originalRequest.headers.Authorization =
                `Bearer ${newAccessToken}`;

            // ------------------------------------------------
            // RETRY ORIGINAL REQUEST
            // ------------------------------------------------

            return api(originalRequest);

        } catch (refreshError) {

            console.error(
                "JWT refresh failed:",
                refreshError
            );

            // ------------------------------------------------
            // Reject waiting requests
            // ------------------------------------------------

            refreshSubscribers.forEach(
                (callback) => {
                    callback(null);
                }
            );

            refreshSubscribers = [];

            // ------------------------------------------------
            // Clear authentication
            // ------------------------------------------------

            clearAuthentication();

            // ------------------------------------------------
            // Redirect
            // ------------------------------------------------

            redirectToLogin();

            return Promise.reject(
                refreshError
            );

        } finally {

            isRefreshing = false;

        }
    }
);

// ============================================================
// EXPORT
// ============================================================

export default api;