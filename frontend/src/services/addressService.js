import api from "./api";

// ==========================================
// GET ALL ADDRESSES
// GET /api/address/
// ==========================================

export const getAddresses = async () => {
    return await api.get("address/");
};

// ==========================================
// GET SINGLE ADDRESS
// GET /api/address/:id/
// ==========================================

export const getAddress = async (id) => {
    return await api.get(`address/${id}/`);
};

// ==========================================
// CREATE ADDRESS
// POST /api/address/
// ==========================================

export const addAddress = async (addressData) => {
    return await api.post(
        "address/",
        addressData
    );
};

// ==========================================
// UPDATE ADDRESS
// PUT /api/address/:id/
// ==========================================

export const updateAddress = async (
    id,
    addressData
) => {
    return await api.put(
        `address/${id}/`,
        addressData
    );
};

// ==========================================
// DELETE ADDRESS
// DELETE /api/address/:id/
// ==========================================

export const deleteAddress = async (id) => {
    return await api.delete(
        `address/${id}/`
    );
};