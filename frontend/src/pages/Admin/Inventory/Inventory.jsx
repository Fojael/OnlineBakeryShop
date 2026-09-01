import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { toast } from "react-toastify";

import { getInventory } from "../../../services/inventoryService";

const Inventory = () => {
    const [inventory, setInventory] = useState([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState("");

    useEffect(() => {
        const fetchInventory = async () => {
            try {
                setLoading(true);

                const response = await getInventory();

                setInventory(response.data);
            } catch (error) {
                console.log(error);
                toast.error("Failed to load inventory.");
            } finally {
                setLoading(false);
            }
        };

        fetchInventory();
    }, []);

    // Search Inventory
    const filteredInventory = useMemo(() => {
        return inventory.filter((item) =>
            item.product_name
                .toLowerCase()
                .includes(search.toLowerCase())
        );
    }, [inventory, search]);

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

            {/* Header */}

            <div className="d-flex justify-content-between align-items-center mb-4">

                <div>

                    <h2 className="fw-bold">
                        Inventory Management
                    </h2>

                    <p className="text-muted">
                        Total Products :
                        <strong>
                            {" "}
                            {filteredInventory.length}
                        </strong>
                    </p>

                </div>

                <Link to="/admin/dashboard" className="btn btn-outline-dark btn-sm">
                    Back to Dashboard
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

            {/* Inventory Table */}

            <div className="table-responsive shadow-sm">

                <table className="table table-striped table-hover align-middle">

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

                                    <td className="fw-semibold">
                                        {item.product_name}
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

                                    <h5>
                                        No inventory records found.
                                    </h5>

                                </td>

                            </tr>

                        )}

                    </tbody>

                </table>

            </div>

        </div>
    );
};

export default Inventory;