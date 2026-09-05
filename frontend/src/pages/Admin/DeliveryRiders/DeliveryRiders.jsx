import { useEffect, useMemo, useState } from "react";
import { toast } from "react-toastify";
import { Link } from "react-router-dom";

import DashboardLayout from "../../../layouts/DashboardLayout";
import api from "../../../services/api";

const INITIAL_FORM_DATA = {
    username: "",
    email: "",
    password: "",
    first_name: "",
    last_name: "",
    phone: "",
};

const INITIAL_EDIT_FORM = {
    username: "",
    email: "",
    first_name: "",
    last_name: "",
    phone: "",
};

const DeliveryRiders = () => {
    const [riders, setRiders] = useState([]);

    const [loading, setLoading] = useState(true);

    const [search, setSearch] = useState("");

    const [submitting, setSubmitting] = useState(false);

    const [updatingId, setUpdatingId] = useState(null);

    const [editingId, setEditingId] = useState(null);

    const [editForm, setEditForm] = useState(
        INITIAL_EDIT_FORM
    );

    const [formData, setFormData] = useState(
        INITIAL_FORM_DATA
    );


    // ============================================================
    // LOAD RIDERS
    // ============================================================

    useEffect(() => {
        let ignore = false;

        const loadRiders = async () => {
            try {
                const response = await api.get(
                    "orders/admin/delivery-riders/"
                );

                if (ignore) {
                    return;
                }

                setRiders(
                    response.data?.results || []
                );
            } catch (error) {
                console.error(error);

                if (!ignore) {
                    toast.error(
                        error.response?.data?.detail ||
                        "Failed to load delivery riders."
                    );
                }
            } finally {
                if (!ignore) {
                    setLoading(false);
                }
            }
        };

        loadRiders();

        return () => {
            ignore = true;
        };
    }, []);


    // ============================================================
    // FILTER RIDERS
    // ============================================================

    const filteredRiders = useMemo(() => {
        const query = search
            .trim()
            .toLowerCase();

        if (!query) {
            return riders;
        }

        return riders.filter((rider) => {
            const fullName =
                `${rider.first_name || ""} ${
                    rider.last_name || ""
                }`.trim();

            return (
                rider.username
                    ?.toLowerCase()
                    .includes(query) ||
                rider.email
                    ?.toLowerCase()
                    .includes(query) ||
                fullName
                    .toLowerCase()
                    .includes(query) ||
                rider.phone
                    ?.toLowerCase()
                    .includes(query)
            );
        });
    }, [riders, search]);


    // ============================================================
    // CREATE RIDER - FORM CHANGE
    // ============================================================

    const handleChange = (event) => {
        const {
            name,
            value,
        } = event.target;

        setFormData((previous) => ({
            ...previous,
            [name]: value,
        }));
    };


    // ============================================================
    // CREATE RIDER
    // ============================================================

    const handleCreate = async (event) => {
        event.preventDefault();

        if (submitting) {
            return;
        }

        if (!formData.username.trim()) {
            toast.warning(
                "Username is required."
            );
            return;
        }

        if (!formData.email.trim()) {
            toast.warning(
                "Email is required."
            );
            return;
        }

        if (!formData.password.trim()) {
            toast.warning(
                "Password is required."
            );
            return;
        }

        try {
            setSubmitting(true);

            await api.post(
                "orders/admin/delivery-riders/create/",
                {
                    username:
                        formData.username.trim(),

                    email:
                        formData.email.trim(),

                    password:
                        formData.password,

                    first_name:
                        formData.first_name.trim(),

                    last_name:
                        formData.last_name.trim(),

                    phone:
                        formData.phone.trim(),
                }
            );

            toast.success(
                "Delivery rider created successfully."
            );

            setFormData({
                ...INITIAL_FORM_DATA,
            });

            // Reload riders after successful creation.
            const response = await api.get(
                "orders/admin/delivery-riders/"
            );

            setRiders(
                response.data?.results || []
            );
        } catch (error) {
            console.error(error);

            const detail =
                error.response?.data?.detail ||
                error.response?.data?.email?.[0] ||
                error.response?.data?.username?.[0] ||
                error.response?.data?.password?.[0] ||
                "Failed to create delivery rider.";

            toast.error(detail);
        } finally {
            setSubmitting(false);
        }
    };


    // ============================================================
    // START EDIT
    // ============================================================

    const handleEditStart = (rider) => {
        setEditingId(rider.id);

        setEditForm({
            username:
                rider.username || "",

            email:
                rider.email || "",

            first_name:
                rider.first_name || "",

            last_name:
                rider.last_name || "",

            phone:
                rider.phone || "",
        });
    };


    // ============================================================
    // CANCEL EDIT
    // ============================================================

    const handleEditCancel = () => {
        setEditingId(null);

        setEditForm({
            ...INITIAL_EDIT_FORM,
        });
    };


    // ============================================================
    // EDIT FORM CHANGE
    // ============================================================

    const handleEditChange = (event) => {
        const {
            name,
            value,
        } = event.target;

        setEditForm((previous) => ({
            ...previous,
            [name]: value,
        }));
    };


    // ============================================================
    // SAVE RIDER EDIT
    // ============================================================

    const handleSaveEdit = async (riderId) => {
        if (updatingId === riderId) {
            return;
        }

        try {
            setUpdatingId(riderId);

            await api.patch(
                `orders/admin/delivery-riders/${riderId}/update/`,
                {
                    username:
                        editForm.username.trim(),

                    email:
                        editForm.email.trim(),

                    first_name:
                        editForm.first_name.trim(),

                    last_name:
                        editForm.last_name.trim(),

                    phone:
                        editForm.phone.trim(),
                }
            );

            toast.success(
                "Rider details updated successfully."
            );

            handleEditCancel();

            const response = await api.get(
                "orders/admin/delivery-riders/"
            );

            setRiders(
                response.data?.results || []
            );
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


    // ============================================================
    // TOGGLE RIDER STATUS
    // ============================================================

    const handleToggleStatus = async (rider) => {
        if (updatingId === rider.id) {
            return;
        }

        const nextValue =
            !rider.is_active;

        try {
            setUpdatingId(rider.id);

            await api.post(
                `orders/admin/delivery-riders/${rider.id}/toggle-status/`,
                {
                    is_active: nextValue,
                }
            );

            toast.success(
                `Rider ${
                    nextValue
                        ? "activated"
                        : "deactivated"
                } successfully.`
            );

            const response = await api.get(
                "orders/admin/delivery-riders/"
            );

            setRiders(
                response.data?.results || []
            );
        } catch (error) {
            console.error(error);

            toast.error(
                error.response?.data?.detail ||
                "Failed to update rider status."
            );
        } finally {
            setUpdatingId(null);
        }
    };


    // ============================================================
    // RENDER
    // ============================================================

    return (
        <DashboardLayout>

            <div className="container-fluid py-4">

                {/* ==================================================
                    PAGE HEADER
                ================================================== */}

                <div className="d-flex justify-content-between align-items-center mb-4">

                    <div>

                        <h2 className="mb-1">
                            Delivery Rider Management
                        </h2>

                        <p className="text-muted mb-0">
                            Total riders:{" "}
                            <strong>
                                {filteredRiders.length}
                            </strong>
                        </p>

                    </div>

                </div>


                {/* ==================================================
                    CREATE RIDER
                ================================================== */}

                <div className="card shadow-sm border-0 mb-4">

                    <div className="card-header bg-dark text-white">

                        <h5 className="mb-0">
                            Create Delivery Rider
                        </h5>

                    </div>

                    <div className="card-body">

                        <form
                            onSubmit={
                                handleCreate
                            }
                        >

                            <div className="row g-3">

                                {/* Username */}

                                <div className="col-md-4">

                                    <label className="form-label">
                                        Username
                                    </label>

                                    <input
                                        type="text"
                                        className="form-control"
                                        name="username"
                                        value={
                                            formData.username
                                        }
                                        onChange={
                                            handleChange
                                        }
                                        autoComplete="username"
                                    />

                                </div>


                                {/* Email */}

                                <div className="col-md-4">

                                    <label className="form-label">
                                        Email
                                    </label>

                                    <input
                                        type="email"
                                        className="form-control"
                                        name="email"
                                        value={
                                            formData.email
                                        }
                                        onChange={
                                            handleChange
                                        }
                                        autoComplete="email"
                                    />

                                </div>


                                {/* Password */}

                                <div className="col-md-4">

                                    <label className="form-label">
                                        Password
                                    </label>

                                    <input
                                        type="password"
                                        className="form-control"
                                        name="password"
                                        value={
                                            formData.password
                                        }
                                        onChange={
                                            handleChange
                                        }
                                        autoComplete="new-password"
                                    />

                                </div>


                                {/* First Name */}

                                <div className="col-md-4">

                                    <label className="form-label">
                                        First Name
                                    </label>

                                    <input
                                        type="text"
                                        className="form-control"
                                        name="first_name"
                                        value={
                                            formData.first_name
                                        }
                                        onChange={
                                            handleChange
                                        }
                                        autoComplete="given-name"
                                    />

                                </div>


                                {/* Last Name */}

                                <div className="col-md-4">

                                    <label className="form-label">
                                        Last Name
                                    </label>

                                    <input
                                        type="text"
                                        className="form-control"
                                        name="last_name"
                                        value={
                                            formData.last_name
                                        }
                                        onChange={
                                            handleChange
                                        }
                                        autoComplete="family-name"
                                    />

                                </div>


                                {/* Phone */}

                                <div className="col-md-4">

                                    <label className="form-label">
                                        Phone
                                    </label>

                                    <input
                                        type="text"
                                        className="form-control"
                                        name="phone"
                                        value={
                                            formData.phone
                                        }
                                        onChange={
                                            handleChange
                                        }
                                        autoComplete="tel"
                                    />

                                </div>

                            </div>


                            <div className="mt-3">

                                <button
                                    type="submit"
                                    className="btn btn-primary"
                                    disabled={submitting}
                                >
                                    {submitting
                                        ? "Creating..."
                                        : "Create Rider"}
                                </button>

                            </div>

                        </form>

                    </div>

                </div>


                {/* ==================================================
                    RIDER LIST
                ================================================== */}

                <div className="card shadow-sm border-0">

                    <div className="card-header bg-light">

                        <div className="d-flex justify-content-between align-items-center gap-3">

                            <h5 className="mb-0">
                                Rider List
                            </h5>

                            <input
                                type="text"
                                className="form-control"
                                style={{
                                    maxWidth: "350px",
                                }}
                                placeholder="Search rider"
                                value={search}
                                onChange={(
                                    event
                                ) =>
                                    setSearch(
                                        event.target.value
                                    )
                                }
                            />

                        </div>

                    </div>


                    <div className="card-body p-0">

                        {loading ? (

                            <div className="text-center py-5">

                                <div
                                    className="spinner-border text-primary"
                                    role="status"
                                >
                                    <span className="visually-hidden">
                                        Loading...
                                    </span>
                                </div>

                                <p className="mt-3 text-muted">
                                    Loading riders...
                                </p>

                            </div>

                        ) : (

                            <div className="table-responsive">

                                <table className="table table-hover align-middle mb-0">

                                    <thead className="table-dark">

                                        <tr>

                                            <th>
                                                ID
                                            </th>

                                            <th>
                                                Username
                                            </th>

                                            <th>
                                                Name
                                            </th>

                                            <th>
                                                Email
                                            </th>

                                            <th>
                                                Phone
                                            </th>

                                            <th>
                                                Status
                                            </th>

                                            <th>
                                                Joined
                                            </th>

                                            <th>
                                                Actions
                                            </th>

                                        </tr>

                                    </thead>


                                    <tbody>

                                        {filteredRiders.length >
                                        0 ? (

                                            filteredRiders.map(
                                                (
                                                    rider
                                                ) => {

                                                    const isEditing =
                                                        editingId ===
                                                        rider.id;

                                                    const isUpdating =
                                                        updatingId ===
                                                        rider.id;

                                                    const fullName =
                                                        `${rider.first_name || ""} ${
                                                            rider.last_name || ""
                                                        }`.trim();

                                                    return (

                                                        <tr
                                                            key={
                                                                rider.id
                                                            }
                                                        >

                                                            {/* ID */}

                                                            <td>
                                                                {
                                                                    rider.id
                                                                }
                                                            </td>


                                                            {/* Username */}

                                                            <td>

                                                                {isEditing ? (

                                                                    <input
                                                                        type="text"
                                                                        className="form-control form-control-sm"
                                                                        name="username"
                                                                        value={
                                                                            editForm.username
                                                                        }
                                                                        onChange={
                                                                            handleEditChange
                                                                        }
                                                                    />

                                                                ) : (

                                                                    rider.username

                                                                )}

                                                            </td>


                                                            {/* Name */}

                                                            <td>

                                                                {isEditing ? (

                                                                    <div className="d-flex gap-2">

                                                                        <input
                                                                            type="text"
                                                                            className="form-control form-control-sm"
                                                                            name="first_name"
                                                                            value={
                                                                                editForm.first_name
                                                                            }
                                                                            onChange={
                                                                                handleEditChange
                                                                            }
                                                                            placeholder="First"
                                                                        />

                                                                        <input
                                                                            type="text"
                                                                            className="form-control form-control-sm"
                                                                            name="last_name"
                                                                            value={
                                                                                editForm.last_name
                                                                            }
                                                                            onChange={
                                                                                handleEditChange
                                                                            }
                                                                            placeholder="Last"
                                                                        />

                                                                    </div>

                                                                ) : (

                                                                    fullName ||
                                                                    "-"

                                                                )}

                                                            </td>


                                                            {/* Email */}

                                                            <td>

                                                                {isEditing ? (

                                                                    <input
                                                                        type="email"
                                                                        className="form-control form-control-sm"
                                                                        name="email"
                                                                        value={
                                                                            editForm.email
                                                                        }
                                                                        onChange={
                                                                            handleEditChange
                                                                        }
                                                                    />

                                                                ) : (

                                                                    rider.email ||
                                                                    "-"

                                                                )}

                                                            </td>


                                                            {/* Phone */}

                                                            <td>

                                                                {isEditing ? (

                                                                    <input
                                                                        type="text"
                                                                        className="form-control form-control-sm"
                                                                        name="phone"
                                                                        value={
                                                                            editForm.phone
                                                                        }
                                                                        onChange={
                                                                            handleEditChange
                                                                        }
                                                                    />

                                                                ) : (

                                                                    rider.phone ||
                                                                    "-"

                                                                )}

                                                            </td>


                                                            {/* Status */}

                                                            <td>

                                                                <span
                                                                    className={`badge ${
                                                                        rider.is_active
                                                                            ? "bg-success"
                                                                            : "bg-secondary"
                                                                    }`}
                                                                >
                                                                    {rider.is_active
                                                                        ? "Active"
                                                                        : "Inactive"}
                                                                </span>

                                                            </td>


                                                            {/* Joined */}

                                                            <td>

                                                                {rider.date_joined
                                                                    ? new Date(
                                                                          rider.date_joined
                                                                      ).toLocaleDateString()
                                                                    : "-"}

                                                            </td>


                                                            {/* Actions */}

                                                            <td>

                                                                {isEditing ? (

                                                                    <div className="d-flex gap-2">

                                                                        <button
                                                                            type="button"
                                                                            className="btn btn-success btn-sm"
                                                                            onClick={() =>
                                                                                handleSaveEdit(
                                                                                    rider.id
                                                                                )
                                                                            }
                                                                            disabled={
                                                                                isUpdating
                                                                            }
                                                                        >
                                                                            {isUpdating
                                                                                ? "Saving..."
                                                                                : "Save"}
                                                                        </button>


                                                                        <button
                                                                            type="button"
                                                                            className="btn btn-outline-secondary btn-sm"
                                                                            onClick={
                                                                                handleEditCancel
                                                                            }
                                                                            disabled={
                                                                                isUpdating
                                                                            }
                                                                        >
                                                                            Cancel
                                                                        </button>

                                                                    </div>

                                                                ) : (

                                                                    <div className="d-flex gap-2 flex-wrap">

                                                                        <Link
                                                                            to={`/admin/riders/${rider.id}/deliveries`}
                                                                            className="btn btn-outline-info btn-sm"
                                                                        >
                                                                            Deliveries
                                                                        </Link>

                                                                        <button
                                                                            type="button"
                                                                            className="btn btn-outline-primary btn-sm"
                                                                            onClick={() =>
                                                                                handleEditStart(
                                                                                    rider
                                                                                )
                                                                            }
                                                                            disabled={
                                                                                isUpdating
                                                                            }
                                                                        >
                                                                            Edit
                                                                        </button>


                                                                        <button
                                                                            type="button"
                                                                            className={`btn btn-sm ${
                                                                                rider.is_active
                                                                                    ? "btn-outline-warning"
                                                                                    : "btn-outline-success"
                                                                            }`}
                                                                            onClick={() =>
                                                                                handleToggleStatus(
                                                                                    rider
                                                                                )
                                                                            }
                                                                            disabled={
                                                                                isUpdating
                                                                            }
                                                                        >
                                                                            {isUpdating
                                                                                ? "Updating..."
                                                                                : rider.is_active
                                                                                ? "Deactivate"
                                                                                : "Activate"}
                                                                        </button>

                                                                    </div>

                                                                )}

                                                            </td>

                                                        </tr>

                                                    );
                                                }
                                            )

                                        ) : (

                                            <tr>

                                                <td
                                                    colSpan="8"
                                                    className="text-center py-5 text-muted"
                                                >
                                                    No delivery riders
                                                    found.
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