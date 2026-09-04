import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { toast } from "react-toastify";

import DashboardLayout from "../../../layouts/DashboardLayout";

import {
    getInventoryItem,
    updateInventory,
} from "../../../services/inventoryService";

const UpdateInventory = () => {
    const { id } = useParams();
    const navigate = useNavigate();

    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

    const [productName, setProductName] = useState("");

    const [formData, setFormData] = useState({
        current_stock: 0,
        minimum_stock: 10,
    });

    useEffect(() => {
        let ignore = false;

        const loadInventory = async () => {
            try {
                const response = await getInventoryItem(id);

                if (ignore) return;

                const item = response.data;

                setProductName(item.product_name || "");

                setFormData({
                    current_stock: Number(item.current_stock),
                    minimum_stock: Number(item.minimum_stock),
                });

            } catch (error) {
                console.error(error);

                if (!ignore) {
                    toast.error("Failed to load inventory.");
                    navigate("/admin/inventory");
                }

            } finally {
                if (!ignore) {
                    setLoading(false);
                }
            }
        };

        loadInventory();

        return () => {
            ignore = true;
        };
    }, [id, navigate]);

    const handleChange = (e) => {
        const { name, value } = e.target;

        setFormData((prev) => ({
            ...prev,
            [name]: value,
        }));
    };

    const remainingStock = useMemo(() => {
        return (
            Number(formData.current_stock) -
            Number(formData.minimum_stock)
        );
    }, [formData]);

    const inventoryStatus = useMemo(() => {

        const stock = Number(formData.current_stock);
        const minimum = Number(formData.minimum_stock);

        if (stock === 0) return "Out of Stock";

        if (stock <= minimum) return "Low Stock";

        return "In Stock";

    }, [formData]);

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (
            formData.current_stock === "" ||
            formData.minimum_stock === ""
        ) {
            toast.warning("Please fill all required fields.");
            return;
        }

        if (
            Number(formData.current_stock) < 0 ||
            Number(formData.minimum_stock) < 0
        ) {
            toast.warning("Stock values cannot be negative.");
            return;
        }

        try {
            setSaving(true);

            await updateInventory(id, {
                current_stock: Number(formData.current_stock),
                minimum_stock: Number(formData.minimum_stock),
            });

            toast.success("Inventory updated successfully.");

            navigate("/admin/inventory");

        } catch (error) {

            console.error(error);

            toast.error("Failed to update inventory.");

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
                        Loading Inventory...
                    </h5>

                </div>
            </DashboardLayout>
        );
    }

    return (
        <DashboardLayout>

            <div className="row justify-content-center">

                <div className="col-lg-8">

                    <div className="card shadow">

                        <div className="card-header bg-primary text-white">

                            <h3 className="mb-0">
                                Update Inventory
                            </h3>

                        </div>

                        <div className="card-body">

                            <form onSubmit={handleSubmit}>

                                <div className="mb-3">

                                    <label className="form-label">
                                        Product Name
                                    </label>

                                    <input
                                        type="text"
                                        className="form-control"
                                        value={productName}
                                        readOnly
                                    />

                                </div>

                                <div className="mb-3">

                                    <label className="form-label">
                                        Current Stock
                                    </label>

                                    <input
                                        type="number"
                                        name="current_stock"
                                        min="0"
                                        className="form-control"
                                        value={formData.current_stock}
                                        onChange={handleChange}
                                    />

                                </div>

                                <div className="mb-3">

                                    <label className="form-label">
                                        Minimum Stock
                                    </label>

                                    <input
                                        type="number"
                                        name="minimum_stock"
                                        min="0"
                                        className="form-control"
                                        value={formData.minimum_stock}
                                        onChange={handleChange}
                                    />

                                </div>

                                <div className="mb-3">

                                    <label className="form-label">
                                        Remaining Stock
                                    </label>

                                    <input
                                        type="text"
                                        className="form-control"
                                        value={remainingStock}
                                        readOnly
                                    />

                                </div>

                                <div className="mb-4">

                                    <label className="form-label">
                                        Inventory Status
                                    </label>

                                    <div>

                                        {inventoryStatus === "In Stock" && (
                                            <span className="badge bg-success fs-6">
                                                In Stock
                                            </span>
                                        )}

                                        {inventoryStatus === "Low Stock" && (
                                            <span className="badge bg-warning text-dark fs-6">
                                                Low Stock
                                            </span>
                                        )}

                                        {inventoryStatus === "Out of Stock" && (
                                            <span className="badge bg-danger fs-6">
                                                Out of Stock
                                            </span>
                                        )}

                                    </div>

                                </div>

                                <div className="d-flex gap-2">

                                    <button
                                        type="submit"
                                        className="btn btn-primary"
                                        disabled={saving}
                                    >
                                        {saving
                                            ? "Updating..."
                                            : "Save Changes"}
                                    </button>

                                    <button
                                        type="button"
                                        className="btn btn-secondary"
                                        disabled={saving}
                                        onClick={() =>
                                            navigate("/admin/inventory")
                                        }
                                    >
                                        Cancel
                                    </button>

                                </div>

                            </form>

                        </div>

                    </div>

                </div>

            </div>

        </DashboardLayout>
    );
};

export default UpdateInventory;