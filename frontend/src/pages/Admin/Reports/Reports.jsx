import { useEffect, useState } from "react";

import DashboardLayout from "../../../layouts/DashboardLayout";
import api from "../../../services/api";

const Metric = ({ label, value }) => (
    <div className="col-sm-6 col-xl-3">
        <div className="border rounded p-3 h-100 bg-white">
            <div className="text-muted small">{label}</div>
            <div className="fs-4 fw-bold">{value}</div>
        </div>
    </div>
);

const StatusTable = ({ title, values }) => (
    <div className="col-lg-4">
        <div className="card border-0 shadow-sm h-100">
            <div className="card-header bg-white fw-bold">{title}</div>
            <table className="table table-sm mb-0">
                <tbody>
                    {Object.entries(values || {}).map(([status, count]) => (
                        <tr key={status}>
                            <td>{status}</td>
                            <td className="text-end fw-semibold">{count}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    </div>
);

const Reports = () => {
    const [report, setReport] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [period, setPeriod] = useState("today");
    const [startDate, setStartDate] = useState("");
    const [endDate, setEndDate] = useState("");

    useEffect(() => {
        let ignore = false;

        if (period === "custom" && (!startDate || !endDate)) {
            setLoading(false);
            return () => {
                ignore = true;
            };
        }

        setLoading(true);
        setError("");

        const params = new URLSearchParams({ period });
        if (period === "custom") {
            params.set("start_date", startDate);
            params.set("end_date", endDate);
        }

        api.get(`reports/admin/summary/?${params.toString()}`)
            .then((response) => {
                if (!ignore) setReport(response.data);
            })
            .catch((requestError) => {
                if (!ignore) {
                    setError(
                        requestError.response?.data?.detail ||
                        "Failed to load reports."
                    );
                }
            })
            .finally(() => {
                if (!ignore) setLoading(false);
            });

        return () => {
            ignore = true;
        };
    }, [period, startDate, endDate]);

    if (loading) {
        return <DashboardLayout><div className="py-5 text-center">Loading reports...</div></DashboardLayout>;
    }

    return (
        <DashboardLayout>
            <div className="container-fluid py-4">
                <h2 className="mb-1">Reports</h2>
                <p className="text-muted mb-4">Operational summary as of {report?.date || "today"}.</p>
                {error && <div className="alert alert-danger">{error}</div>}

                <div className="row g-2 align-items-end mb-4">
                    <div className="col-md-3">
                        <label className="form-label">Sales period</label>
                        <select
                            className="form-select"
                            value={period}
                            onChange={(event) => setPeriod(event.target.value)}
                        >
                            <option value="today">Today</option>
                            <option value="week">This Week</option>
                            <option value="month">This Month</option>
                            <option value="year">This Year</option>
                            <option value="custom">Custom Date Range</option>
                        </select>
                    </div>
                    {period === "custom" && (
                        <>
                            <div className="col-md-3">
                                <label className="form-label">Start date</label>
                                <input
                                    className="form-control"
                                    type="date"
                                    value={startDate}
                                    onChange={(event) => setStartDate(event.target.value)}
                                />
                            </div>
                            <div className="col-md-3">
                                <label className="form-label">End date</label>
                                <input
                                    className="form-control"
                                    type="date"
                                    value={endDate}
                                    onChange={(event) => setEndDate(event.target.value)}
                                />
                            </div>
                        </>
                    )}
                </div>

                <div className="row g-3 mb-4">
                    <Metric label="Sales" value={`৳${report?.sales?.total_sales || "0.00"}`} />
                    <Metric label="Orders" value={report?.orders?.total || 0} />
                    <Metric label="Products" value={report?.products?.total || 0} />
                    <Metric label="Customers" value={report?.customers?.total || 0} />
                    <Metric label="Suppliers" value={report?.suppliers?.total || 0} />
                    <Metric label="Deliveries" value={report?.deliveries?.total || 0} />
                    <Metric label="Payments" value={report?.payments?.total || 0} />
                    <Metric label="Inventory Units" value={report?.inventory?.total_stock || 0} />
                </div>

                <div className="row g-3 mb-4">
                    <StatusTable title="Order Reports" values={report?.orders?.by_status} />
                    <StatusTable title="Delivery Reports" values={report?.deliveries?.by_status} />
                    <StatusTable title="Payment Reports" values={report?.payments?.by_status} />
                </div>

                <div className="row g-3">
                    <div className="col-lg-4"><div className="card border-0 shadow-sm h-100"><div className="card-header bg-white fw-bold">Sales Reports</div><div className="card-body"><p>Delivered orders: {report?.sales?.delivered_orders || 0}</p><p>Paid amount: ৳{report?.payments?.paid_amount || "0.00"}</p><p className="mb-0">Delivered item revenue: ৳{report?.sales?.delivered_item_revenue || "0.00"}</p></div></div></div>
                    <div className="col-lg-4"><div className="card border-0 shadow-sm h-100"><div className="card-header bg-white fw-bold">Product Reports</div><div className="list-group list-group-flush">{(report?.products?.top_sellers || []).map((product) => <div className="list-group-item d-flex justify-content-between" key={product.product_id}><span>{product.product__name}</span><span>{product.units_sold} sold</span></div>)}</div></div></div>
                    <div className="col-lg-4"><div className="card border-0 shadow-sm h-100"><div className="card-header bg-white fw-bold">Inventory and Supplier Reports</div><div className="card-body"><p>Low stock: {report?.inventory?.low_stock || 0}</p><p>Out of stock: {report?.inventory?.out_of_stock || 0}</p><p>Active suppliers: {report?.suppliers?.active || 0}</p><p className="mb-0">Approved suppliers: {report?.suppliers?.approved || 0}</p></div></div></div>
                </div>
            </div>
        </DashboardLayout>
    );
};

export default Reports;