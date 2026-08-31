import axios from "axios";


const api = axios.create({

    baseURL:
        "http://127.0.0.1:8000/api/",

    headers: {

        "Content-Type":
            "application/json",

    },

});


// ==========================================================
// GET ACCESS TOKEN
// ==========================================================

const getAccessToken = () => {

    return (

        localStorage.getItem("access") ||

        sessionStorage.getItem("access") ||

        null

    );

};


// ==========================================================
// GET REFRESH TOKEN
// ==========================================================

const getRefreshToken = () => {

    return (

        localStorage.getItem("refresh") ||

        sessionStorage.getItem("refresh") ||

        null

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

        const originalRequest =
            error.config;


        // ==================================================
        // NO CONFIG
        // ==================================================

        if (!originalRequest) {

            return Promise.reject(error);

        }


        // ==================================================
        // ACCESS TOKEN EXPIRED
        // ==================================================

        if (

            error.response?.status === 401 &&

            !originalRequest._retry

        ) {

            originalRequest._retry =
                true;


            const refresh =
                getRefreshToken();


            // ==================================================
            // NO REFRESH TOKEN
            // ==================================================

            if (!refresh) {

                clearAuthentication();

                return Promise.reject(error);

            }


            try {

                const response =
                    await axios.post(

                        "http://127.0.0.1:8000/api/auth/refresh/",

                        {
                            refresh,
                        }

                    );


                const newAccess =
                    response.data.access;


                if (!newAccess) {

                    throw new Error(
                        "New access token was not returned."
                    );

                }


                // ==================================================
                // SAVE NEW ACCESS TOKEN
                // ==================================================

                if (
                    localStorage.getItem("access")
                ) {

                    localStorage.setItem(
                        "access",
                        newAccess
                    );

                } else {

                    sessionStorage.setItem(
                        "access",
                        newAccess
                    );

                }


                // ==================================================
                // RETRY ORIGINAL REQUEST
                // ==================================================

                originalRequest.headers =
                    originalRequest.headers || {};


                originalRequest.headers.Authorization =
                    `Bearer ${newAccess}`;


                return api(
                    originalRequest
                );

            } catch (refreshError) {

                clearAuthentication();

                return Promise.reject(
                    refreshError
                );

            }

        }


        return Promise.reject(error);

    }

);


// ==========================================================
// CLEAR AUTHENTICATION
// ==========================================================

const clearAuthentication = () => {

    const keys = [

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


    keys.forEach((key) => {

        localStorage.removeItem(key);

        sessionStorage.removeItem(key);

    });

};


export default api;