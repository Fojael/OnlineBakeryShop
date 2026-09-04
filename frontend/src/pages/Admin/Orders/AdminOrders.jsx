```jsx
import {
    useCallback,
    useEffect,
    useMemo,
    useState,
} from "react";

import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";

import DashboardLayout from "../../../layouts/DashboardLayout";

import {
    acceptAdminOrder,
    assignDeliveryRider,
    getAdminOrders,
    getDeliveryRiders,
} from "../../../services/orderService";


// =========================================================
// ORDER STATUS TABS
// =========================================================

const ORDER_TABS = [
    "All",
    "Pending",
    "Accepted",
    "Processing",
    "Ready",
    "Assigned",
    "Out for Delivery",
    "Delivered",
    "Cancelled",
];


// =========================================================
// GET ORDER NUMBER
// =========================================================
// Example:
// 1    -> ORD-0001
// 15   -> ORD-0015
// 100  -> ORD-0100
// 1250 -> ORD-1250
// =========================================================

const getOrderNumber = (id) => {
    return "ORD-" + String(id || "").padStart(4, "0");
};


// =========================================================
// ADMIN ORDERS
// =========================================================

const AdminOrders = () => {
    const navigate = useNavigate();

    // =====================================================
    // STATE
    // =====================================================

    const [orders, setOrders] = useState([]);
    const [riders, setRiders] = useState([]);

    const [loading, setLoading] = useState(true);

    const [search, setSearch] = useState("");
    const [activeTab, setActiveTab] = useState("All");

    const [acceptingOrderId, setAcceptingOrderId] =
        useState(null);

    const [assigningOrderId, setAssigningOrderId] =
        useState(null);

    const [selectedRiders, setSelectedRiders] =
        useState({});


    // =====================================================
    // GET ERROR MESSAGE
    // =====================================================

    const getErrorMessage = (error, defaultMessage) => {
        if (
            error &&
            error.response &&
            error.response.data
        ) {
            const responseData =
                error.response.data;

            if (responseData.detail) {
                return responseData.detail;
            }

            if (responseData.message) {
                return responseData.message;
            }

            if (typeof responseData === "string") {
                return responseData;
            }
        }

        if (error && error.message) {
            return error.message;
        }

        return defaultMessage;
    };


    // =====================================================
    // NORMALIZE API DATA
    // =====================================================

    const normalizeResponseData = (response) => {
        let data = response;

        // Axios response
        if (
            response &&
            response.data !== undefined
        ) {
            data = response.data;
        }

        // Direct array
        if (Array.isArray(data)) {
            return data;
        }

        // Django REST Framework pagination
        if (
            data &&
            Array.isArray(data.results)
        ) {
            return data.results;
        }

        return [];
    };


    // =====================================================
    // FETCH ORDERS
    // =====================================================

    const fetchOrders = useCallback(async () => {
        try {
            const response =
                await getAdminOrders();

            const data =
                normalizeResponseData(response);

            setOrders(data);

            return data;
        } catch (error) {
            console.error(
                "Failed to fetch orders:",
                error
            );

            const message =
                getErrorMessage(
                    error,
                    "Failed to load orders."
                );

            toast.error(message);

            setOrders([]);

            return [];
        }
    }, []);


    // =====================================================
    // FETCH DELIVERY RIDERS
    // =====================================================

    const fetchRiders = useCallback(async () => {
        try {
            const response =
                await getDeliveryRiders();

            const data =
                normalizeResponseData(response);

            setRiders(data);

            return data;
        } catch (error) {
            console.error(
                "Failed to fetch delivery riders:",
                error
            );

            setRiders([]);

            return [];
        }
    }, []);


    // =====================================================
    // INITIAL LOAD
    // =====================================================

    useEffect(() => {
        let mounted = true;

        const loadInitialData = async () => {
            setLoading(true);

            await Promise.all([
                fetchOrders(),
                fetchRiders(),
            ]);

            if (mounted) {
                setLoading(false);
            }
        };

        loadInitialData();

        return () => {
            mounted = false;
        };
    }, [
        fetchOrders,
        fetchRiders,
    ]);


    // =====================================================
    // TAB COUNTS
    // =====================================================

    const tabCounts = useMemo(() => {
        const counts = {};

        ORDER_TABS.forEach((tab) => {
            if (tab === "All") {
                counts[tab] = orders.length;
                return;
            }

            counts[tab] = orders.filter(
                (order) =>
                    order.status === tab
            ).length;
        });

        return counts;
    }, [orders]);


    // =====================================================
    // FILTER ORDERS
    // =====================================================

    const filteredOrders = useMemo(() => {
        const keyword = search
            .trim()
            .toLowerCase();

        return orders.filter((order) => {
            const orderId = String(
                order.id || ""
            ).toLowerCase();

            const orderNumber =
                getOrderNumber(order.id)
                    .toLowerCase();

            const customerName = String(
                order.customer_name || ""
            ).toLowerCase();

            const customerEmail = String(
                order.customer_email || ""
            ).toLowerCase();

            const matchesSearch =
                keyword === "" ||
                orderId.includes(keyword) ||
                orderNumber.includes(keyword) ||
                customerName.includes(keyword) ||
                customerEmail.includes(keyword);

            const matchesStatus =
                activeTab === "All" ||
                order.status === activeTab;

            return (
                matchesSearch &&
                matchesStatus
            );
        });
    }, [
        orders,
        search,
        activeTab,
    ]);


    // =====================================================
    // STATUS BADGE
    // =====================================================

    const getStatusBadge = (status) => {
        switch (status) {
            case "Pending":
                return "badge bg-warning text-dark";

            case "Accepted":
                return "badge bg-primary";

            case "Processing":
                return "badge bg-info text-dark";

            case "Ready":
                return "badge bg-success";

            case "Assigned":
                return "badge bg-secondary";

            case "Out for Delivery":
                return "badge bg-dark";

            case "Delivered":
                return "badge bg-success";

            case "Cancelled":
                return "badge bg-danger";

            default:
                return "badge bg-light text-dark";
        }
    };


    // =====================================================
    // PAYMENT METHOD
    // =====================================================

    const getPaymentMethod = (order) => {
        if (
            order &&
            order.payment_method
        ) {
            return order.payment_method;
        }

        if (
            order &&
            order.paymentMethod
        ) {
            return order.paymentMethod;
        }

        if (
            order &&
            order.payment &&
            order.payment.method
        ) {
            return order.payment.method;
        }

        return "N/A";
    };


    // =====================================================
    // FORMAT DATE
    // =====================================================

    const formatDate = (date) => {
        if (!date) {
            return "-";
        }

        const parsedDate = new Date(date);

        if (
            Number.isNaN(
                parsedDate.getTime()
            )
        ) {
            return "-";
        }

        return parsedDate.toLocaleDateString(
            "en-GB",
            {
                day: "2-digit",
                month: "short",
                year: "numeric",
            }
        );
    };


    // =====================================================
    // FORMAT AMOUNT
    // =====================================================

    const formatAmount = (amount) => {
        const numericAmount =
            Number(amount);

        if (
            Number.isNaN(
                numericAmount
            )
        ) {
            return "0.00";
        }

        return numericAmount.toFixed(2);
    };


    // =====================================================
    // GET ITEM COUNT
    // =====================================================

    const getItemCount = (order) => {
        if (
            order &&
            order.item_count !== undefined &&
            order.item_count !== null
        ) {
            return order.item_count;
        }

        if (
            order &&
            order.items_count !== undefined &&
            order.items_count !== null
        ) {
            return order.items_count;
        }

        if (
            order &&
            Array.isArray(order.items)
        ) {
            return order.items.length;
        }

        return 0;
    };


    // =====================================================
    // UPDATE ORDER
    // =====================================================

    const handleUpdateOrder = (orderId) => {
        navigate(
            "/admin/orders/update/" +
            orderId
        );
    };


    // =====================================================
    // ACCEPT ORDER
    // =====================================================

    const handleAcceptOrder = async (
        orderId
    ) => {
        try {
            setAcceptingOrderId(orderId);

            await acceptAdminOrder(
                orderId
            );

            toast.success(
                "Order accepted successfully."
            );

            await fetchOrders();
        } catch (error) {
            console.error(
                "Accept order error:",
                error
            );

            const message =
                getErrorMessage(
                    error,
                    "Failed to accept order."
                );

            toast.error(message);
        } finally {
            setAcceptingOrderId(null);
        }
    };


    // =====================================================
    // ASSIGN DELIVERY RIDER
    // =====================================================

    const handleAssignDelivery = async (
        orderId
    ) => {
        const riderId =
            selectedRiders[orderId];

        if (!riderId) {
            toast.warning(
                "Please select a delivery rider."
            );

            return;
        }

        try {
            setAssigningOrderId(orderId);

            await assignDeliveryRider(
                orderId,
                riderId
            );

            toast.success(
                "Delivery rider assigned successfully."
            );

            setSelectedRiders(
                (previous) => {
                    const updated = {
                        ...previous,
                    };

                    delete updated[orderId];

                    return updated;
                }
            );

            await fetchOrders();
        } catch (error) {
            console.error(
                "Assign rider error:",
                error
            );

            const message =
                getErrorMessage(
                    error,
                    "Failed to assign delivery rider."
                );

            toast.error(message);
        } finally {
            setAssigningOrderId(null);
        }
    };


    // =====================================================
    // REFRESH
    // =====================================================

    const handleRefresh = async () => {
        try {
            setLoading(true);

            await Promise.all([
                fetchOrders(),
                fetchRiders(),
            ]);

            toast.success(
                "Orders refreshed successfully."
            );
        } catch (error) {
            console.error(
                "Refresh error:",
                error
            );
        } finally {
            setLoading(false);
        }
    };


    // =====================================================
    // CHANGE RIDER
    // =====================================================

    const handleRiderChange = (
        orderId,
        riderId
    ) => {
        setSelectedRiders(
            (previous) => ({
                ...previous,
                [orderId]: riderId,
            })
        );
    };


    // =====================================================
    // LOADING SCREEN
    // =====================================================

    if (loading) {
        return (
            <DashboardLayout>

                <div className="container-fluid py-5">

                    <div className="text-center">

                        <div
                            className="spinner-border text-primary"
                            role="status"
                        >
                            <span className="visually-hidden">
                                Loading...
                            </span>
                        </div>

                        <h5 className="mt-3">
                            Loading Orders...
                        </h5>

                    </div>

                </div>

            </DashboardLayout>
        );
    }


    // =====================================================
    // MAIN RETURN
    // =====================================================

    return (
        <DashboardLayout>

            <div className="container-fluid py-4">

                {/* =================================================
                    PAGE HEADER
                ================================================= */}

                <div className="d-flex justify-content-between align-items-center mb-4">

                    <div>

                        <h2 className="fw-bold mb-1">
                            Order Management
                        </h2>

                        <p className="text-muted mb-0">
                            Manage all customer orders from one place.
                        </p>

                    </div>


                    <button
                        type="button"
                        className="btn btn-primary"
                        onClick={handleRefresh}
                        disabled={
                            loading ||
                            acceptingOrderId ||
                            assigningOrderId
                        }
                    >
                        Refresh
                    </button>

                </div>


                {/* =================================================
                    STATUS TABS
                ================================================= */}

                <div className="card shadow-sm mb-4">

                    <div className="card-body">

                        <ul className="nav nav-tabs flex-wrap">

                            {ORDER_TABS.map(
                                (tab) => {

                                    const isActive =
                                        activeTab ===
                                        tab;

                                    return (
                                        <li
                                            className="nav-item"
                                            key={tab}
                                        >

                                            <button
                                                type="button"
                                                className={
                                                    isActive
                                                        ? "nav-link active"
                                                        : "nav-link"
                                                }
                                                onClick={() =>
                                                    setActiveTab(
                                                        tab
                                                    )
                                                }
                                            >

                                                {tab}

                                                <span
                                                    className={
                                                        isActive
                                                            ? "badge bg-primary ms-2"
                                                            : "badge bg-secondary ms-2"
                                                    }
                                                >
                                                    {
                                                        tabCounts[
                                                            tab
                                                        ]
                                                    }
                                                </span>

                                            </button>

                                        </li>
                                    );
                                }
                            )}

                        </ul>

                    </div>

                </div>


                {/* =================================================
                    SEARCH
                ================================================= */}

                <div className="card shadow-sm mb-4">

                    <div className="card-body">

                        <div className="row g-3 align-items-end">

                            <div className="col-lg-6">

                                <label
                                    htmlFor="orderSearch"
                                    className="form-label fw-semibold"
                                >
                                    Search Orders
                                </label>

                                <input
                                    id="orderSearch"
                                    type="text"
                                    className="form-control"
                                    placeholder="Search Order ID, Customer Name, Email..."
                                    value={search}
                                    onChange={(event) =>
                                        setSearch(
                                            event.target.value
                                        )
                                    }
                                />

                            </div>


                            <div className="col-lg-6">

                                <div className="text-lg-end">

                                    <span className="text-muted">
                                        Showing
                                    </span>

                                    <strong className="text-primary mx-2">
                                        {
                                            filteredOrders.length
                                        }
                                    </strong>

                                    <span>
                                        Orders
                                    </span>

                                </div>

                            </div>

                        </div>

                    </div>

                </div>


                {/* =================================================
                    ORDERS TABLE
                ================================================= */}

                <div className="card shadow-sm">

                    <div className="card-header bg-white py-3">

                        <h5 className="mb-0 fw-bold">
                            Orders
                        </h5>

                    </div>


                    <div className="card-body p-0">

                        <div className="table-responsive">

                            <table className="table table-hover align-middle mb-0">

                                <thead className="table-light">

                                    <tr>

                                        <th>
                                            Order ID
                                        </th>

                                        <th>
                                            Customer
                                        </th>

                                        <th>
                                            Date
                                        </th>

                                        <th className="text-center">
                                            Items
                                        </th>

                                        <th>
                                            Total
                                        </th>

                                        <th>
                                            Payment
                                        </th>

                                        <th>
                                            Status
                                        </th>

                                        <th>
                                            Actions
                                        </th>

                                    </tr>

                                </thead>


                                <tbody>

                                    {filteredOrders.length ===
                                        0 && (
                                            <tr>

                                                <td
                                                    colSpan="8"
                                                    className="text-center py-5"
                                                >

                                                    <h5 className="mb-2">
                                                        No Orders Found
                                                    </h5>

                                                    <p className="text-muted mb-0">
                                                        There are no orders in this category.
                                                    </p>

                                                </td>

                                            </tr>
                                        )}


                                    {filteredOrders.length >
                                        0 &&
                                        filteredOrders.map(
                                            (order) => {

                                                // =================================================
                                                // ORDER DATA
                                                // =================================================

                                                const orderNumber =
                                                    getOrderNumber(
                                                        order.id
                                                    );

                                                const itemCount =
                                                    getItemCount(
                                                        order
                                                    );

                                                const paymentMethod =
                                                    getPaymentMethod(
                                                        order
                                                    );

                                                const statusBadge =
                                                    getStatusBadge(
                                                        order.status
                                                    );

                                                const customerName =
                                                    order.customer_name ||
                                                    "Unknown Customer";

                                                const customerEmail =
                                                    order.customer_email ||
                                                    "-";

                                                const totalAmount =
                                                    formatAmount(
                                                        order.total_amount
                                                    );

                                                const createdDate =
                                                    formatDate(
                                                        order.created_at
                                                    );

                                                const isAccepting =
                                                    acceptingOrderId ===
                                                    order.id;

                                                const isAssigning =
                                                    assigningOrderId ===
                                                    order.id;

                                                const selectedRider =
                                                    selectedRiders[
                                                        order.id
                                                    ] ||
                                                    "";


                                                return (
                                                    <tr
                                                        key={
                                                            order.id
                                                        }
                                                    >

                                                        {/* =================================================
                                                            ORDER ID
                                                        ================================================= */}

                                                        <td>

                                                            <strong className="text-primary">
                                                                {
                                                                    orderNumber
                                                                }
                                                            </strong>

                                                        </td>


                                                        {/* =================================================
                                                            CUSTOMER
                                                        ================================================= */}

                                                        <td>

                                                            <div className="fw-semibold">
                                                                {
                                                                    customerName
                                                                }
                                                            </div>

                                                            <small className="text-muted">
                                                                {
                                                                    customerEmail
                                                                }
                                                            </small>

                                                        </td>


                                                        {/* =================================================
                                                            DATE
                                                        ================================================= */}

                                                        <td>
                                                            {
                                                                createdDate
                                                            }
                                                        </td>


                                                        {/* =================================================
                                                            ITEMS
                                                        ================================================= */}

                                                        <td className="text-center">

                                                            <span className="badge bg-light text-dark border">
                                                                {
                                                                    itemCount
                                                                }
                                                            </span>

                                                        </td>


                                                        {/* =================================================
                                                            TOTAL
                                                        ================================================= */}

                                                        <td>

                                                            <strong className="text-success">
                                                                ৳{" "}
                                                                {
                                                                    totalAmount
                                                                }
                                                            </strong>

                                                        </td>


                                                        {/* =================================================
                                                            PAYMENT
                                                        ================================================= */}

                                                        <td>

                                                            <span className="badge bg-secondary">
                                                                {
                                                                    paymentMethod
                                                                }
                                                            </span>

                                                        </td>


                                                        {/* =================================================
                                                            STATUS
                                                        ================================================= */}

                                                        <td>

                                                            <span
                                                                className={
                                                                    statusBadge
                                                                }
                                                            >
                                                                {
                                                                    order.status ||
                                                                    "Unknown"
                                                                }
                                                            </span>

                                                        </td>


                                                        {/* =================================================
                                                            ACTIONS
                                                        ================================================= */}

                                                        <td>

                                                            <div className="d-flex flex-wrap gap-2">

                                                                {/* =========================================
                                                                    ACCEPT
                                                                ========================================= */}

                                                                {order.status ===
                                                                    "Pending" && (
                                                                        <button
                                                                            type="button"
                                                                            className="btn btn-success btn-sm"
                                                                            onClick={() =>
                                                                                handleAcceptOrder(
                                                                                    order.id
                                                                                )
                                                                            }
                                                                            disabled={
                                                                                isAccepting
                                                                            }
                                                                        >
                                                                            {isAccepting
                                                                                ? "Accepting..."
                                                                                : "Accept"}
                                                                        </button>
                                                                    )}


                                                                {/* =========================================
                                                                    UPDATE
                                                                ========================================= */}

                                                                {(
                                                                    order.status ===
                                                                        "Pending" ||
                                                                    order.status ===
                                                                        "Ready"
                                                                ) && (
                                                                        <button
                                                                            type="button"
                                                                            className="btn btn-warning btn-sm"
                                                                            onClick={() =>
                                                                                handleUpdateOrder(
                                                                                    order.id
                                                                                )
                                                                            }
                                                                        >
                                                                            Update
                                                                        </button>
                                                                    )}


                                                                {/* =========================================
                                                                    ASSIGN RIDER
                                                                ========================================= */}

                                                                {order.status ===
                                                                    "Ready" && (
                                                                        <div className="d-flex gap-2">

                                                                            <select
                                                                                className="form-select form-select-sm"
                                                                                value={
                                                                                    selectedRider
                                                                                }
                                                                                onChange={(
                                                                                    event
                                                                                ) =>
                                                                                    handleRiderChange(
                                                                                        order.id,
                                                                                        event
                                                                                            .target
                                                                                            .value
                                                                                    )
                                                                                }
                                                                            >

                                                                                <option value="">
                                                                                    Select Rider
                                                                                </option>


                                                                                {riders
                                                                                    .filter(
                                                                                        (
                                                                                            rider
                                                                                        ) =>
                                                                                            rider.is_active
                                                                                    )
                                                                                    .map(
                                                                                        (
                                                                                            rider
                                                                                        ) => {

                                                                                            const riderName =
                                                                                                rider.username ||
                                                                                                rider.name ||
                                                                                                rider.email ||
                                                                                                "Rider";

                                                                                            return (
                                                                                                <option
                                                                                                    key={
                                                                                                        rider.id
                                                                                                    }
                                                                                                    value={
                                                                                                        rider.id
                                                                                                    }
                                                                                                >
                                                                                                    {
                                                                                                        riderName
                                                                                                    }
                                                                                                </option>
                                                                                            );
                                                                                        }
                                                                                    )}

                                                                            </select>


                                                                            <button
                                                                                type="button"
                                                                                className="btn btn-primary btn-sm"
                                                                                onClick={() =>
                                                                                    handleAssignDelivery(
                                                                                        order.id
                                                                                    )
                                                                                }
                                                                                disabled={
                                                                                    isAssigning
                                                                                }
                                                                            >
                                                                                {isAssigning
                                                                                    ? "Assigning..."
                                                                                    : "Assign"}
                                                                            </button>

                                                                        </div>
                                                                    )}

                                                            </div>

                                                        </td>

                                                    </tr>
                                                );
                                            }
                                        )}

                                </tbody>

                            </table>

                        </div>

                    </div>

                </div>

            </div>

        </DashboardLayout>
    );
};


// =========================================================
// EXPORT
// =========================================================

export default AdminOrders;
```
