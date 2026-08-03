import api from "./api";

// Get Categories
export const getCategories = () => {
    return api.get("categories/");
};

// Get Category
export const getCategory = (id) => {
    return api.get(`categories/${id}/`);
};

// Create Category
export const createCategory = (formData) => {
    return api.post(
        "categories/",
        formData,
        {
            headers: {
                "Content-Type":
                    "multipart/form-data",
            },
        }
    );
};

// Update Category
export const updateCategory = (
    id,
    formData
) => {
    return api.put(
        `categories/${id}/`,
        formData,
        {
            headers: {
                "Content-Type":
                    "multipart/form-data",
            },
        }
    );
};

// Delete Category
export const deleteCategory = (id) => {
    return api.delete(
        `categories/${id}/`
    );
};