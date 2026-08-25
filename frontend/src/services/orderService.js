import api from "./api";


// =========================================================
// CUSTOMER ORDERS
// =========================================================

// Get logged-in customer's orders
// GET /api/orders/
export const getOrders = () => {
    return api.get("/orders/");
};


// =========================================================
// GET SINGLE CUSTOMER ORDER
// GET /api/orders/:id/
// =========================================================

export const getOrder = (orderId) => {
    return api.get(
        `/orders/${orderId}/`
    );
};


// =========================================================
// CREATE CUSTOMER ORDER
// POST /api/orders/
//
// Backend expects:
//
// {
//     shipping_address,
//     payment_method
// }
//
// Totals, stock and cart are calculated by Django.
// =========================================================

export const createOrder = (orderData) => {

    return api.post(
        "/orders/",
        {
            shipping_address:
                orderData.shipping_address,

            payment_method:
                orderData.payment_method,
        }
    );
};


// =========================================================
// CANCEL CUSTOMER ORDER
// PATCH /api/orders/:id/cancel/
// =========================================================

export const cancelOrder = (orderId) => {

    return api.patch(
        `/orders/${orderId}/cancel/`
    );
};



// =========================================================
// ADMIN ORDERS
// =========================================================


// =========================================================
// GET ALL CUSTOMER ORDERS
// GET /api/orders/admin/
// =========================================================

export const getAdminOrders = () => {

    return api.get(
        "/orders/admin/"
    );
};


// =========================================================
// GET SINGLE ADMIN ORDER
// GET /api/orders/admin/:id/
// =========================================================

export const getAdminOrder = (orderId) => {

    return api.get(
        `/orders/admin/${orderId}/`
    );
};


// =========================================================
// UPDATE ORDER STATUS
// PATCH /api/orders/admin/:id/
//
// Example:
//
// updateOrder(orderId, {
//     status: "Processing"
// });
//
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