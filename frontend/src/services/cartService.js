import api from "./api";

// =========================================================
// CUSTOMER CART
// =========================================================

// GET logged-in customer's cart
export const getCart = () => {
    return api.get("/cart/");
};


// POST add product to cart
export const addToCart = (productId, quantity = 1) => {
    return api.post("/cart/", {
        product: productId,
        quantity,
    });
};


// PUT update cart item quantity
export const updateCartItem = (itemId, quantity) => {
    return api.put(`/cart/items/${itemId}/`, {
        quantity,
    });
};


// DELETE remove cart item
export const removeCartItem = (itemId) => {
    return api.delete(`/cart/items/${itemId}/`);
};