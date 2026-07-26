import { createSlice } from "@reduxjs/toolkit";

const initialState = {
    user: null,
    access: localStorage.getItem("access"),
    refresh: localStorage.getItem("refresh"),
    isAuthenticated: !!localStorage.getItem("access"),
};

const authSlice = createSlice({
    name: "auth",
    initialState,

    reducers: {
        loginSuccess: (state, action) => {
            state.user = action.payload.user;
            state.access = action.payload.access;
            state.refresh = action.payload.refresh;
            state.isAuthenticated = true;
        },

        logout: (state) => {
            state.user = null;
            state.access = null;
            state.refresh = null;
            state.isAuthenticated = false;
        },
    },
});

export const { loginSuccess, logout } =
    authSlice.actions;

export default authSlice.reducer;