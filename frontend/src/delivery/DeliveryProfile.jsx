import React, { useEffect, useState } from "react";

import { Link } from "react-router-dom";

import deliveryService from "../services/deliveryService";

import "./delivery.css";

// ==========================================================
// DELIVERY PROFILE
// ==========================================================

const DeliveryProfile = () => {

    const [profile, setProfile] = useState(null);

    const [loading, setLoading] = useState(true);

    const [saving, setSaving] = useState(false);

    const [error, setError] = useState("");

    const [success, setSuccess] = useState("");

    const [formData, setFormData] = useState({
        first_name: "",
        last_name: "",
        phone: "",
        address: "",
    });

    // ======================================================
    // LOAD PROFILE
    // ======================================================

    const loadProfile = async () => {

        try {

            setLoading(true);
            setError("");

            const data = await deliveryService.getProfile();

            setProfile(data);

            setFormData({
                first_name: data.first_name || "",
                last_name: data.last_name || "",
                phone: data.phone || "",
                address: data.address || "",
            });

        } catch (err) {

            console.error("Profile error:", err);

            setError(
                err.response?.data?.detail || "Failed to load profile."
            );

        } finally {

            setLoading(false);
        }
    };

    useEffect(() => {

        loadProfile();

    }, []);

    // ======================================================
    // INPUT CHANGE
    // ======================================================

    const handleChange = (event) => {

        setFormData({
            ...formData,
            [event.target.name]: event.target.value,
        });
    };

    // ======================================================
    // SAVE PROFILE
    // ======================================================

    const handleSubmit = async (event) => {

        event.preventDefault();

        try {

            setSaving(true);
            setError("");
            setSuccess("");

            const data = await deliveryService.updateProfile(formData);

            setProfile(data);

            setSuccess("Profile updated successfully.");

        } catch (err) {

            console.error("Profile update error:", err);

            setError(
                err.response?.data?.detail || "Failed to update profile."
            );

        } finally {

            setSaving(false);
        }
    };

    // ======================================================
    // LOADING
    // ======================================================

    if (loading) {

        return (
            <div className="delivery-page">

                <div className="delivery-loading">
                    Loading profile...
                </div>

            </div>
        );
    }

    // ======================================================
    // PAGE
    // ======================================================

    return (
        <div className="delivery-page">

            <div className="delivery-header">

                <div>

                    <h1>
                        DELIVERY PROFILE
                    </h1>

                    <p>
                        Manage your delivery rider profile.
                    </p>

                </div>

                <Link
                    to="/delivery/dashboard"
                    className="delivery-header-btn"
                >
                    Dashboard
                </Link>

            </div>

            {error && (

                <div className="delivery-error">
                    {error}
                </div>

            )}

            {success && (

                <div className="delivery-success">
                    {success}
                </div>

            )}

            <div className="delivery-profile-card">

                {/* ======================================== */}
                {/* PROFILE HEADER */}
                {/* ======================================== */}

                <div className="profile-avatar">
                    {(profile?.first_name || profile?.username || "D")
                        .charAt(0)
                        .toUpperCase()}
                </div>

                <h2>
                    {profile?.first_name || profile?.username || "Delivery Rider"}
                </h2>

                <p className="profile-role">
                    Delivery Rider
                </p>

                {/* ======================================== */}
                {/* FORM */}
                {/* ======================================== */}

                <form
                    onSubmit={handleSubmit}
                    className="delivery-profile-form"
                >

                    <div className="form-row">

                        <div className="form-group">

                            <label>
                                First Name
                            </label>

                            <input
                                type="text"
                                name="first_name"
                                value={formData.first_name}
                                onChange={handleChange}
                            />

                        </div>

                        <div className="form-group">

                            <label>
                                Last Name
                            </label>

                            <input
                                type="text"
                                name="last_name"
                                value={formData.last_name}
                                onChange={handleChange}
                            />

                        </div>

                    </div>

                    <div className="form-group">

                        <label>
                            Phone
                        </label>

                        <input
                            type="text"
                            name="phone"
                            value={formData.phone}
                            onChange={handleChange}
                        />

                    </div>

                    <div className="form-group">

                        <label>
                            Address
                        </label>

                        <textarea
                            name="address"
                            rows="4"
                            value={formData.address}
                            onChange={handleChange}
                        />

                    </div>

                    <div className="profile-readonly">

                        <div>

                            <strong>
                                Username
                            </strong>

                            <span>
                                {profile?.username || "N/A"}
                            </span>

                        </div>

                        <div>

                            <strong>
                                Email
                            </strong>

                            <span>
                                {profile?.email || "N/A"}
                            </span>

                        </div>

                    </div>

                    <button
                        type="submit"
                        className="delivery-status-btn"
                        disabled={saving}
                    >
                        {saving ? "Saving..." : "Save Changes"}
                    </button>

                </form>

            </div>

        </div>
    );
};

export default DeliveryProfile;
