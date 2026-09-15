import { useEffect, useEffectEvent, useState } from "react";
import {
    CategoryScale,
    Chart as ChartJS,
    Filler,
    Legend,
    LinearScale,
    LineElement,
    PointElement,
    Tooltip,
} from "chart.js";
import { Line } from "react-chartjs-2";

import DashboardLayout from "../../../layouts/DashboardLayout";
import api from "../../../services/api";
import {
    getAIPredictionSummary,
    getAIReorderRecommendations,
    getSalesAnalysis,
} from "../../../services/aiPredictionService";
import { createReplenishmentRequest } from "../../../services/replenishmentService";

ChartJS.register(CategoryScale, Filler, Legend, LinearScale, LineElement, PointElement, Tooltip);

const money = (value) => `৳${Number(value || 0).toLocaleString("en-BD", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

const AIPrediction = () => {
    const [sales, setSales] = useState(null);
    const [salesLoading, setSalesLoading] = useState(true);
    const [salesError, setSalesError] = useState("");
    const [period, setPeriod] = useState("month");
    const [startDate, setStartDate] = useState(new Date().toISOString().slice(0, 10));
    const [endDate, setEndDate] = useState(new Date().toISOString().slice(0, 10));
    const [trendDays, setTrendDays] = useState(30);
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [training, setTraining] = useState(false);
    const [recommendations, setRecommendations] = useState([]);
    const [recommendationLoading, setRecommendationLoading] = useState(true);
    const [recommendationError, setRecommendationError] = useState("");
    const [drafts, setDrafts] = useState({});
    const [creatingProductId, setCreatingProductId] = useState(null);

    const loadSales = async () => {
        setSalesLoading(true);
        setSalesError("");
        try {
            const params = { period };
            if (period === "custom") {
                params.start_date = startDate;
                params.end_date = endDate;
            }
            const response = await getSalesAnalysis(params);
            setSales(response.data || null);
        } catch (requestError) {
            setSales(null);
            setSalesError(requestError.response?.data?.detail || "Unable to load sales data.");
        } finally {
            setSalesLoading(false);
        }
    };
    const loadSalesEvent = useEffectEvent(loadSales);

    useEffect(() => {
        const timer = window.setTimeout(() => {
            void loadSalesEvent();
        }, 0);
        return () => window.clearTimeout(timer);
    }, [period, startDate, endDate]);

    useEffect(() => {
        let ignore = false;

        Promise.allSettled([getAIPredictionSummary(), getAIReorderRecommendations()])
            .then(([forecastResult, recommendationResult]) => {
                if (ignore) return;
                if (forecastResult.status === "fulfilled") {
                    setData(forecastResult.value.data || null);
                    setError("");
                } else {
                    setError(forecastResult.reason?.response?.data?.detail || "AI prediction is temporarily unavailable.");
                }
                if (recommendationResult.status === "fulfilled") {
                    setRecommendations(recommendationResult.value.data?.recommendations || []);
                } else {
                    setRecommendationError(recommendationResult.reason?.response?.status === 503
                        ? "Train the forecast model before reviewing reorder recommendations."
                        : recommendationResult.reason?.response?.data?.detail || "Unable to load stock risk recommendations.");
                }
            })
            .finally(() => {
                if (!ignore) {
                    setLoading(false);
                    setRecommendationLoading(false);
                }
            });

        return () => {
            ignore = true;
        };
    }, []);

    const trainModel = async () => {
        setTraining(true);
        setError("");
        try {
            await api.post("ai-prediction/admin/train/");
            const [forecastResponse, recommendationResponse] = await Promise.all([
                getAIPredictionSummary(),
                getAIReorderRecommendations(),
            ]);
            setData(forecastResponse.data || null);
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

    const overview = sales?.overview || {};
    const details = sales?.details || [];
    const products = sales?.products || [];
    const trend = (sales?.trend || []).slice(-trendDays);
    const forecastDays = data?.forecast?.daily || [];
    const explanation = overview.sales_growth_percent === null || overview.sales_growth_percent === undefined
        ? "There is not enough previous-period history to compare sales yet."
        : Number(overview.sales_growth_percent) >= 0
            ? "Sales have increased compared with the previous period, and recent sales activity suggests higher demand."
            : "Sales have declined compared with the previous period, so expected demand is being estimated conservatively.";

    return (
        <DashboardLayout>
            <div className="container-fluid py-4">
                <div className="d-flex flex-wrap justify-content-between align-items-start gap-3 mb-4">
                    <div>
                        <h2>Sales Analysis & AI Prediction</h2>
                        <p className="text-muted">Understand completed sales first, then review expected demand and stock risk.</p>
                    </div>
                    <button className="btn btn-primary" onClick={trainModel} disabled={loading || training}>
                        {training ? "Training..." : "Train Model"}
                    </button>
                </div>
                <section className="mb-5"><div className="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-3"><h4 className="mb-0">1. Sales Overview</h4><div className="d-flex gap-2"><select className="form-select" value={period} onChange={(event) => setPeriod(event.target.value)}><option value="today">Today</option><option value="week">Last 7 Days</option><option value="month">This Month</option><option value="year">This Year</option><option value="custom">Custom Date Range</option></select>{period === "custom" && <><input className="form-control" type="date" value={startDate} onChange={(event) => setStartDate(event.target.value)} /><input className="form-control" type="date" value={endDate} onChange={(event) => setEndDate(event.target.value)} /></>}</div></div>{salesLoading && <div className="py-3">Loading sales data...</div>}{salesError && <div className="alert alert-danger">{salesError}</div>}{!salesLoading && !salesError && sales && <div className="row g-3">{[["Total Sales", money(overview.total_sales)], ["Total Orders", overview.total_orders || 0], ["Products Sold", overview.total_products_sold || 0], ["Average Order Value", money(overview.average_order_value)], ["Best-Selling Product", overview.best_selling_product || "No sales yet"], ["Sales Growth / Decline", overview.sales_growth_percent === null ? "N/A" : `${overview.sales_growth_percent}%`], ["Refund Amount", money(overview.refund_amount)], ["Net Sales", money(overview.net_sales)]].map(([label, value]) => <div className="col-sm-6 col-xl-3" key={label}><div className="card border-0 shadow-sm h-100 p-3"><div className="text-muted small">{label}</div><strong className="fs-4">{value}</strong></div></div>)}</div>}</section>
                <section className="mb-5"><h4>2. Sales Details</h4>{!salesLoading && !salesError && details.length === 0 ? <div className="alert alert-light">No sales data available for this period.</div> : <div className="table-responsive"><table className="table table-striped align-middle"><thead><tr><th>Date</th><th>Product</th><th>Quantity Sold</th><th>Sales Amount</th><th>Orders</th><th>Refund</th><th>Net Sales</th><th>Channel</th></tr></thead><tbody>{details.map((row, index) => <tr key={`${row.date}-${row.product}-${row.channel}-${index}`}><td>{row.date}</td><td>{row.product}</td><td>{row.quantity_sold}</td><td>{money(row.sales_amount)}</td><td>{row.orders}</td><td>{money(row.refund)}</td><td>{money(row.net_sales)}</td><td>{row.channel}</td></tr>)}</tbody></table></div>}</section>
                <section className="mb-5"><div className="d-flex justify-content-between align-items-center mb-3"><h4 className="mb-0">3. Sales Trend</h4><select className="form-select w-auto" value={trendDays} onChange={(event) => setTrendDays(Number(event.target.value))}><option value="7">7 days</option><option value="30">30 days</option><option value="90">90 days</option></select></div>{trend.length === 0 ? <div className="alert alert-light">No sales data available.</div> : <Line data={{ labels: trend.map((item) => item.date), datasets: [{ label: "Daily Sales", data: trend.map((item) => Number(item.sales_amount)), borderColor: "#176b87", backgroundColor: "rgba(23, 107, 135, 0.14)", fill: true, tension: 0.3 }] }} options={{ responsive: true, scales: { y: { title: { display: true, text: "Sales Amount (৳)" }, beginAtZero: true }, x: { title: { display: true, text: "Date" } } } }} />}</section>
                <section className="mb-5"><h4>4. Product Performance</h4>{products.length === 0 ? <div className="alert alert-light">No product sales available.</div> : <div className="table-responsive"><table className="table table-bordered"><thead><tr><th>Product</th><th>Units Sold</th><th>Revenue</th><th>Sales Share</th><th>Trend</th></tr></thead><tbody>{products.map((product) => <tr key={product.product_id}><td>{product.product_name}</td><td>{product.units_sold}</td><td>{money(product.revenue)}</td><td>{product.sales_share}%</td><td>{product.trend}</td></tr>)}</tbody></table></div>}</section>
                <section className="mb-5"><h4>5. AI Sales Forecast</h4>{loading && <div className="py-3">Loading AI forecast...</div>}{!loading && error && <div className="alert alert-warning">AI prediction is temporarily unavailable.</div>}{!loading && !error && !data && <div className="alert alert-light">Train the forecast model to see expected sales.</div>}{data && <><div className="row g-3 mb-3">{[["Historical Days", data.summary?.historical_days || 0], ["Next 7 Days", `${data.summary?.forecast_weekly_units || 0} units`], ["Next 30 Days", `${data.summary?.forecast_monthly_units || 0} units`], ["Sales Trend", Number(overview.sales_growth_percent || 0) >= 0 ? "Increasing" : "Declining"]].map(([label, value]) => <div className="col-sm-6 col-xl-3" key={label}><div className="card border-0 shadow-sm h-100 p-3"><div className="text-muted small">{label}</div><strong className="fs-4">{value}</strong></div></div>)}</div><div className="alert alert-info"><strong>Why is this prediction showing?</strong><div>{explanation}</div></div><div className="table-responsive"><table className="table table-sm"><thead><tr><th>Date</th><th>Expected Units</th></tr></thead><tbody>{forecastDays.slice(0, 7).map((item) => <tr key={item.date}><td>{item.date}</td><td>{item.predicted_units}</td></tr>)}</tbody></table></div></>}</section>
                <section><h4>6. Inventory Risk & Reorder Recommendation</h4>{recommendationError && <div className="alert alert-warning">{recommendationError}</div>}{recommendationLoading ? <div className="py-3">Loading stock risk recommendations...</div> : recommendations.length === 0 ? <div className="alert alert-light">No stock risks or reorder recommendations are currently available.</div> : <div className="table-responsive"><table className="table table-bordered align-middle"><thead><tr><th>Product</th><th>Current Stock</th><th>Expected Demand</th><th>Projected Stock</th><th>Risk Level</th><th>Recommended Reorder</th><th>Action</th></tr></thead><tbody>{recommendations.map((recommendation) => { const draft = getDraft(recommendation); const unavailable = !recommendation.supplier_available; return <tr key={recommendation.product_id}><td>{recommendation.product_name}</td><td>{recommendation.current_stock}</td><td>{recommendation.predicted_demand}</td><td>{recommendation.projected_stock}</td><td>{recommendation.risk_level}</td><td>{recommendation.recommended_reorder_quantity}</td><td><div className="d-flex gap-2"><select className="form-select" value={draft.supplier} onChange={(event) => updateDraft(recommendation, "supplier", event.target.value)} disabled={unavailable || creatingProductId === recommendation.product_id}><option value="">{unavailable ? "No active supplier" : "Select supplier"}</option>{!unavailable && <option value={String(recommendation.supplier_id)}>{recommendation.supplier_name || "Recommended supplier"}</option>}</select><input className="form-control" type="number" min="1" value={draft.quantity} onChange={(event) => updateDraft(recommendation, "quantity", event.target.value)} /><button type="button" className="btn btn-primary" disabled={unavailable || creatingProductId === recommendation.product_id} onClick={() => createRequestFromRecommendation(recommendation)}>Request</button></div></td></tr>; })}</tbody></table></div>}</section>
            </div>
        </DashboardLayout>
    );
};

export default AIPrediction;
