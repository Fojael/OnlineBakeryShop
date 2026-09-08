import { createSlice } from "@reduxjs/toolkit";

const initialState = {
    cartItems: [],
};

const cartSlice = createSlice({
    name: "cart",
    initialState,

    reducers: {

        setCart: (state, action) => {
            state.cartItems = Array.isArray(
                action.payload?.items
            )
                ? action.payload.items
                : [];
        },

        addToCart: (state, action) => {
            state.cartItems.push(action.payload);
        },

        removeFromCart: (state, action) => {
            state.cartItems =
                state.cartItems.filter(
                    (item) => item.id !== action.payload
                );
        },

        clearCart: (state) => {
            state.cartItems = [];
        },

    },
});

export const {
    setCart,
    addToCart,
    removeFromCart,
    clearCart,
} = cartSlice.actions;

export default cartSlice.reducer;