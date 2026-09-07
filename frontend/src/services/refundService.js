import api from "./api";

export const requestRefund = (orderId, payload) => (
    api.post("/orders/refunds/request/", {
        order_id: orderId,
        ...payload,
    })
);
