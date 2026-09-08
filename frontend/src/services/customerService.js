import api from "./api";

export const getCustomers = (params = {}) =>
    api.get("auth/admin-customers/", { params });

export const getCustomer = (id) => api.get(`auth/admin-customers/${id}/`);

export const updateCustomerStatus = (id, isActive) =>
    api.patch(`auth/admin-customers/${id}/status/`, {
        is_active: isActive,
    });

export const getCustomerItems = (response) => {
    const data = response?.data;
    return Array.isArray(data) ? data : data?.results || [];
};