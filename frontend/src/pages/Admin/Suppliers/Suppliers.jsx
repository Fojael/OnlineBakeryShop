import { useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { toast } from "react-toastify";

import DashboardLayout from "../../../layouts/DashboardLayout";

import {
    getSuppliers,
    deleteSupplier,
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
            "Are you sure you want to delete this supplier?"
        );

        if (!confirmDelete) return;

        try {
            await deleteSupplier(id);

            toast.success("Supplier deleted successfully.");

            fetchSuppliers();
        } catch (error) {
            console.log(error);
            toast.error("Failed to delete supplier.");
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
                            <th>Supplier Name</th>
                            <th>Company</th>
                            <th>Phone</th>
                            <th>Email</th>
                            <th>Address</th>
                            <th>Created</th>
                            <th width="170">
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

                                    <td>{supplier.company}</td>

                                    <td>{supplier.phone}</td>

                                    <td>{supplier.email}</td>

                                    <td>{supplier.address}</td>

                                    <td>
                                        {new Date(
                                            supplier.created_at
                                        ).toLocaleDateString()}
                                    </td>

                                    <td>

                                        <Link
                                            to={`/admin/suppliers/edit/${supplier.id}`}
                                            className="btn btn-warning btn-sm me-2"
                                        >
                                            Edit
                                        </Link>

                                        <button
                                            className="btn btn-danger btn-sm"
                                            onClick={() =>
                                                handleDelete(
                                                    supplier.id
                                                )
                                            }
                                        >
                                            Delete
                                        </button>

                                    </td>

                                </tr>

                            ))

                        ) : (

                            <tr>

                                <td
                                    colSpan="8"
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