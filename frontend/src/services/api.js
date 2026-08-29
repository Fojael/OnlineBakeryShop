import axios from "axios";


// ==========================================================
// API CONFIGURATION
// ==========================================================

const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL ||
    "http://127.0.0.1:8000/api";


// ==========================================================
// AXIOS INSTANCE
// ==========================================================

const api = axios.create({

    baseURL: API_BASE_URL,

    headers: {
        "Content-Type": "application/json",
    },
});


// ==========================================================
// TOKEN HELPERS
// ==========================================================

const getAccessToken = () => {

    return (
        localStorage.getItem("access") ||
        sessionStorage.getItem("access") ||
        null
    );
};


const getRefreshToken = () => {

    return (
        localStorage.getItem("refresh") ||
        sessionStorage.getItem("refresh") ||
        null
    );
};


// ==========================================================
// SAVE ACCESS TOKEN
// ==========================================================

const saveAccessToken = (
    token
) => {

    if (!token) {
        return;
    }

    if (
        localStorage.getItem("refresh")
    ) {

        localStorage.setItem(
            "access",
            token
        );

        return;
    }

    if (
        sessionStorage.getItem("refresh")
    ) {

        sessionStorage.setItem(
            "access",
            token
        );

        return;
    }

    localStorage.setItem(
        "access",
        token
    );
};


// ==========================================================
// CLEAR AUTHENTICATION
// ==========================================================

const clearAuthentication = () => {

    const localKeys = [
        "access",
        "refresh",
        "user",
        "role",
        "username",
        "email",
        "rememberMe",
        "access_token",
        "refresh_token",
    ];

    const sessionKeys = [
        "access",
        "refresh",
        "user",
        "role",
        "username",
        "email",
        "rememberMe",
        "access_token",
        "refresh_token",
    ];


    localKeys.forEach(
        (key) => {
            localStorage.removeItem(
                key
            );
        }
    );


    sessionKeys.forEach(
        (key) => {
            sessionStorage.removeItem(
                key
            );
        }
    );
};


// ==========================================================
// AUTHENTICATION EXPIRED EVENT
// ==========================================================

const notifyAuthenticationExpired = () => {

    window.dispatchEvent(
        new CustomEvent(
            "authentication-expired"
        )
    );
};


// ==========================================================
// REQUEST INTERCEPTOR
// ==========================================================

api.interceptors.request.use(

    (config) => {

        const token =
            getAccessToken();

        if (token) {

            config.headers =
                config.headers || {};

            config.headers.Authorization =
                `Bearer ${token}`;
        }

        return config;
    },

    (error) => {

        return Promise.reject(
            error
        );
    }
);


// ==========================================================
// REFRESH CONTROL
// ==========================================================

let isRefreshing = false;

let refreshSubscribers = [];


// ==========================================================
// SUBSCRIBE
// ==========================================================

const subscribeTokenRefresh = (
    callback
) => {

    refreshSubscribers.push(
        callback
    );
};


// ==========================================================
// NOTIFY SUCCESS
// ==========================================================

const onRefreshed = (
    newToken
) => {

    refreshSubscribers.forEach(
        (callback) => {
            callback(
                newToken,
                null
            );
        }
    );

    refreshSubscribers = [];
};


// ==========================================================
// NOTIFY FAILURE
// ==========================================================

const onRefreshFailed = (
    error
) => {

    refreshSubscribers.forEach(
        (callback) => {
            callback(
                null,
                error
            );
        }
    );

    refreshSubscribers = [];
};


// ==========================================================
// RESPONSE INTERCEPTOR
// ==========================================================

api.interceptors.response.use(

    // ======================================================
    // SUCCESS
    // ======================================================

    (response) => {

        return response;
    },


    // ======================================================
    // ERROR
    // ======================================================

    async (error) => {

        const originalRequest =
            error.config;


        // --------------------------------------------------
        // Only handle 401
        // --------------------------------------------------

        if (
            error.response?.status !== 401 ||
            !originalRequest
        ) {

            return Promise.reject(
                error
            );
        }


        // --------------------------------------------------
        // Prevent infinite retry
        // --------------------------------------------------

        if (
            originalRequest._retry
        ) {

            return Promise.reject(
                error
            );
        }


        // --------------------------------------------------
        // Do not refresh refresh endpoint
        // --------------------------------------------------

        if (
            originalRequest.url?.includes(
                "/auth/refresh/"
            )
        ) {

            clearAuthentication();

            notifyAuthenticationExpired();

            return Promise.reject(
                error
            );
        }


        // --------------------------------------------------
        // Get refresh token
        // --------------------------------------------------

        const refreshToken =
            getRefreshToken();


        // --------------------------------------------------
        // No refresh token
        // --------------------------------------------------

        if (!refreshToken) {

            clearAuthentication();

            notifyAuthenticationExpired();

            return Promise.reject(
                error
            );
        }


        // ==================================================
        // WAIT IF REFRESHING
        // ==================================================

        if (isRefreshing) {

            return new Promise(
                (
                    resolve,
                    reject
                ) => {

                    subscribeTokenRefresh(
                        (
                            newToken,
                            refreshError
                        ) => {

                            if (
                                !newToken
                            ) {

                                reject(
                                    refreshError ||
                                    error
                                );

                                return;
                            }


                            originalRequest._retry =
                                true;


                            originalRequest.headers =
                                originalRequest.headers ||
                                {};


                            originalRequest.headers.Authorization =
                                `Bearer ${newToken}`;


                            resolve(
                                api(
                                    originalRequest
                                )
                            );
                        }
                    );
                }
            );
        }


        // ==================================================
        // START REFRESH
        // ==================================================

        originalRequest._retry =
            true;

        isRefreshing =
            true;


        try {

            console.log(
                "Access token expired. Refreshing token..."
            );


            // ------------------------------------------------
            // IMPORTANT
            // Backend endpoint:
            //
            // POST /api/auth/refresh/
            // ------------------------------------------------

            const response =
                await axios.post(

                    `${API_BASE_URL}/auth/refresh/`,

                    {
                        refresh:
                            refreshToken,
                    },

                    {
                        headers: {
                            "Content-Type":
                                "application/json",
                        },
                    }
                );


            // ------------------------------------------------
            // New access token
            // ------------------------------------------------

            const newAccessToken =
                response.data?.access;


            if (!newAccessToken) {

                throw new Error(
                    "No access token returned from refresh endpoint."
                );
            }


            console.log(
                "Access token refreshed successfully."
            );


            // ------------------------------------------------
            // Save token
            // ------------------------------------------------

            saveAccessToken(
                newAccessToken
            );


            // ------------------------------------------------
            // Notify waiting requests
            // ------------------------------------------------

            onRefreshed(
                newAccessToken
            );


            // ------------------------------------------------
            // Retry original request
            // ------------------------------------------------

            originalRequest.headers =
                originalRequest.headers ||
                {};


            originalRequest.headers.Authorization =
                `Bearer ${newAccessToken}`;


            return api(
                originalRequest
            );

        } catch (
            refreshError
        ) {

            console.error(
                "Token refresh failed:",
                refreshError
            );


            onRefreshFailed(
                refreshError
            );


            clearAuthentication();


            notifyAuthenticationExpired();


            return Promise.reject(
                refreshError
            );

        } finally {

            isRefreshing =
                false;
        }
    }
);


// ==========================================================
// EXPORT
// ==========================================================

export default api;