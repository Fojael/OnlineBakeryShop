import api from "./api";

// Customer
export const getOrders = () =>
    api.get("/orders/");

export const getOrder = (id) =>
    api.get(`/orders/${id}/`);

export const createOrder = (data) =>
    api.post("/orders/", data);

// Admin
export const getAdminOrders = () =>
    api.get("/orders/admin/");

export const updateOrder = (id, data) =>
    api.put(`/orders/admin/${id}/`, data);

export const deleteOrder = (id) =>
    api.delete(`/orders/admin/${id}/`);
