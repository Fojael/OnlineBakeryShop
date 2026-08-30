import api from "./api";


// ==========================================================
// CREATE PAYMENT
// ==========================================================

export const createPayment = async (
    orderId
) => {

    try {

        console.log(
            "Creating payment for order:",
            orderId
        );

        const response = await api.post(
            `/payments/orders/${orderId}/create/`
        );

        console.log(
            "Payment response:",
            response.data
        );

        return response.data;

    } catch (error) {

        console.error(
            "Create payment error:",
            error
        );

        console.error(
            "Payment backend response:",
            error.response?.data
        );

        console.error(
            "Payment backend status:",
            error.response?.status
        );

        throw error;
    }
};


// ==========================================================
// GET PAYMENT STATUS
// ==========================================================

export const getPaymentStatus = async (
    orderId
) => {

    try {

        const response = await api.get(
            `/payments/orders/${orderId}/status/`
        );

        return response.data;

    } catch (error) {

        console.error(
            "Get payment status error:",
            error
        );

        console.error(
            "Backend response:",
            error.response?.data
        );

        throw error;
    }
};


// ==========================================================
// RETRY PAYMENT
// ==========================================================

export const retryPayment = async (
    orderId
) => {

    try {

        console.log(
            "Retrying payment for order:",
            orderId
        );

        const response = await api.post(
            `/payments/orders/${orderId}/retry/`
        );

        console.log(
            "Retry payment response:",
            response.data
        );

        return response.data;

    } catch (error) {

        console.error(
            "Retry payment error:",
            error
        );

        console.error(
            "Backend response:",
            error.response?.data
        );

        throw error;
    }
};