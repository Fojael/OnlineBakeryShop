import api from "./api";

// ============================================================
// GET ALL CATEGORIES
// ============================================================

export const getCategories = () => {
    return api.get("categories/");
};

// ============================================================
// GET ONE CATEGORY
// ============================================================

export const getCategory = (id) => {
    return api.get(`categories/${id}/`);
};

// ============================================================
// CREATE CATEGORY
// ============================================================

export const createCategory = (data) => {
    return api.post("categories/", data);
};

// ============================================================
// UPDATE CATEGORY
// ============================================================

export const updateCategory = (id, data) => {
    return api.put(`categories/${id}/`, data);
};

// ============================================================
// DELETE CATEGORY
// ============================================================

export const deleteCategory = (id) => {
    return api.delete(`categories/${id}/`);
};