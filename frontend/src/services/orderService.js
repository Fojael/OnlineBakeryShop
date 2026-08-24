import api from "./api";

// =========================================================
// CUSTOMER ORDERS
// =========================================================

// Get logged-in customer's orders
export const getOrders = () => {
    return api.get("/orders/");
};


// Get single customer order
export const getOrder = (orderId) => {
    return api.get(`/orders/${orderId}/`);
};


// Create order from customer's cart
export const createOrder = (orderData) => {
    return api.post("/orders/", {
        address_id: orderData.address_id,
        payment_method: orderData.payment_method,
    });
};


// Cancel customer's pending order
export const cancelOrder = (orderId) => {
    return api.patch(`/orders/${orderId}/cancel/`);
};


// =========================================================
// ADMIN ORDERS
// =========================================================

// Get all real customer orders
export const getAdminOrders = () => {
    return api.get("/orders/admin/");
};


// Get one order for admin
export const getAdminOrder = (orderId) => {
    return api.get(`/orders/admin/${orderId}/`);
};


// Update order status
export const updateOrder = (orderId, orderData) => {
    return api.patch(
        `/orders/admin/${orderId}/`,
        orderData
    );
};