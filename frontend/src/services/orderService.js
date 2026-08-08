import api from "./api";

// =========================================================
// CUSTOMER ORDERS
// =========================================================

// Get logged-in customer's orders
export const getOrders = () => {
    return api.get("/orders/");
};

// Get single order
export const getOrder = (orderId) => {
    return api.get("/orders/" + orderId + "/");
};

// Create order from cart
// Django calculates total_amount from the customer's cart.
export const createOrder = (orderData) => {
    return api.post("/orders/", {
        shipping_address: orderData.shipping_address,
        payment_method: orderData.payment_method,
    });
};

// Cancel order
export const cancelOrder = (orderId) => {
    return api.patch("/orders/" + orderId + "/cancel/");
};