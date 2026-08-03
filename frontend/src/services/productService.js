import api from "./api";

// Get all products
export const getProducts = () => {
    return api.get("products/");
};

// Get one product
export const getProduct = (id) => {
    return api.get(`products/${id}/`);
};

// Create product with image
export const createProduct = (formData) => {
    return api.post("products/", formData, {
        headers: {
            "Content-Type": "multipart/form-data",
        },
    });
};

// Update product with image
export const updateProduct = (id, formData) => {
    return api.put(`products/${id}/`, formData, {
        headers: {
            "Content-Type": "multipart/form-data",
        },
    });
};

// Delete product
export const deleteProduct = (id) => {
    return api.delete(`products/${id}/`);
};
