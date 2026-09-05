import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { toast } from "react-toastify";

import DashboardLayout from "../../../layouts/DashboardLayout";
import { getInventory } from "../../../services/inventoryService";

const Inventory = () => {
    const [inventory, setInventory] = useState([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState("");

    useEffect(() => {
        let ignore = false;

        const loadInventory = async () => {
            try {
                const response = await getInventory();

                if (!ignore) {
                    setInventory(response.data || []);
                }
            } catch (error) {
                console.error(error);

                if (!ignore) {
                    toast.error("Failed to load inventory.");
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
    }, []);

    const filteredInventory = useMemo(() => {
        return inventory.filter((item) =>
            item.product_name
                ?.toLowerCase()
                .includes(search.toLowerCase())
        );
    }, [inventory, search]);

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

            <div className="container-fluid py-4">

                {/* Header */}

                <div className="d-flex justify-content-between align-items-center mb-4">

                    <div>

                        <h2 className="fw-bold">
                            Inventory Management
                        </h2>

                        <p className="text-muted mb-0">
                            Total Products :
                            <strong>
                                {" "}
                                {filteredInventory.length}
                            </strong>
                        </p>

                    </div>

                    <Link
                        to="/admin/dashboard"
                        className="btn btn-outline-dark"
                    >
                        Back to Dashboard
                    </Link>

                    <Link
                        to="/admin/inventory/transactions"
                        className="btn btn-primary ms-2"
                    >
                        Stock Movements
                    </Link>

                    <Link
                        to="/admin/inventory/batches"
                        className="btn btn-outline-primary ms-2"
                    >
                        Production Batches
                    </Link>

                </div>

                {/* Search */}

                <div className="row mb-4">

                    <div className="col-md-4">

                        <input
                            type="text"
                            className="form-control"
                            placeholder="Search Product..."
                            value={search}
                            onChange={(e) =>
                                setSearch(e.target.value)
                            }
                        />

                    </div>

                </div>

                {/* Table */}

                <div className="card shadow-sm">

                    <div className="card-body">

                        <div className="table-responsive">

                            <table className="table table-hover align-middle">

                                <thead className="table-dark">

                                    <tr>

                                        <th>ID</th>
                                        <th>Product</th>
                                        <th>Current Stock</th>
                                        <th>Minimum Stock</th>
                                        <th>Remaining Stock</th>
                                        <th>Status</th>
                                        <th width="170">
                                            Actions
                                        </th>

                                    </tr>

                                </thead>

                                <tbody>

                                    {filteredInventory.length > 0 ? (

                                        filteredInventory.map((item) => (

                                            <tr key={item.id}>

                                                <td>{item.id}</td>

                                                <td>
                                                    <strong>
                                                        {item.product_name}
                                                    </strong>
                                                </td>

                                                <td>
                                                    {item.current_stock}
                                                </td>

                                                <td>
                                                    {item.minimum_stock}
                                                </td>

                                                <td>
                                                    <strong>
                                                        {item.remaining_stock}
                                                    </strong>
                                                </td>

                                                <td>

                                                    {item.status ===
                                                    "In Stock" ? (

                                                        <span className="badge bg-success">
                                                            In Stock
                                                        </span>

                                                    ) : item.status ===
                                                      "Low Stock" ? (

                                                        <span className="badge bg-warning text-dark">
                                                            Low Stock
                                                        </span>

                                                    ) : (

                                                        <span className="badge bg-danger">
                                                            Out of Stock
                                                        </span>

                                                    )}

                                                </td>

                                                <td>

                                                    <Link
                                                        to={`/admin/inventory/update/${item.id}`}
                                                        className="btn btn-primary btn-sm"
                                                    >
                                                        Update Stock
                                                    </Link>

                                                </td>

                                            </tr>

                                        ))

                                    ) : (

                                        <tr>

                                            <td
                                                colSpan="7"
                                                className="text-center py-5"
                                            >

                                                <h5 className="text-muted">
                                                    No inventory records found.
                                                </h5>

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

export default Inventory;