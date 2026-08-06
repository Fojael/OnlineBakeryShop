import {
    useCallback,
    useEffect,
    useMemo,
    useState,
} from "react";
import { Link } from "react-router-dom";
import { toast } from "react-toastify";

import DashboardLayout from "../../../layouts/DashboardLayout";
import { getOrders } from "../../../services/orderService";

const AdminOrders = () => {
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState("");

    const fetchOrders = useCallback(async () => {
        try {
            setLoading(true);

            const response = await getOrders();

            setOrders(response.data);
        } catch (error) {
            console.error(error);
            toast.error("Failed to load orders.");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        const timer = window.setTimeout(() => {
            void fetchOrders();
        }, 0);

        return () => window.clearTimeout(timer);
    }, [fetchOrders]);

    const filteredOrders = useMemo(() => {
        return orders.filter((order) => {
            const keyword = search.toLowerCase();

            return (
                String(order.id)
                    .toLowerCase()
                    .includes(keyword) ||
                order.customer_name
                    ?.toLowerCase()
                    .includes(keyword) ||
                order.status
                    .toLowerCase()
                    .includes(keyword)
            );
        });
    }, [orders, search]);

    const getStatusBadge = (status) => {
        switch (status) {
            case "Pending":
                return "badge bg-warning text-dark";

            case "Processing":
                return "badge bg-info";

            case "Delivered":
                return "badge bg-success";

            case "Cancelled":
                return "badge bg-danger";

            default:
                return "badge bg-secondary";
        }
    };

    if (loading) {
        return (
            <DashboardLayout>
                <div className="text-center py-5">
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

    return (
        <DashboardLayout>

            <div className="d-flex justify-content-between align-items-center mb-4">

                <div>

                    <h2>Order Management</h2>

                    <p className="text-muted">
                        Total Orders :
                        <strong>
                            {" "}
                            {filteredOrders.length}
                        </strong>
                    </p>

                </div>

            </div>

            {/* Search */}

            <div className="row mb-3">

                <div className="col-md-4">

                    <input
                        type="text"
                        className="form-control"
                        placeholder="Search Orders..."
                        value={search}
                        onChange={(e) =>
                            setSearch(e.target.value)
                        }
                    />

                </div>

            </div>

            {/* Table */}

            <div className="table-responsive">

                <table className="table table-bordered table-hover align-middle">

                    <thead className="table-dark">

                        <tr>
                            <th>Order</th>
                            <th>Customer</th>
                            <th>Total</th>
                            <th>Status</th>
                            <th width="140">
                                Action
                            </th>
                        </tr>

                    </thead>

                    <tbody>

                        {filteredOrders.length > 0 ? (

                            filteredOrders.map((order) => (

                                <tr key={order.id}>

                                    <td>
                                        ORD
                                        {String(
                                            order.id
                                        ).padStart(3, "0")}
                                    </td>

                                    <td>
                                        {order.customer_name}
                                    </td>

                                    <td>
                                        ৳
                                        {Number(
                                            order.total_amount
                                        ).toFixed(2)}
                                    </td>

                                    <td>
                                        <span
                                            className={getStatusBadge(
                                                order.status
                                            )}
                                        >
                                            {order.status}
                                        </span>
                                    </td>

                                    <td>

                                        <Link
                                            to={`/admin/orders/update/${order.id}`}
                                            className="btn btn-warning btn-sm"
                                        >
                                            Update
                                        </Link>

                                    </td>

                                </tr>

                            ))

                        ) : (

                            <tr>

                                <td
                                    colSpan="5"
                                    className="text-center py-4"
                                >
                                    No orders found.
                                </td>

                            </tr>

                        )}

                    </tbody>

                </table>

            </div>

        </DashboardLayout>
    );
};

export default AdminOrders;