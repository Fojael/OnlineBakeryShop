import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { toast } from "react-toastify";

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

    const [currentStock, setCurrentStock] = useState(0);
    const [minimumStock, setMinimumStock] = useState(10);

    useEffect(() => {
        const fetchInventory = async () => {
            try {
                const response =
                    await getInventoryItem(id);

                const item = response.data;

                setProductName(item.product_name);
                setCurrentStock(item.current_stock);
                setMinimumStock(item.minimum_stock);

            } catch (error) {
                console.log(error);
                toast.error(
                    "Failed to load inventory."
                );

                navigate("/admin/inventory");
            } finally {
                setLoading(false);
            }
        };

        fetchInventory();
    }, [id, navigate]);

    // Remaining Stock
    const remainingStock = useMemo(() => {
        return (
            Number(currentStock) -
            Number(minimumStock)
        );
    }, [currentStock, minimumStock]);

    // Inventory Status
    const inventoryStatus = useMemo(() => {

        if (Number(currentStock) === 0)
            return "Out of Stock";

        if (
            Number(currentStock) <=
            Number(minimumStock)
        )
            return "Low Stock";

        return "In Stock";

    }, [currentStock, minimumStock]);

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (
            currentStock === "" ||
            minimumStock === ""
        ) {
            toast.warning(
                "Please fill all required fields."
            );
            return;
        }

        if (
            Number(currentStock) < 0 ||
            Number(minimumStock) < 0
        ) {
            toast.warning(
                "Stock values cannot be negative."
            );
            return;
        }

        try {
            setSaving(true);

            await updateInventory(id, {
                current_stock: Number(currentStock),
                minimum_stock: Number(minimumStock),
            });

            toast.success(
                "Inventory updated successfully."
            );

            navigate("/admin/inventory");

        } catch (error) {

            console.log(error);

            toast.error(
                "Failed to update inventory."
            );

        } finally {

            setSaving(false);

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
                    Loading Inventory...
                </h4>

            </div>
        );
    }

    return (
        <div className="container py-4">

            <div className="row justify-content-center">

                <div className="col-lg-8">

                    <div className="card shadow">

                        <div className="card-header bg-primary text-white">

                            <h3 className="mb-0">
                                Update Inventory
                            </h3>

                        </div>

                        <div className="card-body">

                            <form
                                onSubmit={handleSubmit}
                            >

                                {/* Product Name */}

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

                                {/* Current Stock */}

                                <div className="mb-3">

                                    <label className="form-label">
                                        Current Stock
                                    </label>

                                    <input
                                        type="number"
                                        min="0"
                                        className="form-control"
                                        value={
                                            currentStock
                                        }
                                        onChange={(e) =>
                                            setCurrentStock(
                                                e.target
                                                    .value
                                            )
                                        }
                                    />

                                </div>

                                {/* Minimum Stock */}

                                <div className="mb-3">

                                    <label className="form-label">
                                        Minimum Stock
                                    </label>

                                    <input
                                        type="number"
                                        min="0"
                                        className="form-control"
                                        value={
                                            minimumStock
                                        }
                                        onChange={(e) =>
                                            setMinimumStock(
                                                e.target
                                                    .value
                                            )
                                        }
                                    />

                                </div>

                                {/* Remaining Stock */}

                                <div className="mb-3">

                                    <label className="form-label">
                                        Remaining
                                        Stock
                                    </label>

                                    <input
                                        type="text"
                                        className="form-control"
                                        value={
                                            remainingStock
                                        }
                                        readOnly
                                    />

                                </div>

                                {/* Status */}

                                <div className="mb-4">

                                    <label className="form-label">
                                        Inventory
                                        Status
                                    </label>

                                    <div>

                                        {inventoryStatus ===
                                        "In Stock" ? (

                                            <span className="badge bg-success fs-6">
                                                In Stock
                                            </span>

                                        ) : inventoryStatus ===
                                          "Low Stock" ? (

                                            <span className="badge bg-warning text-dark fs-6">
                                                Low
                                                Stock
                                            </span>

                                        ) : (

                                            <span className="badge bg-danger fs-6">
                                                Out
                                                of
                                                Stock
                                            </span>

                                        )}

                                    </div>

                                </div>

                                {/* Buttons */}

                                <button
                                    className="btn btn-primary"
                                    disabled={
                                        saving
                                    }
                                >
                                    {saving
                                        ? "Updating..."
                                        : "Save Changes"}
                                </button>

                                <button
                                    type="button"
                                    className="btn btn-secondary ms-2"
                                    onClick={() =>
                                        navigate(
                                            "/admin/inventory"
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
    );
};

export default UpdateInventory;