import axios from "axios";


// ============================================================
// AXIOS INSTANCE
// ============================================================

const api = axios.create({
    baseURL: "http://127.0.0.1:8000/api/",
    headers: {
        Accept: "application/json",
    },
});


// ============================================================
// REQUEST INTERCEPTOR
// ============================================================

api.interceptors.request.use(
    (config) => {

        const accessToken =
            localStorage.getItem(
                "access"
            );

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
// RESPONSE INTERCEPTOR
// ============================================================

api.interceptors.response.use(

    (response) => {
        return response;
    },

    async (error) => {

        if (
            error.response?.status === 401
        ) {

            console.error(
                "Authentication expired."
            );
        }

        return Promise.reject(
            error
        );
    }
);


export default api;