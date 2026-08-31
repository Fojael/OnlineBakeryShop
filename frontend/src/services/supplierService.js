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