import api from "./api";

export const createOfflineSale = (payload) => (
    api.post("/orders/admin/offline/", payload)
);

export const getOfflineSales = (params = {}) => (
    api.get("/orders/admin/offline/history/", { params })
);

export const getOfflineSale = (orderId) => (
    api.get(`/orders/admin/offline/${orderId}/`)
);

export const getOfflineSalesReport = (params = {}) => (
    api.get("/reports/admin/offline-sales/", { params })
);

export const getDailyOfflineReport = (date, download = false) => (
    api.get("/reports/admin/offline/daily/", {
        params: { date, ...(download ? { download: "csv" } : {}) },
        responseType: download ? "blob" : "json",
    })
);

export const getWeeklyOfflineReport = (date, download = false) => (
    api.get("/reports/admin/offline/weekly/", {
        params: { date, ...(download ? { download: "csv" } : {}) },
        responseType: download ? "blob" : "json",
    })
);

export const getMonthlyOfflineReport = (year, month, download = false) => (
    api.get("/reports/admin/offline/monthly/", {
        params: { year, month, ...(download ? { download: "csv" } : {}) },
        responseType: download ? "blob" : "json",
    })
);
