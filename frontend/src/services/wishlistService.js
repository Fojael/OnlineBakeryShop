import api from "./api";

// ===========================================
// GET WISHLIST
// GET /api/wishlist/
// ===========================================

export const getWishlist = async () => {
    return await api.get("wishlist/");
};

// ===========================================
// ADD TO WISHLIST
// POST /api/wishlist/
// ===========================================

export const addToWishlist = async (
    productId
) => {
    return await api.post(
        "wishlist/",
        {
            product: productId,
        }
    );
};

// ===========================================
// REMOVE FROM WISHLIST
// DELETE /api/wishlist/<id>/
// ===========================================

export const removeFromWishlist =
    async (itemId) => {
        return await api.delete(
            `wishlist/${itemId}/`
        );
    };