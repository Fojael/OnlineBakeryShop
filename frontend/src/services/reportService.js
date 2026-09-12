import api from "./api";

export const getOnlineSalesReport = (params = {}, download = false) => (
    api.get("reports/admin/online-sales/", {
        params: {
            ...params,
            ...(download ? { download: "csv" } : {}),
        },
        responseType: download ? "blob" : "json",
    })
);