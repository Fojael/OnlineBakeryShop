import api from "./api";

// ============================================================
// GET CUSTOMER CART
// GET /api/cart/
// ============================================================

export const getCart = async () => {
    return await api.get("cart/");
};

// ============================================================
// ADD PRODUCT TO CART
// POST /api/cart/
// ============================================================

export const addToCart = async (
    productId,
    quantity = 1
) => {
    return await api.post("cart/", {
        product: productId,
        quantity,
    });
};

// ============================================================
// UPDATE CART ITEM QUANTITY
// PUT /api/cart/items/<item_id>/
// ============================================================

export const updateCartItem = async (
    itemId,
    quantity
) => {
    return await api.put(
        `cart/items/${itemId}/`,
        {
            quantity,
        }
    );
};

// ============================================================
// REMOVE CART ITEM
// DELETE /api/cart/items/<item_id>/
// ============================================================

export const removeCartItem = async (
    itemId
) => {
    return await api.delete(
        `cart/items/${itemId}/`
    );
};

// ============================================================
// CLEAR CART
// (Removes all items one by one)
// ============================================================

export const clearCart = async (
    cartItems = []
) => {
    await Promise.all(
        cartItems.map((item) =>
            removeCartItem(item.id)
        )
    );
};