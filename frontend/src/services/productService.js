import api from "./api";

// ============================================================
// GET ALL PRODUCTS
// ============================================================

export const getProducts = () => {
    return api.get("/products/");
};

// ============================================================
// GET SINGLE PRODUCT
// ============================================================

export const getProduct = (id) => {
    return api.get(`/products/${id}/`);
};

// ============================================================
// CREATE PRODUCT
// ============================================================

export const createProduct = (productData) => {
    return api.post("/products/", productData);
};

// ============================================================
// UPDATE PRODUCT
// ============================================================

export const updateProduct = (id, productData) => {
    return api.put(`/products/${id}/`, productData);
};

// ============================================================
// DELETE PRODUCT
// ============================================================

export const deleteProduct = (id) => {
    return api.delete(`/products/${id}/`);
};