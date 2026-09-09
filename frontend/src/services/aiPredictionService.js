import api from "./api";

export const getAIPredictionSummary = () => (
    api.get("ai-prediction/admin/summary/")
);

export const getAIReorderRecommendations = (horizonDays = 7) => (
    api.get(
        `ai-prediction/admin/reorder-recommendations/?horizon_days=${horizonDays}`,
    )
);

export const getCustomerRecommendations = (productId) => (
    api.get("ai-prediction/customer/recommendations/", {
        params: productId ? { product_id: productId } : undefined,
    })
);
