import { useEffect, useState } from "react";

import DashboardLayout from "../../../layouts/DashboardLayout";
import api from "../../../services/api";
import { getAIReorderRecommendations } from "../../../services/aiPredictionService";
import { createReplenishmentRequest } from "../../../services/replenishmentService";

const AIPrediction = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [training, setTraining] = useState(false);
    const [recommendations, setRecommendations] = useState([]);
    const [recommendationLoading, setRecommendationLoading] = useState(true);
    const [recommendationError, setRecommendationError] = useState("");
    const [drafts, setDrafts] = useState({});
    const [creatingProductId, setCreatingProductId] = useState(null);

    useEffect(() => {
        let ignore = false;

        api.get("ai-prediction/admin/summary/")
            .then((response) => {
                if (!ignore) setData(response.data);
            })
            .catch((requestError) => setError(
                requestError.response?.data?.detail ||
                "Failed to load AI sales prediction."
            ))
            .finally(() => setLoading(false));

        getAIReorderRecommendations()
            .then((response) => {
                if (!ignore) setRecommendations(response.data?.recommendations || []);
            })
            .catch((requestError) => {
                if (!ignore) {
                    setRecommendationError(
                        requestError.response?.status === 503
                            ? "Train the forecast model before reviewing reorder recommendations."
                            : requestError.response?.data?.detail ||
                            "Failed to load reorder recommendations."
                    );
                }
            })
            .finally(() => {
                if (!ignore) setRecommendationLoading(false);
            });

        return () => {
            ignore = true;
        };
    }, []);

    const trainModel = async () => {
        setTraining(true);
        setError("");
        try {
            const response = await api.post("ai-prediction/admin/train/");
            setData(response.data.forecast);
            const recommendationResponse = await getAIReorderRecommendations();
            setRecommendations(recommendationResponse.data?.recommendations || []);
            setRecommendationError("");
        } catch (requestError) {
            setError(
                requestError.response?.data?.detail ||
                "Unable to train the sales forecast model."
            );
        } finally {
            setTraining(false);
        }
    };

    const getDraft = (recommendation) => (
        drafts[recommendation.product_id] || {
            supplier: recommendation.supplier_id
                ? String(recommendation.supplier_id)
                : "",
            quantity: String(recommendation.recommended_reorder_quantity),
        }
    );

    const updateDraft = (recommendation, field, value) => {
        const productId = recommendation.product_id;
        setDrafts((previous) => ({
            ...previous,
            [productId]: {
                ...getDraft(recommendation),
                [field]: value,
            },
        }));
    };

    const createRequestFromRecommendation = async (recommendation) => {
        const draft = getDraft(recommendation);
        const quantity = Number(draft.quantity);

        if (!draft.supplier) {
            setRecommendationError("Select an active approved supplier first.");
            return;
        }

        if (!Number.isInteger(quantity) || quantity <= 0) {
            setRecommendationError("Requested quantity must be a whole number greater than zero.");
            return;
        }

        const confirmed = window.confirm(
            `Create a replenishment request for ${quantity} units of ${recommendation.product_name}?`
        );
        if (!confirmed) return;

        try {
            setCreatingProductId(recommendation.product_id);
            setRecommendationError("");
            await createReplenishmentRequest({
                supplier: Number(draft.supplier),
                product: recommendation.product_id,
                requested_quantity: quantity,
                notes: "Created after admin review of an AI recommendation.",
            });
            const recommendationResponse = await getAIReorderRecommendations();
            setRecommendations(recommendationResponse.data?.recommendations || []);
        } catch (requestError) {
            setRecommendationError(
                requestError.response?.data?.detail ||
                "Failed to create replenishment request."
            );
        } finally {
            setCreatingProductId(null);
        }
    };

    const forecastDays = data?.forecast?.daily || [];
    const maxForecast = Math.max(
        ...forecastDays.map((item) => item.predicted_units),
        1
    );

    return (
        <DashboardLayout>
            <div className="container-fluid py-4">
                <div className="d-flex flex-wrap justify-content-between align-items-start gap-3">
                    <div>
                        <h2>AI Sales Forecast</h2>
                        <p className="text-muted">Forecasts from historical delivered sales and inventory recommendations.</p>
                    </div>
                    <button className="btn btn-primary" onClick={trainModel} disabled={loading || training}>
                        {training ? "Training..." : "Train Model"}
                    </button>
                </div>
                {loading && <div className="py-4">Loading saved forecast...</div>}
                {error && <div className="alert alert-danger">{error}</div>}
                {data && (
                    <>
                        <div className="row g-3 mb-4">
                            <div className="col-md-3"><div className="card p-3"><small>Historical days</small><strong>{data.summary.historical_days}</strong></div></div>
                            <div className="col-md-3"><div className="card p-3"><small>7-day forecast</small><strong>{data.summary.forecast_weekly_units} units</strong></div></div>
                            <div className="col-md-3"><div className="card p-3"><small>30-day forecast</small><strong>{data.summary.forecast_monthly_units} units</strong></div></div>
                            <div className="col-md-3"><div className="card p-3"><small>Model MAE</small><strong>{data.pipeline.evaluation.mae ?? "N/A"}</strong></div></div>
                        </div>
                        <div className="card mb-4 p-3"><strong>Pipeline:</strong> {data.pipeline.extraction} / {data.pipeline.model}</div>
                        <h4>Daily Forecast</h4>
                        <div className="d-flex align-items-end gap-1 border rounded p-3 mb-3" style={{ minHeight: "180px" }}>
                            {forecastDays.slice(0, 14).map((item) => (
                                <div className="flex-fill text-center" key={`chart-${item.date}`}>
                                    <div
                                        className="bg-primary rounded-top"
                                        style={{
                                            height: `${Math.max(4, (item.predicted_units / maxForecast) * 120)}px`,
                                        }}
                                        title={`${item.date}: ${item.predicted_units} units`}
                                    />
                                    <small className="text-muted">{item.date.slice(5)}</small>
                                </div>
                            ))}
                        </div>
                        <div className="table-responsive mb-4">
                            <table className="table table-sm"><tbody>{data.forecast.daily.slice(0, 7).map((item) => <tr key={item.date}><td>{item.date}</td><td>{item.day_of_week}</td><td>{item.predicted_units} units</td></tr>)}</tbody></table>
                        </div>
                        <h4>Actual vs Forecast</h4>
                        <div className="table-responsive mb-4">
                            <table className="table table-sm"><thead><tr><th>Date</th><th>Actual</th><th>Predicted</th></tr></thead><tbody>{(data.actual_vs_predicted || []).slice(-14).map((item) => <tr key={item.date}><td>{item.date}</td><td>{item.actual_units}</td><td>{item.predicted_units}</td></tr>)}</tbody></table>
                        </div>
                        <h4>Product Demand and Inventory Recommendations</h4>
                        <div className="table-responsive">
                            <table className="table table-striped"><thead><tr><th>Product</th><th>Tomorrow</th><th>Next 7 Days</th><th>Next 30 Days</th><th>Current Stock</th><th>Shortage</th><th>Recommendation</th></tr></thead><tbody>{data.predictions.map((item) => <tr key={item.product_id}><td>{item.product_name}</td><td>{item.tomorrow_units}</td><td>{item.next_7_days_units}</td><td>{item.next_30_days_units}</td><td>{item.current_stock}</td><td>{item.expected_shortage}</td><td>{item.recommended_action}</td></tr>)}</tbody></table>
                        </div>
                        <h4 className="mt-4">Admin Reorder Recommendations</h4>
                        {recommendationError && <div className="alert alert-warning">{recommendationError}</div>}
                        {recommendationLoading ? (
                            <div className="py-3">Loading reorder recommendations...</div>
                        ) : recommendations.length === 0 ? (
                            <div className="alert alert-success">No replenishment requests are currently recommended.</div>
                        ) : (
                            <div className="table-responsive">
                                <table className="table table-bordered align-middle">
                                    <thead>
                                        <tr>
                                            <th>Product</th>
                                            <th>Supplier</th>
                                            <th>Current Stock</th>
                                            <th>Predicted Demand</th>
                                            <th>Projected Stock</th>
                                            <th>Risk</th>
                                            <th>Reason</th>
                                            <th>Quantity</th>
                                            <th>Action</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {recommendations.map((recommendation) => {
                                            const draft = getDraft(recommendation);
                                            const supplierUnavailable = !recommendation.supplier_available;
                                            return (
                                                <tr key={recommendation.product_id}>
                                                    <td>{recommendation.product_name}</td>
                                                    <td>
                                                        <select
                                                            className="form-select"
                                                            value={draft.supplier}
                                                            onChange={(event) => updateDraft(recommendation, "supplier", event.target.value)}
                                                            disabled={supplierUnavailable || creatingProductId === recommendation.product_id}
                                                        >
                                                            <option value="">
                                                                {supplierUnavailable ? "No active supplier" : "Select supplier"}
                                                            </option>
                                                            {!supplierUnavailable && (
                                                                <option value={String(recommendation.supplier_id)}>
                                                                    {recommendation.supplier_name || "Recommended supplier"}
                                                                </option>
                                                            )}
                                                        </select>
                                                    </td>
                                                    <td>{recommendation.current_stock}</td>
                                                    <td>{recommendation.predicted_demand}</td>
                                                    <td>{recommendation.projected_stock}</td>
                                                    <td>{recommendation.risk_level}</td>
                                                    <td>{recommendation.reason}</td>
                                                    <td>
                                                        <input
                                                            className="form-control"
                                                            type="number"
                                                            min="1"
                                                            step="1"
                                                            value={draft.quantity}
                                                            onChange={(event) => updateDraft(recommendation, "quantity", event.target.value)}
                                                            disabled={creatingProductId === recommendation.product_id}
                                                        />
                                                    </td>
                                                    <td>
                                                        <button
                                                            type="button"
                                                            className="btn btn-primary btn-sm"
                                                            onClick={() => createRequestFromRecommendation(recommendation)}
                                                            disabled={supplierUnavailable || creatingProductId === recommendation.product_id}
                                                        >
                                                            {creatingProductId === recommendation.product_id ? "Creating..." : "Create Replenishment Request"}
                                                        </button>
                                                    </td>
                                                </tr>
                                            );
                                        })}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </>
                )}
            </div>
        </DashboardLayout>
    );
};

export default AIPrediction;
