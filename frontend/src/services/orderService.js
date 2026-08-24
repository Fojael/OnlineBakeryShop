import api from "./api";

// =========================================================
// CUSTOMER ORDERS
// =========================================================

// Get logged-in customer's orders
export const getOrders = () => {
    return api.get("/orders/");
};

// =========================================================
// Get single customer order
// =========================================================

export const getOrder = (orderId) => {
    return api.get(`/orders/${orderId}/`);
};

// =========================================================
// Create order
// Matches Django backend:
// shipping_address
// payment_method
// =========================================================

export const createOrder = (orderData) => {
    return api.post("/orders/", {
        shipping_address:
            orderData.shipping_address,
        payment_method:
            orderData.payment_method,
    });
};

// =========================================================
// Cancel order
// =========================================================

export const cancelOrder = (orderId) => {
    return api.patch(
        `/orders/${orderId}/cancel/`
    );
};

// =========================================================
// ADMIN ORDERS
// =========================================================

// Get all orders
export const getAdminOrders = () => {
    return api.get("/orders/admin/");
};

// =========================================================
// Get single order
// =========================================================

export const getAdminOrder = (orderId) => {
    return api.get(
        `/orders/admin/${orderId}/`
    );
};

// =========================================================
// Update order status
// =========================================================

export const updateOrder = (
    orderId,
    orderData
) => {
    return api.patch(
        `/orders/admin/${orderId}/`,
        orderData
    );
};