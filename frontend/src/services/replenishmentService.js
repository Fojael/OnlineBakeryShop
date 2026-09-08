import api from "./api";

export const getReplenishmentRequests = () => {
    return api.get("suppliers/replenishments/");
};

export const createReplenishmentRequest = (data) => {
    return api.post("suppliers/replenishments/", data);
};

export const getReplenishmentRequest = (requestId) => {
    return api.get(`suppliers/replenishments/${requestId}/`);
};

export const updateReplenishmentStatus = (requestId, status) => {
    return api.patch(
        `suppliers/replenishments/${requestId}/status/`,
        { status },
    );
};
