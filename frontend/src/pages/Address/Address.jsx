import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { toast } from "react-toastify";

import {
    getAddresses,
    deleteAddress,
} from "../../services/addressService";

const Address = () => {
    // ==========================================================
    // STATE
    // ==========================================================

    const [addresses, setAddresses] = useState([]);

    const [loading, setLoading] = useState(true);

    const [deletingId, setDeletingId] = useState(null);

    const [error, setError] = useState("");

    // ==========================================================
    // LOAD ADDRESSES
    // ==========================================================

    useEffect(() => {
        let mounted = true;

        const loadAddresses = async () => {
            try {
                setLoading(true);
                setError("");

                const response = await getAddresses();

                const addressList = Array.isArray(
                    response.data
                )
                    ? response.data
                    : [];

                if (mounted) {
                    setAddresses(addressList);
                }
            } catch (err) {
                console.error(
                    "Address Loading Error:",
                    err
                );

                if (mounted) {
                    setAddresses([]);

                    setError(
                        "Unable to load your addresses."
                    );
                }

                toast.error(
                    err?.response?.data?.detail ||
                        "Unable to load addresses."
                );
            } finally {
                if (mounted) {
                    setLoading(false);
                }
            }
        };

        loadAddresses();

        return () => {
            mounted = false;
        };
    }, []);

    // ==========================================================
    // DELETE ADDRESS
    // ==========================================================

    const handleDelete = async (id) => {
        const confirmed = window.confirm(
            "Are you sure you want to delete this address?"
        );

        if (!confirmed) {
            return;
        }

        try {
            setDeletingId(id);

            await deleteAddress(id);

            setAddresses((previousAddresses) =>
                previousAddresses.filter(
                    (address) => address.id !== id
                )
            );

            toast.success(
                "Address deleted successfully."
            );
        } catch (err) {
            console.error(
                "Delete Address Error:",
                err
            );

            toast.error(
                err?.response?.data?.detail ||
                    "Unable to delete address."
            );
        } finally {
            setDeletingId(null);
        }
    };

    // ==========================================================
    // LOADING
    // ==========================================================

    if (loading) {
        return (
            <div className="container py-5">

                <div className="text-center">

                    <div
                        className="spinner-border text-primary"
                        role="status"
                    >
                        <span className="visually-hidden">
                            Loading...
                        </span>
                    </div>

                    <h5 className="mt-3">
                        Loading your addresses...
                    </h5>

                    <p className="text-muted">
                        Please wait.
                    </p>

                </div>

            </div>
        );
    }

    // ==========================================================
    // PAGE
    // ==========================================================

    return (
        <div className="container py-5">

            {/* ==================================================
                HEADER
            ================================================== */}

            <div className="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3 mb-4">

                <div>

                    <h2 className="fw-bold mb-1">
                        📍 Address Book
                    </h2>

                    <p className="text-muted mb-0">
                        Manage your delivery addresses.
                    </p>

                </div>

                <div className="d-flex gap-2">

                    <Link
                        to="/customer/dashboard"
                        className="btn btn-outline-secondary"
                    >
                        ← Dashboard
                    </Link>

                    <Link
                        to="/address/add"
                        className="btn btn-primary"
                    >
                        + Add Address
                    </Link>

                </div>

            </div>

            {/* ==================================================
                ERROR
            ================================================== */}

            {error && (
                <div
                    className="alert alert-danger d-flex justify-content-between align-items-center"
                    role="alert"
                >
                    <span>
                        {error}
                    </span>

                    <button
                        type="button"
                        className="btn-close"
                        aria-label="Close"
                        onClick={() => setError("")}
                    />
                </div>
            )}

            {/* ==================================================
                ADDRESS COUNT
            ================================================== */}

            {addresses.length > 0 && (
                <div className="alert alert-light border mb-4">

                    <strong>
                        {addresses.length}
                    </strong>{" "}

                    {addresses.length === 1
                        ? "saved address"
                        : "saved addresses"}

                </div>
            )}

            {/* ==================================================
                EMPTY STATE
            ================================================== */}

            {addresses.length === 0 ? (

                <div className="card border-0 shadow-sm">

                    <div className="card-body text-center py-5">

                        <div
                            className="display-1 mb-3"
                            aria-hidden="true"
                        >
                            📍
                        </div>

                        <h3 className="fw-bold">
                            No Addresses Found
                        </h3>

                        <p className="text-muted mb-4">
                            You haven't added a delivery
                            address yet.
                        </p>

                        <Link
                            to="/address/add"
                            className="btn btn-primary px-4"
                        >
                            + Add Your First Address
                        </Link>

                    </div>

                </div>

            ) : (

                /* ==================================================
                    ADDRESS LIST
                ================================================== */

                <div className="row g-4">

                    {addresses.map((address) => (

                        <div
                            className="col-12 col-lg-6"
                            key={address.id}
                        >

                            <div className="card border-0 shadow-sm h-100">

                                {/* ==================================================
                                    CARD HEADER
                                ================================================== */}

                                <div className="card-header bg-white border-0 pt-4 px-4">

                                    <div className="d-flex justify-content-between align-items-start gap-3">

                                        <div>

                                            <h5 className="fw-bold mb-1">
                                                {address.full_name}
                                            </h5>

                                            {address.is_default && (
                                                <span className="badge bg-success">
                                                    ✓ Default Address
                                                </span>
                                            )}

                                        </div>

                                        <span className="text-muted">
                                            #{address.id}
                                        </span>

                                    </div>

                                </div>

                                {/* ==================================================
                                    CARD BODY
                                ================================================== */}

                                <div className="card-body px-4">

                                    <div className="mb-3">

                                        <div className="d-flex align-items-start mb-2">

                                            <span
                                                className="me-2"
                                                aria-hidden="true"
                                            >
                                                📞
                                            </span>

                                            <div>
                                                <small className="text-muted d-block">
                                                    Phone
                                                </small>

                                                <span>
                                                    {address.phone}
                                                </span>
                                            </div>

                                        </div>

                                        <div className="d-flex align-items-start">

                                            <span
                                                className="me-2"
                                                aria-hidden="true"
                                            >
                                                📍
                                            </span>

                                            <div>

                                                <small className="text-muted d-block">
                                                    Delivery Address
                                                </small>

                                                <span>
                                                    {address.address_line}
                                                </span>

                                            </div>

                                        </div>

                                    </div>

                                    <hr />

                                    {/* ==================================================
                                        LOCATION
                                    ================================================== */}

                                    <div className="mb-3">

                                        <small className="text-muted d-block mb-1">
                                            Location
                                        </small>

                                        <div>

                                            {address.upazila},{" "}
                                            {address.district},{" "}
                                            {address.division}

                                        </div>

                                        <div className="mt-1">

                                            <span className="text-muted">
                                                Postal Code:
                                            </span>{" "}

                                            <strong>
                                                {address.postal_code}
                                            </strong>

                                        </div>

                                    </div>

                                </div>

                                {/* ==================================================
                                    CARD FOOTER
                                ================================================== */}

                                <div className="card-footer bg-white border-0 px-4 pb-4">

                                    <div className="d-flex flex-wrap gap-2">

                                        <Link
                                            to={`/address/edit/${address.id}`}
                                            className="btn btn-warning btn-sm"
                                        >
                                            ✏️ Edit
                                        </Link>

                                        <button
                                            type="button"
                                            className="btn btn-outline-danger btn-sm"
                                            disabled={
                                                deletingId ===
                                                address.id
                                            }
                                            onClick={() =>
                                                handleDelete(
                                                    address.id
                                                )
                                            }
                                        >
                                            {deletingId ===
                                            address.id
                                                ? (
                                                    <>
                                                        <span
                                                            className="spinner-border spinner-border-sm me-1"
                                                            role="status"
                                                            aria-hidden="true"
                                                        />
                                                        Deleting...
                                                    </>
                                                )
                                                : (
                                                    <>
                                                        🗑️ Delete
                                                    </>
                                                )}
                                        </button>

                                    </div>

                                </div>

                            </div>

                        </div>

                    ))}

                </div>

            )}

        </div>
    );
};

export default Address;