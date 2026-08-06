import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";

import DashboardLayout from "../../../layouts/DashboardLayout";
import { createSupplier } from "../../../services/supplierService";

const AddSupplier = () => {
    const navigate = useNavigate();

    const [saving, setSaving] = useState(false);

    const [formData, setFormData] = useState({
        name: "",
        company: "",
        phone: "",
        email: "",
        address: "",
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
    email: formData.email.trim() || null,
};

await createSupplier(payload);

            toast.success("Supplier created successfully.");

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
        toast.error("Failed to create supplier.");
    }
}finally {
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

                                    {/* Supplier Name */}

                                    <div className="mb-3">
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

                                    {/* Company */}

                                    <div className="mb-3">
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

                                    {/* Phone */}

                                    <div className="mb-3">
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

                                    {/* Email */}

                                    <div className="mb-3">
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

                                    {/* Address */}

                                    <div className="mb-4">
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