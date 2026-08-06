import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { toast } from "react-toastify";

import DashboardLayout from "../../../layouts/DashboardLayout";

import {
    getOrder,
    updateOrder,
} from "../../../services/orderService";

const UpdateOrder = () => {
    const { id } = useParams();
    const navigate = useNavigate();

    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

    const [formData, setFormData] = useState({
        status: "Pending",
    });

    useEffect(() => {
        const fetchOrder = async () => {
            try {
                const response = await getOrder(id);

                setFormData({
                    status:
                        response.data.status || "Pending",
                });
            } catch (error) {
                console.error(error);
                toast.error("Failed to load order.");
                navigate("/admin/orders");
            } finally {
                setLoading(false);
            }
        };

        fetchOrder();
    }, [id, navigate]);

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            setSaving(true);

            await updateOrder(id, formData);

            toast.success(
                "Order updated successfully."
            );

            navigate("/admin/orders");
        } catch (error) {
            console.error(error);
            toast.error("Failed to update order.");
        } finally {
            setSaving(false);
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
                        Loading Order...
                    </h5>

                </div>
            </DashboardLayout>
        );
    }

    return (
        <DashboardLayout>

            <div className="container py-4">

                <div className="row justify-content-center">

                    <div className="col-lg-6">

                        <div className="card shadow">

                            <div className="card-header bg-warning">

                                <h3 className="mb-0">
                                    Update Order Status
                                </h3>

                            </div>

                            <div className="card-body">

                                <form
                                    onSubmit={handleSubmit}
                                >

                                    <div className="mb-4">

                                        <label className="form-label">
                                            Status
                                        </label>

                                        <select
                                            className="form-select"
                                            name="status"
                                            value={
                                                formData.status
                                            }
                                            onChange={
                                                handleChange
                                            }
                                        >
                                            <option value="Pending">
                                                Pending
                                            </option>

                                            <option value="Processing">
                                                Processing
                                            </option>

                                            <option value="Delivered">
                                                Delivered
                                            </option>

                                            <option value="Cancelled">
                                                Cancelled
                                            </option>

                                        </select>

                                    </div>

                                    <button
                                        type="submit"
                                        className="btn btn-warning"
                                        disabled={saving}
                                    >
                                        {saving ? (
                                            <>
                                                <span
                                                    className="spinner-border spinner-border-sm me-2"
                                                    role="status"
                                                ></span>

                                                Saving...
                                            </>
                                        ) : (
                                            "Save Changes"
                                        )}
                                    </button>

                                    <button
                                        type="button"
                                        className="btn btn-secondary ms-2"
                                        onClick={() =>
                                            navigate(
                                                "/admin/orders"
                                            )
                                        }
                                    >
                                        Cancel
                                    </button>

                                </form>

                            </div>

                        </div>

                    </div>

                </div>

            </div>

        </DashboardLayout>
    );
};

export default UpdateOrder;