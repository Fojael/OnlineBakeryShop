import api from "./api";

// GET ALL
export const getSuppliers = () => {
    return api.get("suppliers/");
};

// GET ONE
export const getSupplier = (id) => {
    return api.get(`suppliers/${id}/`);
};

// CREATE
export const createSupplier = (data) => {
    return api.post("suppliers/", data);
};

// UPDATE
export const updateSupplier = (id, data) => {
    return api.put(`suppliers/${id}/`, data);
};

// DELETE
export const deleteSupplier = (id) => {
    return api.delete(`suppliers/${id}/`);
};