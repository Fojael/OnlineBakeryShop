import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { toast } from "react-toastify";

import DashboardLayout from "../../../layouts/DashboardLayout";

import {
    getSupplier,
    updateSupplier,
} from "../../../services/supplierService";

const EditSupplier = () => {
    const { id } = useParams();
    const navigate = useNavigate();

    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

    const [formData, setFormData] = useState({
        name: "",
        company: "",
        phone: "",
        email: "",
        address: "",
        business_license: "",
        tax_number: "",
        website: "",
        notes: "",
    });

    useEffect(() => {
        const fetchSupplier = async () => {
            try {
                const response = await getSupplier(id);

                setFormData({
                    name: response.data.name || "",
                    company: response.data.company || "",
                    phone: response.data.phone || "",
                    email: response.data.email || "",
                    address: response.data.address || "",
                    business_license: response.data.business_license || "",
                    tax_number: response.data.tax_number || "",
                    website: response.data.website || "",
                    notes: response.data.notes || "",
                });
            } catch (error) {
                console.error(error);
                toast.error("Failed to load supplier.");
                navigate("/admin/suppliers");
            } finally {
                setLoading(false);
            }
        };

        fetchSupplier();
    }, [id, navigate]);

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
                name: formData.name.trim(),
                company: formData.company.trim(),
                phone: formData.phone.trim(),
                email: formData.email ? formData.email.trim() : "",
                address: formData.address.trim(),
                business_license: formData.business_license.trim(),
                tax_number: formData.tax_number.trim(),
                website: formData.website.trim(),
                notes: formData.notes.trim(),
            };

            await updateSupplier(id, payload);

            toast.success("Supplier updated successfully.");

            navigate("/admin/suppliers");
        } catch (error) {
            console.error(error);

            if (error.response?.data?.email) {
                toast.error(error.response.data.email[0]);
            } else if (error.response?.data?.phone) {
                toast.error(error.response.data.phone[0]);
            } else if (error.response?.data?.name) {
                toast.error(error.response.data.name[0]);
            } else {
                toast.error("Failed to update supplier.");
            }
        } finally {
            setSaving(false);
        }
    };

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
                        Loading Supplier...
                    </h5>
                </div>
            </DashboardLayout>
        );
    }

    return (
        <DashboardLayout>
            <div className="container py-4">
                <div className="row justify-content-center">
                    <div className="col-lg-8">

                        <div className="card shadow">

                            <div className="card-header bg-warning">
                                <h3 className="mb-0">
                                    Edit Supplier
                                </h3>
                            </div>

                            <div className="card-body">

                                <form onSubmit={handleSubmit}>

                                    <div className="row">
                                        <div className="col-md-6 mb-3">
                                            <label className="form-label">
                                                Supplier Name *
                                            </label>

                                            <input
                                                type="text"
                                                className="form-control"
                                                name="name"
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
                                                className="form-control"
                                                name="company"
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
                                                className="form-control"
                                                name="phone"
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
                                                className="form-control"
                                                name="email"
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
                                            rows="3"
                                            className="form-control"
                                            name="address"
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
                                                className="form-control"
                                                name="business_license"
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
                                                className="form-control"
                                                name="tax_number"
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
                                            className="form-control"
                                            name="website"
                                            value={formData.website}
                                            onChange={handleChange}
                                        />
                                    </div>

                                    <div className="mb-4">
                                        <label className="form-label">
                                            Notes
                                        </label>

                                        <textarea
                                            rows="3"
                                            className="form-control"
                                            name="notes"
                                            value={formData.notes}
                                            onChange={handleChange}
                                        />
                                    </div>

                                    {/* Buttons */}

                                    <button
                                        type="submit"
                                        className="btn btn-warning"
                                        disabled={saving}
                                    >
                                        {saving ? (
                                            <>
                                                <span
                                                    className="spinner-border spinner-border-sm me-2"
                                                    role="status"
                                                ></span>
                                                Updating...
                                            </>
                                        ) : (
                                            "Update Supplier"
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

export default EditSupplier;