import { useEffect, useState } from "react";

import DashboardLayout from "../../../layouts/DashboardLayout";
import api from "../../../services/api";
import { getOnlineSalesReport } from "../../../services/reportService";
import "./reports.css";

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
    const [onlineReport, setOnlineReport] = useState(null);
    const [onlineLoading, setOnlineLoading] = useState(true);
    const [onlineError, setOnlineError] = useState("");

    const getOnlinePeriodParams = () => {
        const today = new Date().toISOString().slice(0, 10);
        if (period === "today") return { period: "daily", date: today };
        if (period === "week") return { period: "weekly", date: today };
        if (period === "month") {
            const current = new Date();
            return {
                period: "monthly",
                year: current.getFullYear(),
                month: current.getMonth() + 1,
            };
        }
        if (period === "year") {
            return { period: "yearly", year: new Date().getFullYear() };
        }
        return { period: "custom", start_date: startDate, end_date: endDate };
    };

    useEffect(() => {
        let ignore = false;

        if (period === "custom" && (!startDate || !endDate)) {
            setLoading(false);
            setOnlineLoading(false);
            return () => {
                ignore = true;
            };
        }

        setLoading(true);
        setError("");
        setOnlineLoading(true);
        setOnlineError("");

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

        getOnlineSalesReport(getOnlinePeriodParams())
            .then((response) => {
                if (!ignore) setOnlineReport(response.data);
            })
            .catch((requestError) => {
                if (!ignore) {
                    setOnlineError(
                        requestError.response?.data?.detail ||
                        "Failed to load detailed online sales."
                    );
                    setOnlineReport(null);
                }
            })
            .finally(() => {
                if (!ignore) setOnlineLoading(false);
            });

        return () => {
            ignore = true;
        };
    }, [period, startDate, endDate]);

    const downloadOnlineReport = async () => {
        try {
            const response = await getOnlineSalesReport(
                getOnlinePeriodParams(),
                true,
            );
            const periodData = onlineReport?.period || {};
            const periodName = periodData.name || "custom";
            const start = periodData.start_date || "report";
            const end = periodData.end_date || start;
            const filename = periodName === "daily"
                ? `online_sales_daily_${start}.csv`
                : periodName === "weekly"
                    ? `online_sales_weekly_${start}.csv`
                    : periodName === "monthly"
                        ? `online_sales_monthly_${start.slice(0, 7)}.csv`
                        : periodName === "yearly"
                            ? `online_sales_yearly_${start.slice(0, 4)}.csv`
                            : `online_sales_custom_${start}_to_${end}.csv`;
            const url = URL.createObjectURL(response.data);
            const link = document.createElement("a");
            link.href = url;
            link.download = filename;
            link.click();
            URL.revokeObjectURL(url);
        } catch (requestError) {
            setOnlineError(
                requestError.response?.data?.detail ||
                "Failed to download detailed online sales."
            );
        }
    };

    const viewOnlineReport = () => {
        document.getElementById("online-sales-report-title")?.scrollIntoView({
            behavior: "smooth",
            block: "start",
        });
    };

    if (loading) {
        return <DashboardLayout><div className="py-5 text-center">Loading reports...</div></DashboardLayout>;
    }

    return (
        <DashboardLayout>
            <div className="container-fluid py-4">
                <h2 className="mb-1">Reports</h2>
                <p className="text-muted mb-4">Operational summary as of {report?.date || "today"}.</p>
                {error && <div className="alert alert-danger">{error}</div>}

                <div className="row g-2 align-items-end mb-4 reports-filters">
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

                <section className="online-sales-report-printable" aria-labelledby="online-sales-report-title">
                    <div className="d-flex flex-wrap justify-content-between align-items-start gap-2 mb-3">
                        <div>
                            <h3 id="online-sales-report-title" className="mb-1">Detailed Online Sales Report</h3>
                            <p className="text-muted mb-0">
                                Period: {onlineReport?.period?.start_date || "-"} to {onlineReport?.period?.end_date || "-"}
                            </p>
                            <small className="text-muted">Generated: {new Date().toLocaleString()}</small>
                        </div>
                        <div className="online-sales-report-actions d-flex gap-2">
                            <button type="button" className="btn btn-outline-secondary" onClick={viewOnlineReport} disabled={onlineLoading}>View</button>
                            <button type="button" className="btn btn-outline-primary" onClick={() => window.print()} disabled={onlineLoading || Boolean(onlineError)}>Print</button>
                            <button type="button" className="btn btn-outline-secondary" onClick={() => void downloadOnlineReport()} disabled={onlineLoading || Boolean(onlineError)}>Download</button>
                        </div>
                    </div>
                    {onlineLoading && <div className="alert alert-info">Loading detailed online sales...</div>}
                    {onlineError && <div className="alert alert-danger">{onlineError}</div>}
                    {!onlineLoading && !onlineError && onlineReport && (
                        <>
                            <div className="row g-3 mb-3">
                                <Metric label="Online Orders" value={onlineReport.summary?.total_orders || 0} />
                                <Metric label="Products Sold" value={onlineReport.summary?.total_quantity || 0} />
                                <Metric label="Revenue" value={`৳${onlineReport.summary?.total_revenue || "0.00"}`} />
                            </div>
                            <div className="card border-0 shadow-sm">
                                <div className="table-responsive">
                                    <table className="table table-sm table-striped align-middle mb-0">
                                        <thead>
                                            <tr><th>Order ID</th><th>Customer Name</th><th>Phone</th><th>Email</th><th>Address</th><th>Product</th><th>Quantity</th><th>Date</th><th>Order Status</th><th>Payment Status</th><th className="text-end">Revenue</th></tr>
                                        </thead>
                                        <tbody>
                                            {onlineReport.transactions?.length ? onlineReport.transactions.map((transaction, index) => (
                                                <tr key={`${transaction.order_id}-${transaction.product_name}-${index}`}>
                                                    <td>#{transaction.order_id}</td><td>{transaction.customer_name || "-"}</td><td>{transaction.phone || "-"}</td><td>{transaction.email || "-"}</td><td>{transaction.address || "-"}</td><td>{transaction.product_name || "-"}</td><td>{transaction.quantity || 0}</td><td>{transaction.date ? new Date(transaction.date).toLocaleString() : "-"}</td><td>{transaction.order_status || "-"}</td><td>{transaction.payment_status || "-"}</td><td className="text-end">৳{transaction.revenue || "0.00"}</td>
                                                </tr>
                                            )) : <tr><td colSpan="11" className="text-center text-muted py-4">No online sales found for this period.</td></tr>}
                                        </tbody>
                                    </table>
                                </div>
                                <div className="card-footer bg-white d-flex justify-content-end gap-4"><strong>Total quantity: {onlineReport.totals?.quantity || 0}</strong><strong>Total revenue: ৳{onlineReport.totals?.revenue || "0.00"}</strong></div>
                            </div>
                        </>
                    )}
                </section>
            </div>
        </DashboardLayout>
    );
};

export default Reports;