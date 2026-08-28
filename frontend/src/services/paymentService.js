import api from "./api";


// ============================================================
// CREATE PAYMENT
// ============================================================

export const createPayment = async (
    orderId,
    paymentData = {}
) => {

    if (!orderId) {

        throw new Error(
            "Order ID is required."
        );

    }


    return await api.post(
        `payments/create/${orderId}/`,
        paymentData
    );

};


// ============================================================
// GET SINGLE PAYMENT
// ============================================================

export const getPayment = async (
    paymentId
) => {

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

export const getPayments = async () => {

    return await api.get(
        "payments/"
    );

};


// ============================================================
// GET PAYMENT ERROR MESSAGE
// ============================================================

export const getPaymentErrorMessage = (
    error
) => {

    const data =
        error?.response?.data;


    // ----------------------------------------------------------
    // DETAIL
    // ----------------------------------------------------------

    if (data?.detail) {

        return String(
            data.detail
        );

    }


    // ----------------------------------------------------------
    // MESSAGE
    // ----------------------------------------------------------

    if (data?.message) {

        return String(
            data.message
        );

    }


    // ----------------------------------------------------------
    // ERROR
    // ----------------------------------------------------------

    if (data?.error) {

        return String(
            data.error
        );

    }


    // ----------------------------------------------------------
    // NON FIELD ERRORS
    // ----------------------------------------------------------

    if (data?.non_field_errors) {

        return Array.isArray(
            data.non_field_errors
        )
            ? data.non_field_errors.join(" ")
            : String(
                data.non_field_errors
            );

    }


    // ----------------------------------------------------------
    // DJANGO REST FRAMEWORK VALIDATION ERRORS
    // ----------------------------------------------------------

    if (
        data &&
        typeof data === "object"
    ) {

        const messages =
            Object.values(data)
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


    // ----------------------------------------------------------
    // NETWORK ERROR
    // ----------------------------------------------------------

    if (
        error?.request &&
        !error?.response
    ) {

        return (
            "Unable to connect to the payment server. " +
            "Please check your internet connection and try again."
        );

    }


    // ----------------------------------------------------------
    // DEFAULT
    // ----------------------------------------------------------

    return (
        "Unable to process the payment. Please try again."
    );

};


// ============================================================
// GET PAYMENT REDIRECT URL
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
// GET PAYMENT ID
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

        data?.payment?.payment_id ??

        data?.payment?.paymentId ??

        data?.id ??

        null

    );

};


// ============================================================
// GET ORDER ID
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

        data?.payment?.orderId ??

        data?.payment?.order?.id ??

        data?.order?.id ??

        null

    );

};


// ============================================================
// GET TRANSACTION ID
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

        data?.payment?.transaction?.id ??

        null

    );

};


// ============================================================
// GET PAYMENT STATUS
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

        data?.payment?.paymentStatus ??

        null

    );

};


// ============================================================
// NORMALIZE PAYMENT STATUS
// ============================================================

export const normalizePaymentStatus = (
    status
) => {

    if (
        status === null ||
        status === undefined
    ) {

        return "";

    }


    return String(status)
        .toLowerCase()
        .trim()
        .replace(/[\s-]+/g, "_");

};


// ============================================================
// CHECK SUCCESS
// ============================================================

export const isPaymentSuccessful = (
    status
) => {

    const normalizedStatus =
        normalizePaymentStatus(
            status
        );


    return [

        "success",

        "successful",

        "completed",

        "complete",

        "paid",

        "confirmed",

        "payment_success",

        "payment_successful",

        "succeeded",

        "approved",

    ].includes(
        normalizedStatus
    );

};


// ============================================================
// CHECK FAILED
// ============================================================

export const isPaymentFailed = (
    status
) => {

    const normalizedStatus =
        normalizePaymentStatus(
            status
        );


    return [

        "failed",

        "failure",

        "error",

        "declined",

        "rejected",

        "payment_failed",

        "payment_failure",

        "cancelled_by_gateway",

    ].includes(
        normalizedStatus
    );

};


// ============================================================
// CHECK CANCELLED
// ============================================================

export const isPaymentCancelled = (
    status
) => {

    const normalizedStatus =
        normalizePaymentStatus(
            status
        );


    return [

        "cancelled",

        "canceled",

        "cancel",

        "payment_cancelled",

        "payment_canceled",

        "user_cancelled",

        "user_canceled",

    ].includes(
        normalizedStatus
    );

};


// ============================================================
// CHECK PENDING
// ============================================================

export const isPaymentPending = (
    status
) => {

    const normalizedStatus =
        normalizePaymentStatus(
            status
        );


    return [

        "pending",

        "processing",

        "initiated",

        "created",

        "awaiting_payment",

        "payment_pending",

        "in_progress",

        "initiated_payment",

    ].includes(
        normalizedStatus
    );

};


// ============================================================
// EXTRACT COMPLETE PAYMENT DATA
// ============================================================

export const extractPaymentData = (
    response
) => {

    return {

        paymentId:
            getPaymentId(
                response
            ),

        orderId:
            getOrderId(
                response
            ),

        transactionId:
            getTransactionId(
                response
            ),

        status:
            getPaymentStatus(
                response
            ),

        redirectUrl:
            getPaymentRedirectUrl(
                response
            ),

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