
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


const AdminOrders = () => {
    const navigate = useNavigate();

    const [orders, setOrders] = useState([]);
    const [riders, setRiders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState("");
    const [statusFilter, setStatusFilter] = useState("All");
    const [assigningOrderId, setAssigningOrderId] = useState(null);
    const [acceptingOrderId, setAcceptingOrderId] = useState(null);
    const [selectedRiders, setSelectedRiders] = useState({});


    // =========================================================
    // FETCH ORDERS
    // =========================================================

    const fetchOrders = useCallback(async () => {
        try {
            setLoading(true);

            const response = await getAdminOrders();

            const data = response?.data;

            setOrders(
                Array.isArray(data)
                    ? data
                    : []
            );

        } catch (error) {
            console.error(
                "Failed to load admin orders:",
                error
            );

            const message =
                error?.response?.data?.detail ||
                "Failed to load orders.";

            toast.error(message);

            setOrders([]);

        } finally {
            setLoading(false);
        }
    }, []);


    // =========================================================
    // LOAD ORDERS
    // =========================================================

    const fetchRiders = useCallback(async () => {
        try {
            const response = await getDeliveryRiders();
            setRiders(response?.data?.results || []);
        } catch (error) {
            console.error("Failed to load delivery riders:", error);
        }
    }, []);

    useEffect(() => {
        const timer = window.setTimeout(() => {
            void fetchOrders();
            void fetchRiders();
        }, 0);

        return () => {
            window.clearTimeout(timer);
        };
    }, [fetchOrders, fetchRiders]);


    // =========================================================
    // FILTER ORDERS
    // =========================================================

    const filteredOrders = useMemo(() => {
        const keyword = search
            .trim()
            .toLowerCase();

        return orders.filter((order) => {

            const orderId =
                String(order.id || "");

            const orderNumber =
                `ORD${String(order.id).padStart(3, "0")}`;

            const customerName =
                String(
                    order.customer_name || ""
                ).toLowerCase();

            const customerEmail =
                String(
                    order.customer_email || ""
                ).toLowerCase();

            const status =
                String(
                    order.status || ""
                ).toLowerCase();

            const paymentMethod =
                String(
                    order.payment_method || ""
                ).toLowerCase();


            const matchesSearch =
                !keyword ||
                orderId.includes(keyword) ||
                orderNumber
                    .toLowerCase()
                    .includes(keyword) ||
                customerName.includes(keyword) ||
                customerEmail.includes(keyword) ||
                status.includes(keyword) ||
                paymentMethod.includes(keyword);


            const matchesStatus =
                statusFilter === "All" ||
                order.status === statusFilter;


            return (
                matchesSearch &&
                matchesStatus
            );
        });

    }, [
        orders,
        search,
        statusFilter,
    ]);


    // =========================================================
    // STATUS BADGE
    // =========================================================

    const getStatusBadge = (status) => {

    switch (status) {

        case "Pending":
            return "badge bg-warning text-dark";

        case "Accepted":
            return "badge bg-primary";

        case "Processing":
            return "badge bg-info";

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


    // =========================================================
    // PAYMENT METHOD
    // =========================================================

    const getPaymentMethod = (order) => {

        return (
            order.payment_method ||
            "N/A"
        );
    };


    // =========================================================
    // FORMAT DATE
    // =========================================================

    const formatDate = (date) => {

        if (!date) {
            return "N/A";
        }

        const parsedDate =
            new Date(date);

        if (
            Number.isNaN(
                parsedDate.getTime()
            )
        ) {
            return "N/A";
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


    // =========================================================
    // FORMAT AMOUNT
    // =========================================================

    const formatAmount = (amount) => {

        const value =
            Number(amount);

        if (
            Number.isNaN(value)
        ) {
            return "0.00";
        }

        return value.toFixed(2);
    };


    // =========================================================
    // UPDATE ORDER
    // =========================================================

    const handleUpdateOrder = (id) => {

        navigate(
            `/admin/orders/update/${id}`
        );
    };

    // =========================================================
// ACCEPT ORDER
// =========================================================

const handleAcceptOrder = async (orderId) => {

    if (!orderId) {
        return;
    }

    try {

        setAcceptingOrderId(orderId);

        const response = await acceptAdminOrder(
            orderId
        );

        toast.success(
            response?.data?.message ||
            "Order accepted successfully."
        );

        await fetchOrders();

    } catch (error) {

        console.error(
            "Failed to accept order:",
            error
        );

        toast.error(
            error?.response?.data?.detail ||
            error?.response?.data?.message ||
            "Failed to accept order."
        );

    } finally {

        setAcceptingOrderId(null);

    }
};
    const handleAssignDelivery = async (orderId) => {
        const riderId = selectedRiders[orderId];

        if (!riderId) {
            toast.warning("Please select a delivery rider first.");
            return;
        }

        try {
            setAssigningOrderId(orderId);
            await assignDeliveryRider(orderId, riderId);
            toast.success("Delivery rider assigned successfully.");
            setSelectedRiders((previous) => ({
                ...previous,
                [orderId]: "",
            }));
            await fetchOrders();
        } catch (error) {
            console.error("Failed to assign rider:", error);
            const detail =
                error?.response?.data?.detail ||
                error?.response?.data?.not_ready_items ||
                "Failed to assign delivery rider.";
            toast.error(typeof detail === "string" ? detail : "Failed to assign delivery rider.");
        } finally {
            setAssigningOrderId(null);
        }
    };


    // =========================================================
    // LOADING
    // =========================================================

    if (loading) {

        return (
            <DashboardLayout>

                <div className="container-fluid py-5 text-center">

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

            </DashboardLayout>
        );
    }


    // =========================================================
    // PAGE
    // =========================================================

    return (
        <DashboardLayout>

            <div className="container-fluid py-4">

                {/* =================================================
                    HEADER
                ================================================= */}

                <div className="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3 mb-4">

                    <div>

                        <h2 className="mb-1">
                            Order Management
                        </h2>

                        <p className="text-muted mb-0">
                            Manage customer orders
                            from the database.
                        </p>

                    </div>


                    <button
                        type="button"
                        className="btn btn-primary"
                        onClick={fetchOrders}
                    >
                        Refresh Orders
                    </button>

                </div>


                {/* =================================================
                    FILTERS
                ================================================= */}

                <div className="card shadow-sm mb-4">

                    <div className="card-body">

                        <div className="row g-3">

                            {/* SEARCH */}

                            <div className="col-md-7">

                                <label
                                    htmlFor="order-search"
                                    className="form-label fw-semibold"
                                >
                                    Search Orders
                                </label>

                                <input
                                    id="order-search"
                                    type="text"
                                    className="form-control"
                                    placeholder="Search by order ID, customer, email, status..."
                                    value={search}
                                    onChange={(event) =>
                                        setSearch(
                                            event.target.value
                                        )
                                    }
                                />

                            </div>


                            {/* STATUS FILTER */}

                            <div className="col-md-5">

                                <label
                                    htmlFor="status-filter"
                                    className="form-label fw-semibold"
                                >
                                    Filter by Status
                                </label>

                                <select
                                    id="status-filter"
                                    className="form-select"
                                    value={statusFilter}
                                    onChange={(event) =>
                                        setStatusFilter(
                                            event.target.value
                                        )
                                    }
                                >

<option value="Pending">
    Pending
</option>

<option value="Accepted">
    Accepted
</option>

<option value="Processing">
    Processing
</option>

<option value="Ready">
    Ready
</option>

<option value="Assigned">
    Assigned
</option>

<option value="Out for Delivery">
    Out for Delivery
</option>

<option value="Delivered">
    Delivered
</option>

<option value="Cancelled">
    Cancelled
</option>

                                </select>

                            </div>

                        </div>

                    </div>

                </div>


                {/* =================================================
                    ORDER COUNT
                ================================================= */}

                <div className="mb-3">

                    <strong>
                        Total Orders:
                    </strong>{" "}

                    {filteredOrders.length}

                </div>


                {/* =================================================
                    ORDERS TABLE
                ================================================= */}

                <div className="card shadow">

                    <div className="card-header bg-primary text-white">

                        <h5 className="mb-0">
                            Customer Orders
                        </h5>

                    </div>


                    <div className="card-body p-0">

                        <div className="table-responsive">

                            <table className="table table-bordered table-hover align-middle mb-0">

                                <thead className="table-dark">

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

                                        <th>
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
                                            Action
                                        </th>

                                    </tr>

                                </thead>


                                <tbody>

                                    {filteredOrders.length > 0 ? (

                                        filteredOrders.map(
                                            (order) => {

                                                const orderNumber =
                                                    `ORD${String(
                                                        order.id
                                                    ).padStart(
                                                        3,
                                                        "0"
                                                    )}`;

                                                return (

                                                    <tr
                                                        key={
                                                            order.id
                                                        }
                                                    >

                                                        {/* ORDER */}

                                                        <td>

                                                            <strong>
                                                                {
                                                                    orderNumber
                                                                }
                                                            </strong>

                                                        </td>


                                                        {/* CUSTOMER */}

                                                        <td>

                                                            <div>
                                                                <strong>
                                                                    {
                                                                        order.customer_name ||
                                                                        "Unknown Customer"
                                                                    }
                                                                </strong>
                                                            </div>

                                                            <small className="text-muted">
                                                                {
                                                                    order.customer_email ||
                                                                    "N/A"
                                                                }
                                                            </small>

                                                        </td>


                                                        {/* DATE */}

                                                        <td>

                                                            {
                                                                formatDate(
                                                                    order.created_at
                                                                )
                                                            }

                                                        </td>


                                                        {/* ITEMS */}

                                                        <td>

                                                            {
                                                                order.item_count ??
                                                                0
                                                            }

                                                        </td>


                                                        {/* TOTAL */}

                                                        <td>

                                                            <strong>
                                                                ৳
                                                                {
                                                                    formatAmount(
                                                                        order.total_amount
                                                                    )
                                                                }
                                                            </strong>

                                                        </td>


                                                        {/* PAYMENT */}

                                                        <td>

                                                            {
                                                                getPaymentMethod(
                                                                    order
                                                                )
                                                            }

                                                        </td>


                                                        {/* STATUS */}

                                                        <td>

                                                            <span
                                                                className={getStatusBadge(
                                                                    order.status
                                                                )}
                                                            >
                                                                {
                                                                    order.status ||
                                                                    "N/A"
                                                                }
                                                            </span>

                                                        </td>


                                                        {/* ACTION */}

<td>

    <div className="d-flex flex-column gap-2">

        {/* =================================================
            ACCEPT ORDER
        ================================================= */}

        {order.status === "Pending" && (

            <button
                type="button"
                className="btn btn-success btn-sm"
                onClick={() =>
                    handleAcceptOrder(
                        order.id
                    )
                }
                disabled={
                    acceptingOrderId ===
                    order.id
                }
            >

                {acceptingOrderId === order.id ? (

                    <>
                        <span
                            className="spinner-border spinner-border-sm me-1"
                            role="status"
                            aria-hidden="true"
                        />

                        Accepting...
                    </>

                ) : (

                    "Accept Order"

                )}

            </button>

        )}


        {/* =================================================
            DELIVERY RIDER ASSIGNMENT
        ================================================= */}

       {order.status === "Ready" && (

    <div className="d-flex gap-2 align-items-center">

        <select
            className="form-select form-select-sm"
            value={
                selectedRiders[
                    order.id
                ] || ""
            }
            onChange={(event) =>
                setSelectedRiders(
                    (previous) => ({
                        ...previous,
                        [order.id]:
                            event.target.value,
                    })
                )
            }
        >

            <option value="">
                Select rider
            </option>

            {riders
                .filter(
                    (rider) =>
                        rider.is_active
                )
                .map(
                    (rider) => (
                        <option
                            key={rider.id}
                            value={rider.id}
                        >
                            {rider.username}
                        </option>
                    )
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
                assigningOrderId ===
                order.id
            }
        >

            {assigningOrderId === order.id
                ? "Assigning..."
                : "Assign"}

        </button>

    </div>

)}

        {/* =================================================
            UPDATE ORDER
        ================================================= */}

       {(
    order.status === "Pending" ||
    order.status === "Ready"
) && (

    <button
        type="button"
        className="btn btn-warning btn-sm"
        onClick={() =>
            handleUpdateOrder(order.id)
        }
    >
        Update
    </button>

)}

    </div>

</td>

                                                    </tr>

                                                );
                                            }
                                        )

                                    ) : (

                                        <tr>

                                            <td
                                                colSpan="8"
                                                className="text-center py-5"
                                            >

                                                <h5>
                                                    No Orders Found
                                                </h5>

                                                <p className="text-muted mb-0">

                                                    {search ||
                                                    statusFilter !== "All"
                                                        ? "No orders match your search or filter."
                                                        : "There are no orders yet."}

                                                </p>

                                            </td>

                                        </tr>

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


export default AdminOrders;
