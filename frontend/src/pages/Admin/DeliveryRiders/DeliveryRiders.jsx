import { useCallback, useEffect, useMemo, useState } from "react";
import { toast } from "react-toastify";

import DashboardLayout from "../../../layouts/DashboardLayout";
import api from "../../../services/api";

const DeliveryRiders = () => {
    const [riders, setRiders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState("");
    const [submitting, setSubmitting] = useState(false);
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
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {filteredRiders.length > 0 ? (
                                            filteredRiders.map((rider) => (
                                                <tr key={rider.id}>
                                                    <td>{rider.id}</td>
                                                    <td>{rider.username}</td>
                                                    <td>{`${rider.first_name || ""} ${rider.last_name || ""}`.trim() || "-"}</td>
                                                    <td>{rider.email}</td>
                                                    <td>{rider.phone || "-"}</td>
                                                    <td>
                                                        <span className={`badge ${rider.is_active ? "bg-success" : "bg-secondary"}`}>
                                                            {rider.is_active ? "Active" : "Inactive"}
                                                        </span>
                                                    </td>
                                                    <td>
                                                        {rider.date_joined ? new Date(rider.date_joined).toLocaleDateString() : "-"}
                                                    </td>
                                                </tr>
                                            ))
                                        ) : (
                                            <tr>
                                                <td colSpan="7" className="text-center py-4 text-muted">
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
