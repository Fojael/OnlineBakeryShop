import { useCallback, useEffect, useMemo, useState } from "react";
import { toast } from "react-toastify";

import DashboardLayout from "../../../layouts/DashboardLayout";
import api from "../../../services/api";

const DeliveryRiders = () => {
    const [riders, setRiders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState("");
    const [submitting, setSubmitting] = useState(false);
    const [updatingId, setUpdatingId] = useState(null);
    const [editingId, setEditingId] = useState(null);
    const [editForm, setEditForm] = useState({
        username: "",
        email: "",
        first_name: "",
        last_name: "",
        phone: "",
    });
    const [formData, setFormData] = useState({
        username: "",
        email: "",
        password: "",
        first_name: "",
        last_name: "",
        phone: "",
    });

    const fetchRiders = useCallback(async () => {
        try {
            setLoading(true);
            const response = await api.get("orders/admin/delivery-riders/");
            setRiders(response.data?.results || []);
        } catch (error) {
            console.error(error);
            toast.error(error.response?.data?.detail || "Failed to load delivery riders.");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        void fetchRiders();
    }, [fetchRiders]);

    const filteredRiders = useMemo(() => {
        const query = search.toLowerCase();

        return riders.filter((rider) => {
            const fullName = `${rider.first_name || ""} ${rider.last_name || ""}`.trim();
            return (
                rider.username?.toLowerCase().includes(query) ||
                rider.email?.toLowerCase().includes(query) ||
                fullName.toLowerCase().includes(query) ||
                rider.phone?.toLowerCase().includes(query)
            );
        });
    }, [riders, search]);

    const handleChange = (event) => {
        const { name, value } = event.target;
        setFormData((previous) => ({
            ...previous,
            [name]: value,
        }));
    };

    const handleCreate = async (event) => {
        event.preventDefault();

        if (!formData.username.trim()) {
            toast.warning("Username is required.");
            return;
        }

        if (!formData.email.trim()) {
            toast.warning("Email is required.");
            return;
        }

        if (!formData.password.trim()) {
            toast.warning("Password is required.");
            return;
        }

        try {
            setSubmitting(true);
            await api.post("orders/admin/delivery-riders/create/", formData);
            toast.success("Delivery rider created successfully.");
            setFormData({
                username: "",
                email: "",
                password: "",
                first_name: "",
                last_name: "",
                phone: "",
            });
            void fetchRiders();
        } catch (error) {
            console.error(error);
            const detail =
                error.response?.data?.detail ||
                error.response?.data?.email?.[0] ||
                error.response?.data?.username?.[0] ||
                "Failed to create delivery rider.";
            toast.error(detail);
        } finally {
            setSubmitting(false);
        }
    };

    const handleEditStart = (rider) => {
        setEditingId(rider.id);
        setEditForm({
            username: rider.username || "",
            email: rider.email || "",
            first_name: rider.first_name || "",
            last_name: rider.last_name || "",
            phone: rider.phone || "",
        });
    };

    const handleEditCancel = () => {
        setEditingId(null);
        setEditForm({
            username: "",
            email: "",
            first_name: "",
            last_name: "",
            phone: "",
        });
    };

    const handleEditChange = (event) => {
        const { name, value } = event.target;
        setEditForm((previous) => ({
            ...previous,
            [name]: value,
        }));
    };

    const handleSaveEdit = async (riderId) => {
        try {
            setUpdatingId(riderId);
            await api.patch(`orders/admin/delivery-riders/${riderId}/update/`, editForm);
            toast.success("Rider details updated successfully.");
            handleEditCancel();
            void fetchRiders();
        } catch (error) {
            console.error(error);
            const detail =
                error.response?.data?.detail ||
                error.response?.data?.email?.[0] ||
                error.response?.data?.username?.[0] ||
                "Failed to update rider.";
            toast.error(detail);
        } finally {
            setUpdatingId(null);
        }
    };

    const handleToggleStatus = async (rider) => {
        const nextValue = !rider.is_active;

        try {
            setUpdatingId(rider.id);
            await api.post(`orders/admin/delivery-riders/${rider.id}/toggle-status/`, {
                is_active: nextValue,
            });
            toast.success(`Rider ${nextValue ? "activated" : "deactivated"} successfully.`);
            void fetchRiders();
        } catch (error) {
            console.error(error);
            toast.error(error.response?.data?.detail || "Failed to update rider status.");
        } finally {
            setUpdatingId(null);
        }
    };

    return (
        <DashboardLayout>
            <div className="container-fluid">
                <div className="d-flex justify-content-between align-items-center mb-4">
                    <div>
                        <h2 className="mb-1">Delivery Rider Management</h2>
                        <p className="text-muted mb-0">
                            Total riders: <strong>{filteredRiders.length}</strong>
                        </p>
                    </div>
                </div>

                <div className="card shadow-sm border-0 mb-4">
                    <div className="card-header bg-dark text-white">
                        <h5 className="mb-0">Create Delivery Rider</h5>
                    </div>

                    <div className="card-body">
                        <form onSubmit={handleCreate}>
                            <div className="row g-3">
                                <div className="col-md-4">
                                    <label className="form-label">Username</label>
                                    <input
                                        type="text"
                                        className="form-control"
                                        name="username"
                                        value={formData.username}
                                        onChange={handleChange}
                                    />
                                </div>

                                <div className="col-md-4">
                                    <label className="form-label">Email</label>
                                    <input
                                        type="email"
                                        className="form-control"
                                        name="email"
                                        value={formData.email}
                                        onChange={handleChange}
                                    />
                                </div>

                                <div className="col-md-4">
                                    <label className="form-label">Password</label>
                                    <input
                                        type="password"
                                        className="form-control"
                                        name="password"
                                        value={formData.password}
                                        onChange={handleChange}
                                    />
                                </div>

                                <div className="col-md-4">
                                    <label className="form-label">First Name</label>
                                    <input
                                        type="text"
                                        className="form-control"
                                        name="first_name"
                                        value={formData.first_name}
                                        onChange={handleChange}
                                    />
                                </div>

                                <div className="col-md-4">
                                    <label className="form-label">Last Name</label>
                                    <input
                                        type="text"
                                        className="form-control"
                                        name="last_name"
                                        value={formData.last_name}
                                        onChange={handleChange}
                                    />
                                </div>

                                <div className="col-md-4">
                                    <label className="form-label">Phone</label>
                                    <input
                                        type="text"
                                        className="form-control"
                                        name="phone"
                                        value={formData.phone}
                                        onChange={handleChange}
                                    />
                                </div>
                            </div>

                            <div className="mt-3">
                                <button type="submit" className="btn btn-primary" disabled={submitting}>
                                    {submitting ? "Creating..." : "Create Rider"}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>

                <div className="card shadow-sm border-0">
                    <div className="card-header bg-light">
                        <div className="d-flex justify-content-between align-items-center">
                            <h5 className="mb-0">Rider List</h5>
                            <input
                                type="text"
                                className="form-control w-50"
                                placeholder="Search rider"
                                value={search}
                                onChange={(event) => setSearch(event.target.value)}
                            />
                        </div>
                    </div>

                    <div className="card-body p-0">
                        {loading ? (
                            <div className="p-4 text-muted">Loading riders...</div>
                        ) : (
                            <div className="table-responsive">
                                <table className="table table-hover align-middle mb-0">
                                    <thead className="table-dark">
                                        <tr>
                                            <th>ID</th>
                                            <th>Username</th>
                                            <th>Name</th>
                                            <th>Email</th>
                                            <th>Phone</th>
                                            <th>Status</th>
                                            <th>Joined</th>
                                            <th>Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {filteredRiders.length > 0 ? (
                                            filteredRiders.map((rider) => {
                                                const isEditing = editingId === rider.id;

                                                return (
                                                    <tr key={rider.id}>
                                                        <td>{rider.id}</td>
                                                        <td>
                                                            {isEditing ? (
                                                                <input
                                                                    type="text"
                                                                    className="form-control form-control-sm"
                                                                    name="username"
                                                                    value={editForm.username}
                                                                    onChange={handleEditChange}
                                                                />
                                                            ) : (
                                                                rider.username
                                                            )}
                                                        </td>
                                                        <td>
                                                            {isEditing ? (
                                                                <div className="d-flex gap-2">
                                                                    <input
                                                                        type="text"
                                                                        className="form-control form-control-sm"
                                                                        name="first_name"
                                                                        value={editForm.first_name}
                                                                        onChange={handleEditChange}
                                                                        placeholder="First"
                                                                    />
                                                                    <input
                                                                        type="text"
                                                                        className="form-control form-control-sm"
                                                                        name="last_name"
                                                                        value={editForm.last_name}
                                                                        onChange={handleEditChange}
                                                                        placeholder="Last"
                                                                    />
                                                                </div>
                                                            ) : (
                                                                `${rider.first_name || ""} ${rider.last_name || ""}`.trim() || "-"
                                                            )}
                                                        </td>
                                                        <td>
                                                            {isEditing ? (
                                                                <input
                                                                    type="email"
                                                                    className="form-control form-control-sm"
                                                                    name="email"
                                                                    value={editForm.email}
                                                                    onChange={handleEditChange}
                                                                />
                                                            ) : (
                                                                rider.email
                                                            )}
                                                        </td>
                                                        <td>
                                                            {isEditing ? (
                                                                <input
                                                                    type="text"
                                                                    className="form-control form-control-sm"
                                                                    name="phone"
                                                                    value={editForm.phone}
                                                                    onChange={handleEditChange}
                                                                />
                                                            ) : (
                                                                rider.phone || "-"
                                                            )}
                                                        </td>
                                                        <td>
                                                            <span className={`badge ${rider.is_active ? "bg-success" : "bg-secondary"}`}>
                                                                {rider.is_active ? "Active" : "Inactive"}
                                                            </span>
                                                        </td>
                                                        <td>
                                                            {rider.date_joined ? new Date(rider.date_joined).toLocaleDateString() : "-"}
                                                        </td>
                                                        <td>
                                                            {isEditing ? (
                                                                <div className="d-flex gap-2">
                                                                    <button
                                                                        type="button"
                                                                        className="btn btn-success btn-sm"
                                                                        onClick={() => handleSaveEdit(rider.id)}
                                                                        disabled={updatingId === rider.id}
                                                                    >
                                                                        {updatingId === rider.id ? "Saving..." : "Save"}
                                                                    </button>
                                                                    <button
                                                                        type="button"
                                                                        className="btn btn-outline-secondary btn-sm"
                                                                        onClick={handleEditCancel}
                                                                        disabled={updatingId === rider.id}
                                                                    >
                                                                        Cancel
                                                                    </button>
                                                                </div>
                                                            ) : (
                                                                <div className="d-flex gap-2 flex-wrap">
                                                                    <button
                                                                        type="button"
                                                                        className="btn btn-outline-primary btn-sm"
                                                                        onClick={() => handleEditStart(rider)}
                                                                    >
                                                                        Edit
                                                                    </button>
                                                                    <button
                                                                        type="button"
                                                                        className={`btn btn-sm ${rider.is_active ? "btn-outline-warning" : "btn-outline-success"}`}
                                                                        onClick={() => handleToggleStatus(rider)}
                                                                        disabled={updatingId === rider.id}
                                                                    >
                                                                        {updatingId === rider.id ? "Updating..." : rider.is_active ? "Deactivate" : "Activate"}
                                                                    </button>
                                                                </div>
                                                            )}
                                                        </td>
                                                    </tr>
                                                );
                                            })
                                        ) : (
                                            <tr>
                                                <td colSpan="8" className="text-center py-4 text-muted">
                                                    No delivery riders found.
                                                </td>
                                            </tr>
                                        )}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
};

export default DeliveryRiders;
