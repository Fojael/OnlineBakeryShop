import api from "./api";


// ==========================================================
// REGISTER
// ==========================================================

export const register = (
    data
) => {

    return api.post(
        "auth/register/",
        data
    );

};


// ==========================================================
// LOGIN
// ==========================================================

export const login = (
    data
) => {

    return api.post(
        "auth/login/",
        data
    );

};


// ==========================================================
// LOGOUT
// ==========================================================

export const logout = async (
    refreshToken
) => {

    try {

        if (refreshToken) {

            await api.post(
                "auth/logout/",
                {
                    refresh:
                        refreshToken,
                }
            );

        }

    } catch (error) {

        console.error(
            "Logout API error:",
            error
        );

    } finally {

        clearAuth();

    }

};


// ==========================================================
// PROFILE
// ==========================================================

export const getProfile = () => {

    return api.get(
        "auth/profile/"
    );

};


export const updateProfile = (
    data
) => {

    return api.put(
        "auth/profile/",
        data
    );

};


// ==========================================================
// CHANGE PASSWORD
// ==========================================================

export const changePassword = (
    data
) => {

    return api.post(
        "auth/change-password/",
        data
    );

};


// ==========================================================
// REFRESH TOKEN
// ==========================================================

export const refreshToken = (
    refresh
) => {

    return api.post(
        "auth/refresh/",
        {
            refresh,
        }
    );

};


// ==========================================================
// IS AUTHENTICATED
// ==========================================================

export const isAuthenticated = () => {

    return Boolean(

        localStorage.getItem(
            "access"
        )

        ||

        sessionStorage.getItem(
            "access"
        )

    );

};


// ==========================================================
// GET ACCESS TOKEN
// ==========================================================

export const getAccessToken = () => {

    return (

        localStorage.getItem(
            "access"
        )

        ||

        sessionStorage.getItem(
            "access"
        )

        ||

        null

    );

};


// ==========================================================
// GET REFRESH TOKEN
// ==========================================================

export const getRefreshToken = () => {

    return (

        localStorage.getItem(
            "refresh"
        )

        ||

        sessionStorage.getItem(
            "refresh"
        )

        ||

        null

    );

};


// ==========================================================
// CURRENT USER
// ==========================================================

export const getCurrentUser = () => {

    const user =

        localStorage.getItem(
            "user"
        )

        ||

        sessionStorage.getItem(
            "user"
        );


    if (!user) {

        return null;

    }


    try {

        return JSON.parse(
            user
        );

    } catch (error) {

        console.error(
            "Failed to parse stored user:",
            error
        );

        return null;

    }

};


// ==========================================================
// USER ROLE
// ==========================================================

export const getUserRole = () => {

    const user =
        getCurrentUser();

    return (
        user?.role
        ||
        null
    );

};


// ==========================================================
// USERNAME
// ==========================================================

export const getUsername = () => {

    const user =
        getCurrentUser();

    return (
        user?.username
        ||
        null
    );

};


// ==========================================================
// EMAIL
// ==========================================================

export const getEmail = () => {

    const user =
        getCurrentUser();

    return (
        user?.email
        ||
        null
    );

};


// ==========================================================
// CLEAR AUTH
// ==========================================================

export const clearAuth = () => {

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


    keys.forEach(
        (key) => {

            localStorage.removeItem(
                key
            );

            sessionStorage.removeItem(
                key
            );

        }
    );

};