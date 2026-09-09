import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
    BarElement,
    CategoryScale,
    Chart as ChartJS,
    Legend,
    LinearScale,
    LineElement,
    PointElement,
    Tooltip,
} from "chart.js";
import { Bar, Line } from "react-chartjs-2";

import DashboardLayout from "../../../layouts/DashboardLayout";
import api from "../../../services/api";
import {
    getAIPredictionSummary,
    getAIReorderRecommendations,
} from "../../../services/aiPredictionService";

ChartJS.register(
    BarElement,
    CategoryScale,
    Legend,
    LinearScale,
    LineElement,
    PointElement,
    Tooltip,
);

const INITIAL_STATS = {
    customers: 0,
    suppliers: 0,
    delivery_riders: 0,
    products: 0,
    orders: 0,
    sales: "0.00",
    pending_orders: 0,
    processing_orders: 0,
    delivered_orders: 0,
    low_stock_products: 0,
};

const Dashboard = () => {
    const [stats, setStats] = useState(INITIAL_STATS);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [aiData, setAIData] = useState(null);
    const [aiRecommendations, setAIRecommendations] = useState([]);
    const [aiLoading, setAILoading] = useState(true);
    const [aiError, setAIError] = useState("");
    const [aiNoHistory, setAINoHistory] = useState(false);

    useEffect(() => {
        let ignore = false;

        const loadDashboard = async () => {
            try {
                const response = await api.get(
                    "auth/admin-dashboard/"
                );

                if (ignore) {
                    return;
                }

                const dashboardStats = response.data?.stats;

                setStats((previousStats) => ({
                    ...previousStats,
                    ...(dashboardStats || {}),
                }));
            } catch (err) {
                console.error(
                    "Admin dashboard error:",
                    err
                );

                if (!ignore) {
                    setError(
                        err.response?.data?.detail ||
                        err.response?.data?.message ||
                        "Failed to load dashboard data."
                    );
                }
            } finally {
                if (!ignore) {
                    setLoading(false);
                }
            }
        };

        loadDashboard();

        return () => {
            ignore = true;
        };
    }, []);

    useEffect(() => {
        let ignore = false;

        Promise.all([
            getAIPredictionSummary(),
            getAIReorderRecommendations(),
        ])
            .then(([forecastResponse, recommendationResponse]) => {
                if (ignore) return;
                setAIData(forecastResponse.data);
                setAIRecommendations(
                    recommendationResponse.data?.recommendations || [],
                );
            })
            .catch((requestError) => {
                if (ignore) return;
                if (requestError.response?.status === 503) {
                    setAINoHistory(true);
                    return;
                }
                setAIError(
                    requestError.response?.data?.detail ||
                    "Failed to load AI dashboard data.",
                );
            })
            .finally(() => {
                if (!ignore) setAILoading(false);
            });

        return () => {
            ignore = true;
        };
    }, []);

    const cards = [
        {
            label: "Customers",
            value: stats.customers,
        },
        {
            label: "Suppliers",
            value: stats.suppliers,
        },
        {
            label: "Delivery Men",
            value: stats.delivery_riders,
        },
        {
            label: "Products",
            value: stats.products,
        },
        {
            label: "Orders",
            value: stats.orders,
        },
        {
            label: "Sales",
            value: `৳${stats.sales}`,
        },
    ];

    const forecast = aiData?.forecast;
    const dailyForecast = forecast?.daily || [];
    const productPredictions = forecast?.products || [];
    const highRiskProducts = aiRecommendations.filter(
        (item) => item.risk_level === "HIGH RISK",
    );
    const dailyChartData = {
        labels: dailyForecast.slice(0, 14).map((item) => item.date.slice(5)),
        datasets: [
            {
                label: "Predicted units",
                data: dailyForecast.slice(0, 14).map((item) => item.predicted_units),
                borderColor: "#176b87",
                backgroundColor: "rgba(23, 107, 135, 0.15)",
                fill: true,
                tension: 0.3,
            },
        ],
    };
    const topProducts = productPredictions.slice(0, 6);
    const productChartData = {
        labels: topProducts.map((item) => item.product_name),
        datasets: [
            {
                label: "Next 30 days",
                data: topProducts.map((item) => item.next_30_days_units),
                backgroundColor: "#e58f65",
            },
        ],
    };
    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false },
        },
        scales: {
            y: { beginAtZero: true },
        },
    };

    return (
        <DashboardLayout>
            <div className="container-fluid py-4">

                <h2>Admin Dashboard</h2>

                <hr />

                {error && (
                    <div className="alert alert-danger">
                        {error}
                    </div>
                )}

                {loading ? (
                    <div className="text-center py-5">

                        <div
                            className="spinner-border text-primary"
                            role="status"
                        >
                            <span className="visually-hidden">
                                Loading...
                            </span>
                        </div>

                        <p className="mt-3 text-muted">
                            Loading dashboard...
                        </p>

                    </div>
                ) : (
                    <>
                        {/* ==================================================
                            MAIN STATISTICS
                        ================================================== */}

                        <div className="row g-3 mb-4">

                            {cards.map((card) => (
                                <div
                                    className="col-md-4 col-lg-2"
                                    key={card.label}
                                >
                                    <div className="card h-100 shadow-sm border-0">

                                        <div className="card-body">

                                            <div className="text-muted small">
                                                {card.label}
                                            </div>

                                            <h4 className="mt-2 mb-0">
                                                {card.value}
                                            </h4>

                                        </div>

                                    </div>
                                </div>
                            ))}

                        </div>

                        <div className="card border-0 shadow-sm mb-4">
                            <div className="card-body d-flex flex-wrap justify-content-between align-items-center gap-3">
                                <div>
                                    <h5 className="mb-1">Offline Sales Reports</h5>
                                    <p className="text-muted mb-0">
                                        Generate daily, weekly, and monthly counter-sale reports from persisted offline orders.
                                    </p>
                                </div>
                                <Link className="btn btn-outline-primary" to="/admin/offline-sales/history">
                                    Open Reports
                                </Link>
                            </div>
                        </div>


                        {/* ==================================================
                            ORDER / INVENTORY STATISTICS
                        ================================================== */}

                        <div className="row g-3">

                            {/* Pending */}

                            <div className="col-md-3">

                                <div className="card shadow-sm border-0">

                                    <div className="card-body">

                                        <div className="text-muted small">
                                            Pending Orders
                                        </div>

                                        <h4>
                                            {stats.pending_orders}
                                        </h4>

                                    </div>

                                </div>

                            </div>


                            {/* Processing */}

                            <div className="col-md-3">

                                <div className="card shadow-sm border-0">

                                    <div className="card-body">

                                        <div className="text-muted small">
                                            Processing Orders
                                        </div>

                                        <h4>
                                            {stats.processing_orders}
                                        </h4>

                                    </div>

                                </div>

                            </div>


                            {/* Delivered */}

                            <div className="col-md-3">

                                <div className="card shadow-sm border-0">

                                    <div className="card-body">

                                        <div className="text-muted small">
                                            Delivered Orders
                                        </div>

                                        <h4>
                                            {stats.delivered_orders}
                                        </h4>

                                    </div>

                                </div>

                            </div>


                            {/* Low Stock */}

                            <div className="col-md-3">

                                <div className="card shadow-sm border-0">

                                    <div className="card-body">

                                        <div className="text-muted small">
                                            Low Stock Products
                                        </div>

                                        <h4>
                                            {stats.low_stock_products}
                                        </h4>

                                    </div>

                                </div>

                            </div>

                        </div>

                        <section className="mt-5" aria-labelledby="ai-dashboard-heading">
                            <div className="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-3">
                                <div>
                                    <h3 id="ai-dashboard-heading" className="mb-1">AI Demand Intelligence</h3>
                                    <p className="text-muted mb-0">Forecasts and reorder guidance from realized delivered sales.</p>
                                </div>
                                {aiData && <span className="badge text-bg-light">Model {aiData.pipeline?.model_version || "fallback"}</span>}
                            </div>

                            {aiLoading && (
                                <div className="border rounded p-4 text-center">Loading AI forecast...</div>
                            )}
                            {aiNoHistory && (
                                <div className="alert alert-secondary">No historical sales forecast is available yet. Train the AI model after more delivered-sales history is collected.</div>
                            )}
                            {aiError && <div className="alert alert-danger">{aiError}</div>}

                            {!aiLoading && !aiNoHistory && !aiError && aiData && (
                                <>
                                    <div className="row g-3 mb-4">
                                        <div className="col-sm-6 col-xl-3"><div className="card h-100 border-0 shadow-sm"><div className="card-body"><div className="text-muted small">Total predicted demand</div><h4 className="mb-0">{aiData.summary?.forecast_monthly_units ?? 0} units</h4><small className="text-muted">Next 30 days</small></div></div></div>
                                        <div className="col-sm-6 col-xl-3"><div className="card h-100 border-0 shadow-sm"><div className="card-body"><div className="text-muted small">Daily forecast</div><h4 className="mb-0">{dailyForecast[0]?.predicted_units ?? 0} units</h4><small className="text-muted">Tomorrow</small></div></div></div>
                                        <div className="col-sm-6 col-xl-3"><div className="card h-100 border-0 shadow-sm"><div className="card-body"><div className="text-muted small">Weekly forecast</div><h4 className="mb-0">{aiData.summary?.forecast_weekly_units ?? 0} units</h4><small className="text-muted">Next 7 days</small></div></div></div>
                                        <div className="col-sm-6 col-xl-3"><div className="card h-100 border-0 shadow-sm"><div className="card-body"><div className="text-muted small">High stockout risk</div><h4 className="mb-0">{highRiskProducts.length}</h4><small className="text-muted">Products needing review</small></div></div></div>
                                    </div>

                                    <div className="row g-3 mb-4">
                                        <div className="col-xl-7">
                                            <div className="card border-0 shadow-sm h-100">
                                                <div className="card-header bg-white fw-bold">Daily forecast</div>
                                                <div className="card-body" style={{ height: "280px" }}>
                                                    {dailyForecast.length ? <Line data={dailyChartData} options={chartOptions} /> : <div className="text-muted">No daily forecast data.</div>}
                                                </div>
                                            </div>
                                        </div>
                                        <div className="col-xl-5">
                                            <div className="card border-0 shadow-sm h-100">
                                                <div className="card-header bg-white fw-bold">Top predicted products</div>
                                                <div className="card-body" style={{ height: "280px" }}>
                                                    {topProducts.length ? <Bar data={productChartData} options={chartOptions} /> : <div className="text-muted">No product forecast data.</div>}
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="card border-0 shadow-sm mb-4">
                                        <div className="card-header bg-white fw-bold">Product demand and stock outlook</div>
                                        <div className="table-responsive">
                                            <table className="table table-sm table-hover mb-0">
                                                <thead><tr><th>Product</th><th>Historical sales</th><th>Current stock</th><th>Predicted demand</th><th>Projected stock</th><th>Risk</th><th>Explanation</th></tr></thead>
                                                <tbody>
                                                    {productPredictions.length ? productPredictions.map((item) => {
                                                        const recommendation = aiRecommendations.find((entry) => entry.product_id === item.product_id);
                                                        return <tr key={item.product_id}><td>{item.product_name}</td><td>{item.historical_sales ?? 0}</td><td>{item.current_stock}</td><td>{item.next_30_days_units}</td><td>{recommendation?.projected_stock ?? item.current_stock - item.next_30_days_units}</td><td>{recommendation?.risk_level || "LOW RISK"}</td><td>{item.explanation || recommendation?.explanation || "Historical realized sales used."}</td></tr>;
                                                    }) : <tr><td colSpan="7" className="text-center text-muted py-3">No product forecast data.</td></tr>}
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>

                                    <div className="row g-3">
                                        <div className="col-lg-6">
                                            <div className="card border-0 shadow-sm h-100">
                                                <div className="card-header bg-white fw-bold">High stockout risk</div>
                                                <div className="list-group list-group-flush">
                                                    {highRiskProducts.length ? highRiskProducts.map((item) => <div className="list-group-item d-flex justify-content-between gap-3" key={item.product_id}><span>{item.product_name}<small className="d-block text-muted">{item.reason}</small></span><strong>{item.recommended_reorder_quantity} units</strong></div>) : <div className="list-group-item text-muted">No products currently have high stockout risk.</div>}
                                                </div>
                                            </div>
                                        </div>
                                        <div className="col-lg-6">
                                            <div className="card border-0 shadow-sm h-100">
                                                <div className="card-header bg-white fw-bold">AI recommendation explanation</div>
                                                <div className="card-body"><p className="mb-2">Recommendations compare predicted demand with current stock and the existing inventory minimum-stock threshold.</p><p className="text-muted small mb-0">{aiData.pipeline?.cleaning || "Missing product-days are treated as zero realized sales."} {aiData.pipeline?.feature_engineering || "Date and lag features are used where history supports them."}</p></div>
                                            </div>
                                        </div>
                                    </div>
                                </>
                            )}
                        </section>
                    </>
                )}

            </div>
        </DashboardLayout>
    );
};

export default Dashboard;