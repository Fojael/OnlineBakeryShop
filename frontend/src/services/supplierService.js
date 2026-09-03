import api from "./api";

// ==========================================================
// SUPPLIER DASHBOARD
// ==========================================================

export const getSupplierDashboard = async () => {
    const response = await api.get(
        "suppliers/dashboard/"
    );

    return response.data;
};


// ==========================================================
// SUPPLIER PROFILE
// ==========================================================

export const getSupplierProfile = async () => {
    const response = await api.get(
        "suppliers/profile/"
    );

    return response.data;
};


// ==========================================================
// UPDATE SUPPLIER PROFILE
// ==========================================================

export const updateSupplierProfile = async (data) => {
    const response = await api.patch(
        "suppliers/profile/",
        data
    );

    return response.data;
};


// ==========================================================
// SUPPLIER PRODUCTS
// ==========================================================

export const getSupplierProducts = async () => {
    const response = await api.get(
        "suppliers/products/"
    );

    return response.data;
};


export const getSupplierProduct = async (id) => {
    const response = await api.get(
        `suppliers/products/${id}/`
    );

    return response.data;
};


export const createSupplierProduct = async (data) => {
    const response = await api.post(
        "suppliers/products/",
        data,
        {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        }
    );

    return response.data;
};


export const updateSupplierProduct = async (id, data) => {
    const response = await api.patch(
        `suppliers/products/${id}/`,
        data,
        {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        }
    );

    return response.data;
};


export const deleteSupplierProduct = async (id) => {
    const response = await api.delete(
        `suppliers/products/${id}/`
    );

    return response.data;
};


// ==========================================================
// ADMIN - GET ALL SUPPLIERS
// ==========================================================

export const getSuppliers = async () => {
    const response = await api.get(
        "suppliers/"
    );

    return response;
};


// ==========================================================
// ADMIN - GET SINGLE SUPPLIER
// ==========================================================

export const getSupplier = async (id) => {
    const response = await api.get(
        `suppliers/${id}/`
    );

    return response;
};


// ==========================================================
// ADMIN - CREATE SUPPLIER
// ==========================================================

export const createSupplier = async (data) => {
    const response = await api.post(
        "suppliers/",
        data
    );

    return response;
};


// ==========================================================
// ADMIN - UPDATE SUPPLIER
// ==========================================================

export const updateSupplier = async (
    id,
    data
) => {
    const response = await api.patch(
        `suppliers/${id}/`,
        data
    );

    return response;
};


// ==========================================================
// ADMIN - DELETE SUPPLIER
// ==========================================================

export const deleteSupplier = async (id) => {
    const response = await api.delete(
        `suppliers/${id}/`
    );

    return response;
};


// ==========================================================
// ADMIN - ACTIVATE SUPPLIER
// ==========================================================

export const activateSupplier = async (id) => {
    const response = await api.post(
        `suppliers/${id}/activate/`
    );

    return response;
};


// ==========================================================
// ADMIN - DEACTIVATE SUPPLIER
// ==========================================================

export const deactivateSupplier = async (id) => {
    const response = await api.post(
        `suppliers/${id}/deactivate/`
    );

    return response;
};

