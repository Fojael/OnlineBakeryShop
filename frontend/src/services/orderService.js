import api from "./api";

// =========================================================
// CUSTOMER ORDERS
// =========================================================

export const getOrders = () => {
    return api.get("/orders/");
};

export const getOrder = (id) => {
    return api.get(`/orders/${id}/`);
};

export const createOrder = (orderData) => {
    return api.post("/orders/", orderData);
};

export const cancelOrder = (id) => {
    return api.patch(`/orders/${id}/cancel/`);
};

// =========================================================
// ADMIN ORDERS
// =========================================================

export const getAdminOrders = () => {
    return api.get("/orders/admin/");
};

// Admin gets one order
export const getAdminOrder = (id) => {
    return api.get(`/orders/admin/${id}/`);
};

// Admin updates order status
export const updateOrder = (id, data) => {
    return api.put(`/orders/admin/${id}/`, data);
};