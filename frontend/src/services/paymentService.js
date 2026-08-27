import axios from "axios";

// ==========================================================
// API BASE URL
// ==========================================================

const API_BASE_URL =
    import.meta.env.VITE_API_URL ||
    "http://127.0.0.1:8000/api";


// ==========================================================
// AXIOS INSTANCE
// ==========================================================

const paymentAPI = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        "Content-Type": "application/json",
    },
});


// ==========================================================
// REQUEST INTERCEPTOR
// ==========================================================

paymentAPI.interceptors.request.use(
    (config) => {
        const token =
            localStorage.getItem("access_token");

        if (token) {
            config.headers.Authorization =
                `Bearer ${token}`;
        }

        return config;
    },

    (error) => {
        return Promise.reject(error);
    }
);


// ==========================================================
// CREATE ORDER
// ==========================================================

export const createOrder = async ({
    shipping_address,
    payment_method,
}) => {
    const response = await paymentAPI.post(
        "/orders/",
        {
            shipping_address,
            payment_method,
        }
    );

    return response.data;
};


// ==========================================================
// CREATE SSLCommerz PAYMENT
// ==========================================================

export const createPayment = async (orderId) => {
    const response = await paymentAPI.post(
        `/payments/create/${orderId}/`
    );

    return response.data;
};


// ==========================================================
// GET CUSTOMER ORDERS
// ==========================================================

export const getOrders = async () => {
    const response = await paymentAPI.get(
        "/orders/"
    );

    return response.data;
};


// ==========================================================
// GET SINGLE ORDER
// ==========================================================

export const getOrder = async (orderId) => {
    const response = await paymentAPI.get(
        `/orders/${orderId}/`
    );

    return response.data;
};


// ==========================================================
// CANCEL ORDER
// ==========================================================

export const cancelOrder = async (orderId) => {
    const response = await paymentAPI.post(
        `/orders/${orderId}/cancel/`
    );

    return response.data;
};


// ==========================================================
// EXPORT AXIOS INSTANCE
// ==========================================================

export default paymentAPI;