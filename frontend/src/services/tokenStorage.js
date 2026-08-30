// ==========================================================
// GET ACCESS TOKEN
// ==========================================================

export const getAccessToken = () => {

    return (
        localStorage.getItem("access") ||
        sessionStorage.getItem("access") ||
        null
    );

};


// ==========================================================
// GET REFRESH TOKEN
// ==========================================================

export const getRefreshToken = () => {

    return (
        localStorage.getItem("refresh") ||
        sessionStorage.getItem("refresh") ||
        null
    );

};


// ==========================================================
// SAVE ACCESS TOKEN
// ==========================================================

export const saveAccessToken = (token) => {

    if (localStorage.getItem("refresh")) {

        localStorage.setItem(
            "access",
            token
        );

    } else {

        sessionStorage.setItem(
            "access",
            token
        );

    }

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

    keys.forEach((key) => {

        localStorage.removeItem(key);
        sessionStorage.removeItem(key);

    });

};