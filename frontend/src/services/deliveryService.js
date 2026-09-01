import api from "./api";

// ==========================================================
// DELIVERY SERVICE
// ==========================================================

const deliveryService = {

    // ======================================================
    // GET DELIVERY DASHBOARD
    // ======================================================

    getDashboard: async () => {
        const response = await api.get("orders/delivery/dashboard/");
        return response.data;
    },

    // ======================================================
    // GET MY DELIVERIES
    // ======================================================

    getOrders: async (status = "") => {
        const url = status ? `orders/delivery/?status=${status}` : "orders/delivery/";
        const response = await api.get(url);
        return response.data;
    },

    // ======================================================
    // GET DELIVERY ORDER DETAILS
    // ======================================================

    getOrderDetails: async (orderId) => {
        const response = await api.get(`orders/delivery/${orderId}/`);
        return response.data;
    },

    // ======================================================
    // UPDATE DELIVERY STATUS
    // ======================================================

    updateStatus: async (orderId, deliveryStatus) => {
        const response = await api.patch(`orders/delivery/${orderId}/status/`, {
            status: deliveryStatus,
        });

        return response.data;
    },

    // ======================================================
    // GET DELIVERY PROFILE
    // ======================================================

    getProfile: async () => {
        const response = await api.get("auth/profile/");
        return response.data;
    },

    // ======================================================
    // UPDATE DELIVERY PROFILE
    // ======================================================

    updateProfile: async (data) => {
        const response = await api.patch("auth/profile/", data);
        return response.data;
    },
};

export default deliveryService;
