import api from "./api";


// ============================================================
// CUSTOMER - GET ALL ORDERS
// ============================================================

export const getOrders = async () => {

    return await api.get(
        "/orders/"
    );

};


// ============================================================
// CUSTOMER - GET SINGLE ORDER
// ============================================================

export const getOrder = async (
    orderId
) => {

    return await api.get(
        `/orders/${orderId}/`
    );

};


// ============================================================
// CUSTOMER - CREATE ORDER
// ============================================================

export const createOrder = async (
    orderData
) => {

    return await api.post(
        "/orders/",
        orderData
    );

};


// ============================================================
// CUSTOMER - CANCEL ORDER
// ============================================================

export const cancelOrder = async (
    orderId
) => {

    return await api.post(
        `/orders/${orderId}/cancel/`
    );

};


// ============================================================
// ADMIN - GET ALL ORDERS
// ============================================================

export const getAdminOrders = async () => {

    return await api.get(
        "/orders/admin/"
    );

};


// ============================================================
// ADMIN - GET SINGLE ORDER
// ============================================================

export const getAdminOrder = async (
    orderId
) => {

    return await api.get(
        `/orders/admin/${orderId}/`
    );

};


// ============================================================
// ADMIN - UPDATE ORDER STATUS
// ============================================================

export const updateAdminOrderStatus = async (
    orderId,
    status
) => {

    return await api.patch(

        `/orders/admin/${orderId}/update/`,

        {
            status: status,
        }

    );

};