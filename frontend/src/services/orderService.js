import api from "./api";


// ============================================================
// CUSTOMER - GET ALL ORDERS
// ============================================================

export const getOrders = async () => {
    return api.get("/orders/");
};


// ============================================================
// CUSTOMER - GET SINGLE ORDER
// ============================================================

export const getOrder = async (orderId) => {
    return api.get(`/orders/${orderId}/`);
};


// ============================================================
// CUSTOMER - CREATE ORDER
// ============================================================

export const createOrder = async (orderData) => {
    return api.post(
        "/orders/",
        orderData
    );
};


// ============================================================
// CUSTOMER - CANCEL ORDER
// ============================================================

export const cancelOrder = async (orderId) => {
    return api.post(
        `/orders/${orderId}/cancel/`
    );
};


// ============================================================
// ADMIN - GET ALL ORDERS
// ============================================================

export const getAdminOrders = async () => {
    return api.get(
        "/orders/admin/"
    );
};


// ============================================================
// ADMIN - GET SINGLE ORDER
// ============================================================

export const getAdminOrder = async (orderId) => {
    return api.get(
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
    return api.post(
        `/orders/admin/${orderId}/update/`,
        {
            status,
        }
    );
};


// ============================================================
// ADMIN - ACCEPT ORDER
// ============================================================

export const acceptAdminOrder = async (orderId) => {
    return api.post(
        `/orders/admin/${orderId}/accept/`
    );
};


// ============================================================
// ADMIN - GET DELIVERY RIDERS
// ============================================================

export const getDeliveryRiders = async () => {
    return api.get(
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
    return api.patch(
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
    return api.post(
        `/orders/admin/delivery-riders/${riderId}/toggle-status/`,
        {
            is_active: isActive,
        }
    );
};


// ============================================================
// ADMIN - ASSIGN SPECIFIC DELIVERY RIDER
// ============================================================
//
// IMPORTANT:
// Delivery assignment is handled by the DELIVERY app.
//
// Workflow:
//
// Order Ready
//      ↓
// Admin selects specific rider
//      ↓
// POST /delivery/admin/orders/<orderId>/create/
//      ↓
// Delivery created with ASSIGNED status
//      ↓
// Order becomes Assigned
//
// ============================================================

export const assignDeliveryRider = async (
    orderId,
    riderId
) => {
    return api.post(
        `/delivery/admin/orders/${orderId}/create/`,
        {
            rider_id: riderId,
        }
    );
};


// ============================================================
// SUPPLIER - GET ALL OWN ORDERS
// ============================================================

export const getSupplierOrders = async () => {
    return api.get(
        "/orders/supplier/"
    );
};


// ============================================================
// SUPPLIER - GET SINGLE ORDER
// ============================================================

export const getSupplierOrder = async (
    orderId
) => {
    return api.get(
        `/orders/supplier/${orderId}/`
    );
};


// ============================================================
// SUPPLIER - UPDATE ORDER ITEM STATUS
// ============================================================
//
// Allowed workflow:
//
// Pending
//    ↓
// Processing
//    ↓
// Ready
//
// There is intentionally NO Delivered status here.
// Delivery is handled by the rider.
//
// ============================================================

export const updateSupplierOrderItemStatus = async (
    itemId,
    supplierStatus
) => {
    return api.patch(
        `/orders/supplier/items/${itemId}/update/`,
        {
            supplier_status: supplierStatus,
        }
    );
};