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

    try {

        console.log(
            "Creating order:",
            orderData
        );

        const response = await api.post(
            "/orders/",
            orderData
        );

        console.log(
            "Order created:",
            response.data
        );

        return response;

    } catch (error) {

        console.error(
            "Order creation API error:",
            error
        );

        console.error(
            "Backend response:",
            error.response?.data
        );

        console.error(
            "Backend status:",
            error.response?.status
        );

        throw error;
    }

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


// ============================================================
// ADMIN - GET DELIVERY RIDERS
// ============================================================

export const getDeliveryRiders = async () => {

    return await api.get(
        "/orders/admin/delivery-riders/"
    );

};


// ============================================================
// ADMIN - UPDATE DELIVERY RIDER
// ============================================================

export const updateDeliveryRider = async (
    riderId,
    payload
) => {

    return await api.patch(
        `/orders/admin/delivery-riders/${riderId}/update/`,
        payload
    );

};


// ============================================================
// ADMIN - TOGGLE DELIVERY RIDER STATUS
// ============================================================

export const toggleDeliveryRiderStatus = async (
    riderId,
    isActive
) => {

    return await api.post(
        `/orders/admin/delivery-riders/${riderId}/toggle-status/`,
        {
            is_active: isActive,
        }
    );

};


// ============================================================
// ADMIN - ASSIGN DELIVERY RIDER TO ORDER
// ============================================================

export const assignDeliveryRider = async (
    orderId,
    riderId
) => {

    return await api.post(
        `/orders/admin/${orderId}/assign-delivery/`,
        {
            rider_id: riderId,
        }
    );

};


// ============================================================
// SUPPLIER - GET ALL OWN ORDERS
// ============================================================

export const getSupplierOrders = async () => {

    return await api.get(
        "/orders/supplier/"
    );
};


// ============================================================
// SUPPLIER - GET SINGLE ORDER
// ============================================================

export const getSupplierOrder = async (
    orderId
) => {

    return await api.get(
        `/orders/supplier/${orderId}/`
    );
};


// ============================================================
// SUPPLIER - UPDATE ORDER ITEM STATUS
// ============================================================

export const updateSupplierOrderItemStatus = async (
    itemId,
    supplierStatus
) => {

    return await api.patch(
        `/orders/supplier/items/${itemId}/update/`,
        {
            supplier_status: supplierStatus,
        }
    );
};