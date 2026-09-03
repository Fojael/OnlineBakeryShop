import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";

import DashboardLayout from "../../../layouts/DashboardLayout";
import { createSupplier } from "../../../services/supplierService";

const AddSupplier = () => {
    const navigate = useNavigate();

    const [saving, setSaving] = useState(false);

    const [formData, setFormData] = useState({
        username: "",
        password: "",
        name: "",
        company: "",
        email: "",
        phone: "",
        address: "",
        business_license: "",
        tax_number: "",
        website: "",
        notes: "",
    });

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const validateEmail = (email) => {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        // Validation
        if (!formData.username.trim()) {
            toast.warning("Username is required.");
            return;
        }

        if (!formData.password.trim()) {
            toast.warning("Password is required.");
            return;
        }

        if (formData.password.length < 8) {
            toast.warning("Password must be at least 8 characters long.");
            return;
        }

        if (!formData.name.trim()) {
            toast.warning("Supplier Name is required.");
            return;
        }

        if (!formData.phone.trim()) {
            toast.warning("Phone is required.");
            return;
        }

        if (
            formData.email &&
            !validateEmail(formData.email)
        ) {
            toast.warning("Enter a valid email address.");
            return;
        }

        try {
            setSaving(true);

            const payload = {
                ...formData,
                username: formData.username.trim(),
                password: formData.password,
                name: formData.name.trim(),
                company: formData.company.trim(),
                email: formData.email ? formData.email.trim() : "",
                phone: formData.phone.trim(),
                address: formData.address.trim(),
                business_license: formData.business_license.trim(),
                tax_number: formData.tax_number.trim(),
                website: formData.website.trim(),
                notes: formData.notes.trim(),
            };

            await createSupplier(payload);

            toast.success("Supplier created successfully.");

            navigate("/admin/suppliers");
        } catch (error) {
            console.error(error);

            if (error.response?.data?.username) {
                toast.error(error.response.data.username[0]);
            } else if (error.response?.data?.email) {
                toast.error(error.response.data.email[0]);
            } else if (error.response?.data?.phone) {
                toast.error(error.response.data.phone[0]);
            } else if (error.response?.data?.password) {
                toast.error(error.response.data.password[0]);
            } else if (error.response?.data?.detail) {
                toast.error(error.response.data.detail);
            } else {
                toast.error("Failed to create supplier.");
            }
        } finally {
            setSaving(false);
        }
    };

    return (
        <DashboardLayout>
            <div className="container py-4">

                <div className="row justify-content-center">

                    <div className="col-lg-8">

                        <div className="card shadow">

                            <div className="card-header bg-primary text-white">
                                <h3 className="mb-0">
                                    Add Supplier
                                </h3>
                            </div>

                            <div className="card-body">

                                <form onSubmit={handleSubmit}>

                                    <div className="row">
                                        <div className="col-md-6 mb-3">
                                            <label className="form-label">
                                                Username *
                                            </label>

                                            <input
                                                type="text"
                                                name="username"
                                                className="form-control"
                                                value={formData.username}
                                                onChange={handleChange}
                                            />
                                        </div>

                                        <div className="col-md-6 mb-3">
                                            <label className="form-label">
                                                Password *
                                            </label>

                                            <input
                                                type="password"
                                                name="password"
                                                className="form-control"
                                                value={formData.password}
                                                onChange={handleChange}
                                            />
                                        </div>
                                    </div>

                                    <div className="row">
                                        <div className="col-md-6 mb-3">
                                            <label className="form-label">
                                                Supplier Name *
                                            </label>

                                            <input
                                                type="text"
                                                name="name"
                                                className="form-control"
                                                value={formData.name}
                                                onChange={handleChange}
                                            />
                                        </div>

                                        <div className="col-md-6 mb-3">
                                            <label className="form-label">
                                                Company
                                            </label>

                                            <input
                                                type="text"
                                                name="company"
                                                className="form-control"
                                                value={formData.company}
                                                onChange={handleChange}
                                            />
                                        </div>
                                    </div>

                                    <div className="row">
                                        <div className="col-md-6 mb-3">
                                            <label className="form-label">
                                                Phone *
                                            </label>

                                            <input
                                                type="text"
                                                name="phone"
                                                className="form-control"
                                                value={formData.phone}
                                                onChange={handleChange}
                                            />
                                        </div>

                                        <div className="col-md-6 mb-3">
                                            <label className="form-label">
                                                Email
                                            </label>

                                            <input
                                                type="email"
                                                name="email"
                                                className="form-control"
                                                value={formData.email}
                                                onChange={handleChange}
                                            />
                                        </div>
                                    </div>

                                    <div className="mb-3">
                                        <label className="form-label">
                                            Address
                                        </label>

                                        <textarea
                                            name="address"
                                            rows="3"
                                            className="form-control"
                                            value={formData.address}
                                            onChange={handleChange}
                                        />
                                    </div>

                                    <div className="row">
                                        <div className="col-md-6 mb-3">
                                            <label className="form-label">
                                                Business License
                                            </label>

                                            <input
                                                type="text"
                                                name="business_license"
                                                className="form-control"
                                                value={formData.business_license}
                                                onChange={handleChange}
                                            />
                                        </div>

                                        <div className="col-md-6 mb-3">
                                            <label className="form-label">
                                                Tax Number
                                            </label>

                                            <input
                                                type="text"
                                                name="tax_number"
                                                className="form-control"
                                                value={formData.tax_number}
                                                onChange={handleChange}
                                            />
                                        </div>
                                    </div>

                                    <div className="mb-3">
                                        <label className="form-label">
                                            Website
                                        </label>

                                        <input
                                            type="url"
                                            name="website"
                                            className="form-control"
                                            value={formData.website}
                                            onChange={handleChange}
                                        />
                                    </div>

                                    <div className="mb-4">
                                        <label className="form-label">
                                            Notes
                                        </label>

                                        <textarea
                                            name="notes"
                                            rows="3"
                                            className="form-control"
                                            value={formData.notes}
                                            onChange={handleChange}
                                        />
                                    </div>

                                    {/* Buttons */}

                                    <button
                                        type="submit"
                                        className="btn btn-primary"
                                        disabled={saving}
                                    >
                                        {saving ? (
                                            <>
                                                <span
                                                    className="spinner-border spinner-border-sm me-2"
                                                    role="status"
                                                ></span>
                                                Saving...
                                            </>
                                        ) : (
                                            "Save"
                                        )}
                                    </button>

                                    <button
                                        type="button"
                                        className="btn btn-secondary ms-2"
                                        onClick={() =>
                                            navigate("/admin/suppliers")
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
        </DashboardLayout>
    );
};

export default AddSupplier;

