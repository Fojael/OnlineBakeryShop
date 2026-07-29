import api from "./api";

// Get all products
export const getProducts = () => {
    return api.get("products/");
};

// Get single product
export const getProduct = (id) => {
    return api.get(`products/${id}/`);
};

// Create product (Admin only)
export const createProduct = (data) => {
    return api.post("products/", data);
};

// Update product (Admin only)
export const updateProduct = (id, data) => {
    return api.put(`products/${id}/`, data);
};

// Delete product (Admin only)
export const deleteProduct = (id) => {
    return api.delete(`products/${id}/`);
};