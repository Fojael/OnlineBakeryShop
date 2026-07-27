import api from "./api";

export const register = (data) => {
    return api.post("auth/register/", data);
};

export const login = (data) => {
    return api.post("auth/login/", data);
};

export const getProfile = () => {
    return api.get("auth/profile/");
};

export const changePassword = (data) => {
    return api.post(
        "auth/change-password/",
        data
    );
};

export const logout = (refresh) => {
    return api.post("auth/logout/", {
        refresh,
    });
};