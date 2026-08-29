import axios from "axios";

const api = axios.create({
    baseURL: "http://127.0.0.1:8000/api",
    headers: {
        "Content-Type": "application/json",
    },
});


// ==========================================================
// REQUEST INTERCEPTOR
// ==========================================================

api.interceptors.request.use(
    (config) => {

        const token = localStorage.getItem("access_token");

        if (token) {
            config.headers.Authorization =
                `Bearer ${token}`;
        }

        return config;
    },

    (error) => {
        return Promise.reject(error);
    }
);


// ==========================================================
// RESPONSE INTERCEPTOR
// ==========================================================

api.interceptors.response.use(
    (response) => {
        return response;
    },

    async (error) => {

        if (error.response?.status === 401) {

            console.warn(
                "Authentication expired."
            );

            // Do not automatically redirect here.
            // Authentication handling can be added later.
        }

        return Promise.reject(error);
    }
);


export default api;