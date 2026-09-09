import api from "./api";

export const getRefunds = () => api.get("/orders/refunds/");

export const requestRefund = (orderId, payload) => (
    api.post("/orders/refunds/request/", {
        order_id: orderId,
        ...payload,
    })
);

export const uploadRefundPhotos = (refundId, photos) => {
    const formData = new FormData();

    photos.forEach((photo) => formData.append("photos", photo));

    return api.post(
        `/orders/refunds/${refundId}/photos/`,
        formData,
        {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        },
    );
};
