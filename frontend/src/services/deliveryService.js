import api from "./api";

// ==========================================================
// DELIVERY SERVICE
// ==========================================================

const deliveryService = {

    normalizeDelivery: (delivery) => ({
        ...delivery.order_details,
        ...delivery,
        order_id: delivery.order,
        delivery_id: delivery.id,
    }),

    // ======================================================
    // GET DELIVERY DASHBOARD
    // ======================================================

    getDashboard: async () => {
        const [dashboardResponse, deliveriesResponse] = await Promise.all([
            api.get("delivery/dashboard/"),
            api.get("delivery/my/"),
        ]);

        return {
            stats: dashboardResponse.data,
            deliveries: (deliveriesResponse.data || []).map(
                deliveryService.normalizeDelivery
            ),
        };
    },

    // ======================================================
    // GET MY DELIVERIES
    // ======================================================

    getOrders: async (status = "") => {
        const url = status
            ? `delivery/my/?status=${status}`
            : "delivery/my/";
        const response = await api.get(url);
        return (response.data || []).map(
            deliveryService.normalizeDelivery
        );
    },

    // ======================================================
    // GET DELIVERY ORDER DETAILS
    // ======================================================

    getOrderDetails: async (orderId) => {
        const response = await api.get(`delivery/${orderId}/`);
        return deliveryService.normalizeDelivery(response.data);
    },

    // ======================================================
    // UPDATE DELIVERY STATUS
    // ======================================================

    updateStatus: async (orderId, deliveryStatus) => {
        const response = await api.patch(`delivery/${orderId}/status/`, {
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
