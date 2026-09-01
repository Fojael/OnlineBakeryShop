import { useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { toast } from "react-toastify";

import DashboardLayout from "../../../layouts/DashboardLayout";

import {
    getSuppliers,
    deleteSupplier,
    activateSupplier,
    deactivateSupplier,
} from "../../../services/supplierService";

const Suppliers = () => {
    const [suppliers, setSuppliers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState("");

    const fetchSuppliers = useCallback(async () => {
        try {
            setLoading(true);

            const response = await getSuppliers();

            setSuppliers(response.data);
        } catch (error) {
            console.log(error);
            toast.error("Failed to load suppliers.");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        const timer = window.setTimeout(() => {
            void fetchSuppliers();
        }, 0);

        return () => window.clearTimeout(timer);
    }, [fetchSuppliers]);

    const handleDelete = async (id) => {
        const confirmDelete = window.confirm(
            "Delete Supplier?\n\nThis action cannot be undone."
        );

        if (!confirmDelete) return;

        try {
            await deleteSupplier(id);

            toast.success("Supplier deleted successfully.");

            void fetchSuppliers();
        } catch (error) {
            console.log(error);
            toast.error("Failed to delete supplier.");
        }
    };

    const handleActivate = async (id) => {
        try {
            await activateSupplier(id);
            toast.success("Supplier activated successfully.");
            void fetchSuppliers();
        } catch (error) {
            console.log(error);
            toast.error("Failed to activate supplier.");
        }
    };

    const handleDeactivate = async (id) => {
        try {
            await deactivateSupplier(id);
            toast.success("Supplier deactivated successfully.");
            void fetchSuppliers();
        } catch (error) {
            console.log(error);
            toast.error("Failed to deactivate supplier.");
        }
    };

    const filteredSuppliers = useMemo(() => {
        return suppliers.filter((supplier) =>
            supplier.name
                .toLowerCase()
                .includes(search.toLowerCase())
        );
    }, [suppliers, search]);

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
                        Loading Suppliers...
                    </h5>
                </div>
            </DashboardLayout>
        );
    }

    return (
        <DashboardLayout>

            <div className="d-flex justify-content-between align-items-center mb-4">

                <div>
                    <h2>Supplier Management</h2>
                    <p className="text-muted">
                        Total Suppliers :
                        <strong>
                            {" "}
                            {filteredSuppliers.length}
                        </strong>
                    </p>
                </div>

                <Link
                    to="/admin/suppliers/add"
                    className="btn btn-primary"
                >
                    Add Supplier
                </Link>

            </div>

            {/* Search */}

            <div className="row mb-3">

                <div className="col-md-4">

                    <input
                        type="text"
                        className="form-control"
                        placeholder="Search Supplier..."
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
                            <th>ID</th>
                            <th>Name</th>
                            <th>Company</th>
                            <th>Email</th>
                            <th>Phone</th>
                            <th>Status</th>
                            <th>Approval</th>
                            <th>Created</th>
                            <th width="220">
                                Actions
                            </th>
                        </tr>

                    </thead>

                    <tbody>

                        {filteredSuppliers.length > 0 ? (

                            filteredSuppliers.map((supplier) => (

                                <tr key={supplier.id}>

                                    <td>{supplier.id}</td>

                                    <td>{supplier.name}</td>

                                    <td>{supplier.company || "-"}</td>

                                    <td>{supplier.email || "-"}</td>

                                    <td>{supplier.phone || "-"}</td>

                                    <td>
                                        <span
                                            className={`badge ${supplier.is_active ? "bg-success" : "bg-secondary"}`}
                                        >
                                            {supplier.is_active ? "Active" : "Inactive"}
                                        </span>
                                    </td>

                                    <td>
                                        <span
                                            className={`badge ${supplier.is_approved ? "bg-info" : "bg-warning text-dark"}`}
                                        >
                                            {supplier.is_approved ? "Approved" : "Pending"}
                                        </span>
                                    </td>

                                    <td>
                                        {new Date(
                                            supplier.created_at
                                        ).toLocaleDateString()}
                                    </td>

                                    <td>
                                        <div className="d-flex flex-wrap gap-2">
                                            <Link
                                                to={`/admin/suppliers/edit/${supplier.id}`}
                                                className="btn btn-outline-primary btn-sm"
                                            >
                                                Edit
                                            </Link>

                                            {supplier.is_active ? (
                                                <button
                                                    className="btn btn-outline-secondary btn-sm"
                                                    onClick={() =>
                                                        handleDeactivate(
                                                            supplier.id
                                                        )
                                                    }
                                                >
                                                    Deactivate
                                                </button>
                                            ) : (
                                                <button
                                                    className="btn btn-outline-success btn-sm"
                                                    onClick={() =>
                                                        handleActivate(
                                                            supplier.id
                                                        )
                                                    }
                                                >
                                                    Activate
                                                </button>
                                            )}

                                            <button
                                                className="btn btn-outline-danger btn-sm"
                                                onClick={() =>
                                                    handleDelete(
                                                        supplier.id
                                                    )
                                                }
                                            >
                                                Delete
                                            </button>
                                        </div>
                                    </td>

                                </tr>

                            ))

                        ) : (

                            <tr>

                                <td
                                    colSpan="9"
                                    className="text-center py-4"
                                >
                                    No suppliers found.
                                </td>

                            </tr>

                        )}

                    </tbody>

                </table>

            </div>

        </DashboardLayout>
    );
};

export default Suppliers;