import api from "./api";

// ==========================================================
// AUTH
// ==========================================================

export const register = (data) => {
    return api.post("auth/register/", data);
};

export const login = (data) => {
    return api.post("auth/login/", data);
};

export const logout = async (refreshToken) => {
    try {
        if (refreshToken) {
            await api.post("auth/logout/", {
                refresh: refreshToken,
            });
        }
    } finally {
        clearAuth();
    }
};

// ==========================================================
// PROFILE
// ==========================================================

export const getProfile = () => {
    return api.get("auth/profile/");
};

export const updateProfile = (data) => {
    return api.put("auth/profile/", data, {
        headers:
            data instanceof FormData
                ? {
                      "Content-Type": "multipart/form-data",
                  }
                : {
                      "Content-Type": "application/json",
                  },
    });
};

// ==========================================================
// PASSWORD
// ==========================================================

export const changePassword = (data) => {
    return api.post(
        "auth/change-password/",
        data
    );
};

// ==========================================================
// TOKEN
// ==========================================================

export const refreshToken = (refresh) => {
    return api.post("auth/refresh/", {
        refresh,
    });
};

// ==========================================================
// AUTHENTICATION HELPERS
// ==========================================================

export const isAuthenticated = () => {
    return Boolean(
        localStorage.getItem("access") ||
        sessionStorage.getItem("access")
    );
};

export const getAccessToken = () => {
    return (
        localStorage.getItem("access") ||
        sessionStorage.getItem("access") ||
        null
    );
};

export const getRefreshToken = () => {
    return (
        localStorage.getItem("refresh") ||
        sessionStorage.getItem("refresh") ||
        null
    );
};

// ==========================================================
// CURRENT USER
// ==========================================================

export const getCurrentUser = () => {
    const user =
        localStorage.getItem("user") ||
        sessionStorage.getItem("user");

    if (!user) {
        return null;
    }

    try {
        return JSON.parse(user);
    } catch (error) {
        console.error(
            "Failed to parse stored user:",
            error
        );

        return null;
    }
};

export const getUserRole = () => {
    const user = getCurrentUser();

    return user?.role || null;
};

export const getUsername = () => {
    const user = getCurrentUser();

    return user?.username || null;
};

export const getEmail = () => {
    const user = getCurrentUser();

    return user?.email || null;
};

// ==========================================================
// CLEAR AUTHENTICATION
// ==========================================================

export const clearAuth = () => {
    // localStorage
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    localStorage.removeItem("user");
    localStorage.removeItem("role");
    localStorage.removeItem("username");
    localStorage.removeItem("email");

    // sessionStorage
    sessionStorage.removeItem("access");
    sessionStorage.removeItem("refresh");
    sessionStorage.removeItem("user");
    sessionStorage.removeItem("role");
    sessionStorage.removeItem("username");
    sessionStorage.removeItem("email");
};