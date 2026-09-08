import api from "./api";
import { store } from "../redux/store";
import { setCart } from "../redux/cartSlice";

const syncCartState = (response) => {
    store.dispatch(setCart(response.data));
    return response;
};

// ============================================================
// GET CUSTOMER CART
// GET /api/cart/
// ============================================================

export const getCart = async () => {
    const response = await api.get("cart/");
    return syncCartState(response);
};

// ============================================================
// ADD PRODUCT TO CART
// POST /api/cart/
// ============================================================

export const addToCart = async (
    productId,
    quantity = 1
) => {
    const response = await api.post("cart/", {
        product: productId,
        quantity,
    });
    return syncCartState(response);
};

// ============================================================
// UPDATE CART ITEM QUANTITY
// PUT /api/cart/items/<item_id>/
// ============================================================

export const updateCartItem = async (
    itemId,
    quantity
) => {
    const response = await api.put(
        `cart/items/${itemId}/`,
        {
            quantity,
        }
    );
    return syncCartState(response);
};

// ============================================================
// REMOVE CART ITEM
// DELETE /api/cart/items/<item_id>/
// ============================================================

export const removeCartItem = async (
    itemId
) => {
    const response = await api.delete(
        `cart/items/${itemId}/`
    );
    return syncCartState(response);
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