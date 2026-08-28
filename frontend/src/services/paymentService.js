import api from "./api";

// ============================================================
// PAYMENT SERVICE
// ============================================================
//
// Backend base URL:
//
// http://127.0.0.1:8000/api/
//
// Payment endpoints:
//
// GET     /api/payments/
// POST    /api/payments/create/
// GET     /api/payments/<id>/
// GET     /api/payments/<id>/status/
// POST    /api/payments/<id>/confirm/
// POST    /api/payments/<id>/cancel/
// POST    /api/payments/<id>/retry/
//
// ============================================================


// ============================================================
// CREATE PAYMENT
// ============================================================
//
// Used for online payment methods:
//
// - bKash
// - Nagad
// - Rocket
// - Credit Card
//
// Example:
//
// const response = await createPayment({
//     order_id: orderId,
//     payment_method: "bKash"
// });
//
// ============================================================

export const createPayment = async (paymentData) => {
    return await api.post(
        "payments/create/",
        paymentData
    );
};


// ============================================================
// GET SINGLE PAYMENT
// ============================================================
//
// GET /api/payments/<paymentId>/
//
// ============================================================

export const getPayment = async (paymentId) => {
    if (!paymentId) {
        throw new Error(
            "Payment ID is required."
        );
    }

    return await api.get(
        `payments/${paymentId}/`
    );
};


// ============================================================
// GET PAYMENT STATUS
// ============================================================
//
// GET /api/payments/<paymentId>/status/
//
// Used by:
//
// PaymentSuccess.jsx
// PaymentFailed.jsx
// PaymentCancelled.jsx
//
// ============================================================

export const checkPaymentStatus = async (
    paymentId
) => {
    if (!paymentId) {
        throw new Error(
            "Payment ID is required."
        );
    }

    return await api.get(
        `payments/${paymentId}/status/`
    );
};


// ============================================================
// CONFIRM PAYMENT
// ============================================================
//
// POST /api/payments/<paymentId>/confirm/
//
// ============================================================

export const confirmPayment = async (
    paymentId,
    paymentData = {}
) => {
    if (!paymentId) {
        throw new Error(
            "Payment ID is required."
        );
    }

    return await api.post(
        `payments/${paymentId}/confirm/`,
        paymentData
    );
};


// ============================================================
// CANCEL PAYMENT
// ============================================================
//
// POST /api/payments/<paymentId>/cancel/
//
// ============================================================

export const cancelPayment = async (
    paymentId,
    paymentData = {}
) => {
    if (!paymentId) {
        throw new Error(
            "Payment ID is required."
        );
    }

    return await api.post(
        `payments/${paymentId}/cancel/`,
        paymentData
    );
};


// ============================================================
// RETRY PAYMENT
// ============================================================
//
// POST /api/payments/<paymentId>/retry/
//
// Used from PaymentFailed.jsx.
//
// ============================================================

export const retryPayment = async (
    paymentId,
    paymentData = {}
) => {
    if (!paymentId) {
        throw new Error(
            "Payment ID is required."
        );
    }

    return await api.post(
        `payments/${paymentId}/retry/`,
        paymentData
    );
};


// ============================================================
// GET CUSTOMER PAYMENTS
// ============================================================
//
// GET /api/payments/
//
// Returns payments belonging to the authenticated customer.
//
// ============================================================

export const getPayments = async () => {
    return await api.get(
        "payments/"
    );
};


// ============================================================
// PAYMENT ERROR MESSAGE
// ============================================================
//
// Converts Django/DRF errors into a readable message.
//
// ============================================================

export const getPaymentErrorMessage = (
    error
) => {
    const data =
        error?.response?.data;

    // --------------------------------------------------------
    // DETAIL
    // --------------------------------------------------------

    if (data?.detail) {
        return String(
            data.detail
        );
    }

    // --------------------------------------------------------
    // MESSAGE
    // --------------------------------------------------------

    if (data?.message) {
        return String(
            data.message
        );
    }

    // --------------------------------------------------------
    // ERROR
    // --------------------------------------------------------

    if (data?.error) {
        return String(
            data.error
        );
    }

    // --------------------------------------------------------
    // NON-FIELD ERROR
    // --------------------------------------------------------

    if (data?.non_field_errors) {
        return Array.isArray(
            data.non_field_errors
        )
            ? data.non_field_errors.join(" ")
            : String(
                data.non_field_errors
            );
    }

    // --------------------------------------------------------
    // VALIDATION ERRORS
    // --------------------------------------------------------

    if (
        data &&
        typeof data === "object"
    ) {
        const messages = Object.values(
            data
        )
            .flat(Infinity)
            .filter(
                (message) =>
                    message !== null &&
                    message !== undefined &&
                    String(message).trim() !== ""
            )
            .map(
                (message) =>
                    String(message)
            );

        if (messages.length > 0) {
            return messages.join(" ");
        }
    }

    // --------------------------------------------------------
    // NETWORK ERROR
    // --------------------------------------------------------

    if (
        error?.request &&
        !error?.response
    ) {
        return (
            "Unable to connect to the payment server. " +
            "Please check your internet connection and try again."
        );
    }

    // --------------------------------------------------------
    // DEFAULT
    // --------------------------------------------------------

    return (
        "Unable to process the payment. Please try again."
    );
};


// ============================================================
// EXTRACT PAYMENT REDIRECT URL
// ============================================================
//
// Supports different backend response structures.
//
// Possible responses:
//
// {
//     payment_url: "..."
// }
//
// OR:
//
// {
//     redirect_url: "..."
// }
//
// OR:
//
// {
//     checkout_url: "..."
// }
//
// OR:
//
// {
//     payment: {
//         payment_url: "..."
//     }
// }
//
// ============================================================

export const getPaymentRedirectUrl = (
    response
) => {
    const data =
        response?.data ?? response;

    return (
        data?.payment_url ||
        data?.redirect_url ||
        data?.checkout_url ||
        data?.gateway_url ||
        data?.url ||
        data?.payment?.payment_url ||
        data?.payment?.redirect_url ||
        data?.payment?.checkout_url ||
        data?.payment?.gateway_url ||
        data?.payment?.url ||
        null
    );
};


// ============================================================
// EXTRACT PAYMENT ID
// ============================================================

export const getPaymentId = (
    response
) => {
    const data =
        response?.data ?? response;

    return (
        data?.payment_id ??
        data?.paymentId ??
        data?.payment?.id ??
        data?.id ??
        null
    );
};


// ============================================================
// EXTRACT ORDER ID
// ============================================================

export const getOrderId = (
    response
) => {
    const data =
        response?.data ?? response;

    return (
        data?.order_id ??
        data?.orderId ??
        data?.payment?.order_id ??
        data?.payment?.order?.id ??
        data?.order?.id ??
        null
    );
};


// ============================================================
// EXTRACT TRANSACTION ID
// ============================================================

export const getTransactionId = (
    response
) => {
    const data =
        response?.data ?? response;

    return (
        data?.transaction_id ??
        data?.transactionId ??
        data?.trx_id ??
        data?.trxID ??
        data?.transaction?.id ??
        data?.payment?.transaction_id ??
        data?.payment?.transactionId ??
        data?.payment?.trx_id ??
        data?.payment?.trxID ??
        null
    );
};


// ============================================================
// EXTRACT PAYMENT STATUS
// ============================================================
//
// Handles responses such as:
//
// {
//     status: "success"
// }
//
// OR:
//
// {
//     payment: {
//         status: "success"
//     }
// }
//
// ============================================================

export const getPaymentStatus = (
    response
) => {
    const data =
        response?.data ?? response;

    return (
        data?.status ??
        data?.payment_status ??
        data?.paymentStatus ??
        data?.payment?.status ??
        data?.payment?.payment_status ??
        null
    );
};


// ============================================================
// PAYMENT STATUS NORMALIZER
// ============================================================

export const normalizePaymentStatus = (
    status
) => {
    if (!status) {
        return "";
    }

    return String(status)
        .toLowerCase()
        .trim()
        .replace(/[\s-]+/g, "_");
};


// ============================================================
// CHECK SUCCESSFUL PAYMENT
// ============================================================

export const isPaymentSuccessful = (
    status
) => {
    const normalizedStatus =
        normalizePaymentStatus(status);

    return [
        "success",
        "successful",
        "completed",
        "complete",
        "paid",
        "confirmed",
        "payment_success",
        "payment_successful",
    ].includes(
        normalizedStatus
    );
};


// ============================================================
// CHECK FAILED PAYMENT
// ============================================================

export const isPaymentFailed = (
    status
) => {
    const normalizedStatus =
        normalizePaymentStatus(status);

    return [
        "failed",
        "failure",
        "error",
        "declined",
        "rejected",
        "payment_failed",
        "payment_failure",
    ].includes(
        normalizedStatus
    );
};


// ============================================================
// CHECK CANCELLED PAYMENT
// ============================================================

export const isPaymentCancelled = (
    status
) => {
    const normalizedStatus =
        normalizePaymentStatus(status);

    return [
        "cancelled",
        "canceled",
        "cancel",
        "payment_cancelled",
        "payment_canceled",
    ].includes(
        normalizedStatus
    );
};


// ============================================================
// CHECK PENDING PAYMENT
// ============================================================

export const isPaymentPending = (
    status
) => {
    const normalizedStatus =
        normalizePaymentStatus(status);

    return [
        "pending",
        "processing",
        "initiated",
        "created",
        "awaiting_payment",
        "payment_pending",
    ].includes(
        normalizedStatus
    );
};


// ============================================================
// EXTRACT COMPLETE PAYMENT INFORMATION
// ============================================================
//
// Useful for payment result pages.
//
// ============================================================

export const extractPaymentData = (
    response
) => {
    return {
        paymentId:
            getPaymentId(response),

        orderId:
            getOrderId(response),

        transactionId:
            getTransactionId(response),

        status:
            getPaymentStatus(response),

        redirectUrl:
            getPaymentRedirectUrl(response),
    };
};


// ============================================================
// DEFAULT EXPORT
// ============================================================

const paymentService = {
    createPayment,

    getPayment,

    getPayments,

    checkPaymentStatus,

    confirmPayment,

    cancelPayment,

    retryPayment,

    getPaymentErrorMessage,

    getPaymentRedirectUrl,

    getPaymentId,

    getOrderId,

    getTransactionId,

    getPaymentStatus,

    normalizePaymentStatus,

    isPaymentSuccessful,

    isPaymentFailed,

    isPaymentCancelled,

    isPaymentPending,

    extractPaymentData,
};

export default paymentService;