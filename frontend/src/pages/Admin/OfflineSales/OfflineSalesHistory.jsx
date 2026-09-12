import { useEffect, useEffectEvent, useState } from "react";
import { Link } from "react-router-dom";
import { toast } from "react-toastify";

import DashboardLayout from "../../../layouts/DashboardLayout";
import { getApiErrorMessage } from "../../../services/api";
import {
    getDailyOfflineReport,
    getMonthlyOfflineReport,
    getOfflineSale,
    getOfflineSales,
    getWeeklyOfflineReport,
} from "../../../services/offlineSalesService";
import OfflineReceipt from "./OfflineReceipt";

const getRows = (response) => {
    const data = response?.data;
    return Array.isArray(data) ? data : data?.results || [];
};

const EMPTY_REPORT = {
    report: "Offline Sales Reports",
    period: {},
    summary: {
        total_offline_orders: 0,
        total_items_sold: 0,
        total_revenue: "0.00",
    },
    daily_breakdown: [],
    transactions: [],
    totals: {
        quantity: 0,
        revenue: "0.00",
    },
};

const OfflineSalesHistory = () => {
    const [sales, setSales] = useState([]);
    const [report, setReport] = useState(EMPTY_REPORT);
    const [search, setSearch] = useState("");
    const [startDate, setStartDate] = useState("");
    const [endDate, setEndDate] = useState("");
    const [period, setPeriod] = useState("month");
    const [reportDate, setReportDate] = useState(new Date().toISOString().slice(0, 10));
    const [reportYear, setReportYear] = useState(new Date().getFullYear());
    const [reportMonth, setReportMonth] = useState(new Date().getMonth() + 1);
    const [selectedSale, setSelectedSale] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const loadData = async () => {
        setLoading(true);
        setError("");
        try {
            const reportRequest = period === "today"
                ? getDailyOfflineReport(reportDate)
                : period === "week"
                    ? getWeeklyOfflineReport(reportDate)
                    : getMonthlyOfflineReport(reportYear, reportMonth);
            const [salesResponse, reportResponse] = await Promise.all([
                getOfflineSales({
                    search: search.trim() || undefined,
                    start_date: startDate || undefined,
                    end_date: endDate || undefined,
                }),
                reportRequest,
            ]);
            setSales(getRows(salesResponse));
            setReport({
                ...EMPTY_REPORT,
                ...reportResponse?.data,
                period: {
                    ...EMPTY_REPORT.period,
                    ...reportResponse?.data?.period,
                },
                summary: {
                    ...EMPTY_REPORT.summary,
                    ...reportResponse?.data?.summary,
                },
                totals: {
                    ...EMPTY_REPORT.totals,
                    ...reportResponse?.data?.totals,
                },
            });
        } catch (error) {
            setError(getApiErrorMessage(error, "Unable to load offline sales."));
            toast.error(getApiErrorMessage(error, "Unable to load offline sales."));
        } finally {
            setLoading(false);
        }
    };

    const loadDataEvent = useEffectEvent(loadData);

    useEffect(() => {
        const timer = window.setTimeout(() => {
            void loadDataEvent();
        }, 0);
        return () => window.clearTimeout(timer);
    }, [period]);

    const viewSale = async (saleId) => {
        try {
            const response = await getOfflineSale(saleId);
            setSelectedSale(response.data);
        } catch (error) {
            toast.error(getApiErrorMessage(error, "Unable to load receipt."));
        }
    };

    const downloadReport = async () => {
        const response = period === "today"
            ? await getDailyOfflineReport(reportDate, true)
            : period === "week"
                ? await getWeeklyOfflineReport(reportDate, true)
                : await getMonthlyOfflineReport(reportYear, reportMonth, true);
        const url = URL.createObjectURL(response.data);
        const link = document.createElement("a");
        link.href = url;
        link.download = period === "today"
            ? `offline_sales_daily_${reportDate}.csv`
            : period === "week"
                ? `offline_sales_weekly_${reportDate}.csv`
                : `offline_sales_monthly_${reportYear}-${String(reportMonth).padStart(2, "0")}.csv`;
        link.click();
        URL.revokeObjectURL(url);
    };

    if (selectedSale) {
        return (
            <DashboardLayout>
                <OfflineReceipt order={selectedSale} onCreateAnother={() => setSelectedSale(null)} />
            </DashboardLayout>
        );
    }

    return (
        <DashboardLayout>
            <div className="container-fluid py-4 offline-report-page">
                <div className="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-4">
                    <div><h2 className="mb-1">{report.report}</h2><p className="text-muted mb-0">Persisted counter sales only.</p><p className="offline-report-generated mb-0">Period: {report.period.start_date || "-"} to {report.period.end_date || "-"} · Generated: {new Date().toLocaleString()}</p></div>
                    <div className="offline-report-actions d-flex gap-2"><button type="button" className="btn btn-outline-primary" onClick={() => window.print()} disabled={loading || Boolean(error)}>Print Report</button><button type="button" className="btn btn-outline-secondary" onClick={() => void downloadReport()} disabled={loading || Boolean(error)}>Download</button><Link className="btn btn-primary" to="/admin/offline-sales">Create Offline Sale</Link></div>
                </div>
                <div className="row g-3 mb-4">
                    <div className="col-md-5"><label className="form-label">Search customer, phone, or order ID</label><input className="form-control" value={search} onChange={(event) => setSearch(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter") void loadData(); }} /></div>
                    <div className="col-md-2"><label className="form-label">Start date</label><input className="form-control" type="date" value={startDate} onChange={(event) => setStartDate(event.target.value)} /></div>
                    <div className="col-md-2"><label className="form-label">End date</label><input className="form-control" type="date" value={endDate} onChange={(event) => setEndDate(event.target.value)} /></div>
                    <div className="col-md-2"><label className="form-label">Report type</label><select className="form-select" value={period} onChange={(event) => setPeriod(event.target.value)}><option value="today">Daily</option><option value="week">Weekly</option><option value="month">Monthly</option></select></div>
                    <div className="col-md-2"><label className="form-label">Report date</label><input className="form-control" type="date" value={reportDate} onChange={(event) => setReportDate(event.target.value)} /></div>
                    {period === "month" && <><div className="col-md-1"><label className="form-label">Year</label><input className="form-control" type="number" value={reportYear} onChange={(event) => setReportYear(event.target.value)} /></div><div className="col-md-1"><label className="form-label">Month</label><input className="form-control" type="number" min="1" max="12" value={reportMonth} onChange={(event) => setReportMonth(event.target.value)} /></div></>}
                    <div className="col-md-2 d-flex align-items-end gap-2"><button type="button" className="btn btn-outline-primary" onClick={() => void loadData()}>Search</button><button type="button" className="btn btn-outline-secondary" onClick={() => void downloadReport()}>CSV</button></div>
                </div>
                {error && <div className="alert alert-danger">{error}</div>}
                <div className="row g-3 mb-4"><div className="col-sm-6 col-xl-3"><div className="border rounded p-3 bg-white"><div className="text-muted small">Offline Revenue</div><strong>৳{report.summary.total_revenue || "0.00"}</strong></div></div><div className="col-sm-6 col-xl-3"><div className="border rounded p-3 bg-white"><div className="text-muted small">Completed Sales</div><strong>{report.summary.total_offline_orders || 0}</strong></div></div><div className="col-sm-6 col-xl-3"><div className="border rounded p-3 bg-white"><div className="text-muted small">Units Sold</div><strong>{report.summary.total_items_sold || 0}</strong></div></div><div className="col-sm-6 col-xl-3"><div className="border rounded p-3 bg-white"><div className="text-muted small">Average Sale</div><strong>৳{report.summary.total_offline_orders ? (Number(report.summary.total_revenue || 0) / report.summary.total_offline_orders).toFixed(2) : "0.00"}</strong></div></div></div>
                <div className="row g-3 mb-4"><div className="col-lg-6"><div className="card border-0 shadow-sm h-100"><div className="card-header bg-white fw-bold">Top Offline Products</div><div className="table-responsive"><table className="table table-sm mb-0"><thead><tr><th>Product</th><th>Units</th><th className="text-end">Revenue</th></tr></thead><tbody>{(report.top_products || []).map((product) => <tr key={product.product_id}><td>{product.product_name}</td><td>{product.units_sold}</td><td className="text-end">৳{product.revenue}</td></tr>)}</tbody></table></div></div></div><div className="col-lg-6"><div className="card border-0 shadow-sm h-100"><div className="card-header bg-white fw-bold">Payment Methods</div><div className="table-responsive"><table className="table table-sm mb-0"><thead><tr><th>Method</th><th>Sales</th><th className="text-end">Amount</th></tr></thead><tbody>{(report.payment_methods || []).map((method) => <tr key={method.payment_method}><td>{method.payment_method}</td><td>{method.count}</td><td className="text-end">৳{method.amount}</td></tr>)}</tbody></table></div></div></div></div>
                <div className="card border-0 shadow-sm mb-4"><div className="card-header bg-white fw-bold">Daily Breakdown</div><div className="table-responsive"><table className="table table-sm mb-0"><thead><tr><th>Date</th><th>Offline Orders</th><th>Items Sold</th><th className="text-end">Daily Sales</th></tr></thead><tbody>{(report.daily_breakdown || []).map((day) => <tr key={day.date}><td>{day.date}</td><td>{day.offline_orders}</td><td>{day.items_sold}</td><td className="text-end">৳{day.daily_sales}</td></tr>)}</tbody></table></div></div>
                <div className="card border-0 shadow-sm mb-4"><div className="card-header bg-white fw-bold">Detailed Transactions</div><div className="table-responsive"><table className="table table-sm align-middle mb-0"><thead><tr><th>Order</th><th>Customer</th><th>Phone</th><th>Product</th><th>Qty</th><th>Unit Price</th><th>Line Total</th><th>Order Total</th><th>Date/Time</th><th>Created By</th></tr></thead><tbody>{(report.transactions || []).map((transaction, index) => <tr key={`${transaction.order_id}-${transaction.product_name}-${index}`}><td>#{transaction.order_id}</td><td>{transaction.customer_name}</td><td>{transaction.phone}</td><td>{transaction.product_name}</td><td>{transaction.quantity}</td><td>৳{transaction.unit_price}</td><td>৳{transaction.line_total}</td><td>৳{transaction.order_total}</td><td>{new Date(transaction.order_datetime).toLocaleString()}</td><td>{transaction.created_by}</td></tr>)}</tbody></table></div><div className="card-footer bg-white d-flex justify-content-end gap-4"><strong>Total quantity: {report.totals.quantity || 0}</strong><strong>Total revenue: ৳{report.totals.revenue || "0.00"}</strong></div></div>
                <div className="card border-0 shadow-sm offline-history-table"><div className="table-responsive">{loading ? <div className="p-4 text-muted">Loading offline sales...</div> : <table className="table align-middle mb-0"><thead><tr><th>Order ID</th><th>Customer</th><th>Phone</th><th>Date</th><th>Products</th><th>Total</th><th>Payment</th><th>Created By</th><th>Actions</th></tr></thead><tbody>{sales.length === 0 ? <tr><td colSpan="9" className="text-center text-muted py-4">No offline sales found.</td></tr> : sales.map((sale) => <tr key={sale.id}><td>#{sale.id}</td><td>{sale.customer_name}</td><td>{sale.offline_customer_phone}</td><td>{new Date(sale.created_at).toLocaleString()}</td><td>{sale.item_count}</td><td>৳{sale.total_amount}</td><td>{sale.payment_status || "Paid"}</td><td>{sale.created_by_name || "Admin"}</td><td><div className="d-flex gap-1"><button type="button" className="btn btn-sm btn-outline-primary" onClick={() => void viewSale(sale.id)}>View</button><button type="button" className="btn btn-sm btn-outline-secondary" onClick={() => void viewSale(sale.id)}>Print</button><button type="button" className="btn btn-sm btn-outline-secondary" onClick={() => void viewSale(sale.id)}>Download</button></div></td></tr>)}</tbody></table>}</div></div>
            </div>
        </DashboardLayout>
    );
};

export default OfflineSalesHistory;
