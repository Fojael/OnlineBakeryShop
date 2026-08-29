// ==========================================================
// frontend/src/services/paymentService.js
// ==========================================================

import api from "./api";


// ==========================================================
// CREATE PAYMENT
// ==========================================================

export const createPayment = async (orderId) => {
    const response = await api.post(
        "/payments/create/",
        {
            order_id: orderId,
        }
    );

    return response.data;
};


// ==========================================================
// REDIRECT TO SSLCommerz GATEWAY
// ==========================================================

export const redirectToGateway = (gatewayUrl) => {

    if (!gatewayUrl) {
        throw new Error(
            "Payment gateway URL was not provided."
        );
    }

    window.location.href = gatewayUrl;
};


// ==========================================================
// VERIFY PAYMENT
// ==========================================================

export const verifyPayment = async (queryString) => {

    const response = await api.get(
        `/payments/success/?${queryString}`
    );

    return response.data;
};


// ==========================================================
// GET PAYMENT STATUS
// ==========================================================

export const getPaymentStatus = async (orderId) => {

    const response = await api.get(
        `/payments/status/${orderId}/`
    );

    return response.data;
};


// ==========================================================
// RETRY PAYMENT
// ==========================================================

export const retryPayment = async (orderId) => {

    const response = await api.post(
        "/payments/retry/",
        {
            order_id: orderId,
        }
    );

    return response.data;
};


// ==========================================================
// CANCEL PAYMENT
// ==========================================================

export const cancelPayment = async (orderId) => {

    const response = await api.post(
        "/payments/cancel/",
        {
            order_id: orderId,
        }
    );

    return response.data;
};


// ==========================================================
// DEFAULT EXPORT
// ==========================================================

const paymentService = {
    createPayment,
    redirectToGateway,
    verifyPayment,
    getPaymentStatus,
    retryPayment,
    cancelPayment,
};

export default paymentService;