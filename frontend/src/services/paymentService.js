import api from "./api";


// ============================================================
// CREATE PAYMENT
// ============================================================

export const createPayment = async (orderId) => {

    const response = await api.post(
        `/payments/create/${orderId}/`
    );

    return response.data;
};


// ============================================================
// GET PAYMENT STATUS
// ============================================================

export const getPaymentStatus = async (orderId) => {

    const response = await api.get(
        `/payments/status/${orderId}/`
    );

    return response.data;
};


// ============================================================
// RETRY PAYMENT
// ============================================================

export const retryPayment = async (orderId) => {

    const response = await api.post(
        `/payments/retry/${orderId}/`
    );

    return response.data;
};