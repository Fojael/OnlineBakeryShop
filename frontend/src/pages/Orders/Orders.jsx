import {
    useCallback,
    useEffect,
    useMemo,
    useState,
} from "react";
import { toast } from "react-toastify";

import { getOrders } from "../../services/orderService";

const Orders = () => {
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
                String(order.id).includes(keyword) ||
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
            <div className="container py-5 text-center">
                <div
                    className="spinner-border text-primary"
                    role="status"
                >
                    <span className="visually-hidden">
                        Loading...
                    </span>
                </div>

                <h4 className="mt-3">
                    Loading Orders...
                </h4>
            </div>
        );
    }

    return (
        <div className="container py-5">

            <div className="d-flex justify-content-between align-items-center mb-4">

                <div>
                    <h2>My Orders</h2>

                    <p className="text-muted mb-0">
                        Total Orders:
                        <strong>
                            {" "}
                            {filteredOrders.length}
                        </strong>
                    </p>
                </div>

                <div style={{ width: "300px" }}>
                    <input
                        type="text"
                        className="form-control"
                        placeholder="Search Order..."
                        value={search}
                        onChange={(e) =>
                            setSearch(e.target.value)
                        }
                    />
                </div>

            </div>

            <div className="card shadow">

                <div className="card-body">

                    <div className="table-responsive">

                        <table className="table table-bordered table-hover align-middle">

                            <thead className="table-dark">

                                <tr>
                                    <th>Order</th>
                                    <th>Date</th>
                                    <th>Total</th>
                                    <th>Status</th>
                                </tr>

                            </thead>

                            <tbody>

                                {filteredOrders.length > 0 ? (

                                    filteredOrders.map((order) => (

                                        <tr key={order.id}>

                                            <td>
                                                ORD
                                                {String(order.id).padStart(
                                                    3,
                                                    "0"
                                                )}
                                            </td>

                                            <td>
                                                {new Date(
                                                    order.created_at
                                                ).toLocaleDateString()}
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

                                        </tr>

                                    ))

                                ) : (

                                    <tr>

                                        <td
                                            colSpan="4"
                                            className="text-center py-4"
                                        >
                                            No orders found.
                                        </td>

                                    </tr>

                                )}

                            </tbody>

                        </table>

                    </div>

                </div>

            </div>

        </div>
    );
};

export default Orders;