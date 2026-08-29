import api from "./api";

// ==========================================================
// CUSTOMER ORDERS
// ==========================================================

// GET /api/orders/
export const getMyOrders = async () => {
    const response = await api.get("/orders/");
    return response.data;
};


// GET /api/orders/<orderId>/
export const getOrder = async (orderId) => {
    const response = await api.get(`/orders/${orderId}/`);
    return response.data;
};


// POST /api/orders/
export const createOrder = async (data) => {
    const response = await api.post("/orders/", data);
    return response.data;
};


// POST /api/orders/<orderId>/cancel/
export const cancelOrder = async (orderId) => {
    const response = await api.post(
        `/orders/${orderId}/cancel/`
    );
    return response.data;
};


// ==========================================================
// ADMIN ORDERS
// ==========================================================

// GET /api/orders/admin/
export const getAdminOrders = async () => {
    const response = await api.get("/orders/admin/");
    return response.data;
};


// GET SINGLE ADMIN ORDER
// Uses existing backend endpoint:
// GET /api/orders/<orderId>/
export const getAdminOrder = async (orderId) => {
    const response = await api.get(
        `/orders/${orderId}/`
    );
    return response.data;
};


// PATCH /api/orders/admin/<orderId>/
export const updateAdminOrderStatus = async (
    orderId,
    status
) => {
    const response = await api.patch(
        `/orders/admin/${orderId}/`,
        {
            status: status,
        }
    );

    return response.data;
};


// ==========================================================
// ALIASES
// ==========================================================

export const getOrders = getMyOrders;

export const getCustomerOrders = getMyOrders;

export const getOrderDetails = getOrder;

export const updateOrderStatus =
    updateAdminOrderStatus;


// ==========================================================
// DEFAULT EXPORT
// ==========================================================

const orderService = {

    getMyOrders,
    getOrder,
    createOrder,
    cancelOrder,

    getAdminOrders,
    getAdminOrder,
    updateAdminOrderStatus,

    getOrders,
    getCustomerOrders,
    getOrderDetails,
    updateOrderStatus,
};

export default orderService;