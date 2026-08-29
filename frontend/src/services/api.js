import axios from "axios";


const api = axios.create({

    baseURL:
        "http://127.0.0.1:8000/api",

    headers: {
        "Content-Type":
            "application/json",
    },

});


// ==========================================================
// REQUEST INTERCEPTOR
// ==========================================================

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

        return Promise.reject(
            error
        );

    }
);


export default api;