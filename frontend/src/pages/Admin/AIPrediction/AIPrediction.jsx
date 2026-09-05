import { useEffect, useState } from "react";

import DashboardLayout from "../../../layouts/DashboardLayout";
import api from "../../../services/api";

const AIPrediction = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        api.get("ai-prediction/admin/summary/")
            .then((response) => setData(response.data))
            .catch((requestError) => setError(
                requestError.response?.data?.detail ||
                "Failed to load AI sales prediction."
            ))
            .finally(() => setLoading(false));
    }, []);

    const forecastDays = data?.forecast?.daily || [];
    const maxForecast = Math.max(
        ...forecastDays.map((item) => item.predicted_units),
        1
    );

    return (
        <DashboardLayout>
            <div className="container-fluid py-4">
                <h2>AI Sales Prediction</h2>
                <p className="text-muted">Historical order forecasting and inventory recommendations.</p>
                {loading && <div className="py-4">Training forecast model...</div>}
                {error && <div className="alert alert-danger">{error}</div>}
                {data && (
                    <>
                        <div className="row g-3 mb-4">
                            <div className="col-md-3"><div className="card p-3"><small>Historical days</small><strong>{data.summary.historical_days}</strong></div></div>
                            <div className="col-md-3"><div className="card p-3"><small>Weekly forecast</small><strong>{data.summary.forecast_weekly_units} units</strong></div></div>
                            <div className="col-md-3"><div className="card p-3"><small>Monthly forecast</small><strong>{data.summary.forecast_monthly_units} units</strong></div></div>
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
                        <h4>Actual vs Predicted</h4>
                        <div className="table-responsive mb-4">
                            <table className="table table-sm"><thead><tr><th>Date</th><th>Actual</th><th>Predicted</th></tr></thead><tbody>{(data.actual_vs_predicted || []).slice(-14).map((item) => <tr key={item.date}><td>{item.date}</td><td>{item.actual_units}</td><td>{item.predicted_units}</td></tr>)}</tbody></table>
                        </div>
                        <h4>Product Demand and Inventory Recommendations</h4>
                        <div className="table-responsive">
                            <table className="table table-striped"><thead><tr><th>Product</th><th>Tomorrow</th><th>Next 7 Days</th><th>Next 30 Days</th><th>Current Stock</th><th>Shortage</th><th>Recommendation</th></tr></thead><tbody>{data.predictions.map((item) => <tr key={item.product_id}><td>{item.product_name}</td><td>{item.tomorrow_units}</td><td>{item.next_7_days_units}</td><td>{item.next_30_days_units}</td><td>{item.current_stock}</td><td>{item.expected_shortage}</td><td>{item.recommended_action}</td></tr>)}</tbody></table>
                        </div>
                    </>
                )}
            </div>
        </DashboardLayout>
    );
};

export default AIPrediction;
