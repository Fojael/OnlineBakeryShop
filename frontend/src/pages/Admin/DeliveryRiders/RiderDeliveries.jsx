import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import DashboardLayout from "../../../layouts/DashboardLayout";
import api from "../../../services/api";

const RiderDeliveries = () => {
    const { riderId } = useParams();
    const [rider, setRider] = useState(null);
    const [deliveries, setDeliveries] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        let ignore = false;

        api.get(`orders/admin/delivery-riders/${riderId}/deliveries/`)
            .then((response) => {
                if (!ignore) {
                    setRider(response.data?.rider || null);
                    setDeliveries(response.data?.results || []);
                }
            })
            .catch((requestError) => {
                if (!ignore) {
                    setError(
                        requestError.response?.data?.detail ||
                        "Failed to load rider deliveries."
                    );
                }
            })
            .finally(() => {
                if (!ignore) {
                    setLoading(false);
                }
            });

        return () => {
            ignore = true;
        };
    }, [riderId]);

    return (
        <DashboardLayout>
            <div className="container-fluid py-4">
                <div className="d-flex justify-content-between align-items-center mb-4">
                    <div>
                        <h2 className="mb-1">Rider Deliveries</h2>
                        <p className="text-muted mb-0">
                            {rider?.name || rider?.username || "Delivery rider"}
                        </p>
                    </div>
                    <Link className="btn btn-outline-secondary" to="/admin/riders">
                        Back to Riders
                    </Link>
                </div>

                {error && <div className="alert alert-danger">{error}</div>}

                <div className="card border-0 shadow-sm">
                    <div className="table-responsive">
                        <table className="table table-hover align-middle mb-0">
                            <thead>
                                <tr>
                                    <th>Delivery</th>
                                    <th>Order</th>
                                    <th>Customer</th>
                                    <th>Status</th>
                                    <th>Assigned</th>
                                </tr>
                            </thead>
                            <tbody>
                                {loading ? (
                                    <tr><td colSpan="5">Loading deliveries...</td></tr>
                                ) : deliveries.length === 0 ? (
                                    <tr><td colSpan="5">No deliveries assigned.</td></tr>
                                ) : (
                                    deliveries.map((delivery) => (
                                        <tr key={delivery.id}>
                                            <td>#{delivery.id}</td>
                                            <td>#{delivery.order}</td>
                                            <td>{delivery.order_details?.customer_name || "-"}</td>
                                            <td>{delivery.status}</td>
                                            <td>{delivery.assigned_at ? new Date(delivery.assigned_at).toLocaleString() : "-"}</td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
};

export default RiderDeliveries;
