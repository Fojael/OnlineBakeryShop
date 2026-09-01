import { useEffect, useState } from "react";
import { toast } from "react-toastify";

import {
    getSupplierProfile,
    updateSupplierProfile,
} from "../../../services/supplierService";

const SupplierProfile = () => {
    const [profile, setProfile] = useState(null);
    const [error, setError] = useState("");
    const [saving, setSaving] = useState(false);
    const [formData, setFormData] = useState({
        name: "",
        company: "",
        phone: "",
        address: "",
        website: "",
        business_license: "",
        tax_number: "",
    });

    useEffect(() => {
        let active = true;

        const fetchProfile = async () => {
            try {
                const response = await getSupplierProfile();

                if (!active) return;

                const data = response?.supplier || response;

                setProfile(data);
                setError("");
                setFormData({
                    name: data?.name || "",
                    company: data?.company || "",
                    phone: data?.phone || "",
                    address: data?.address || "",
                    website: data?.website || "",
                    business_license: data?.business_license || "",
                    tax_number: data?.tax_number || "",
                });
            } catch (caughtError) {
                if (!active) return;

                console.error("Failed to load supplier profile:", caughtError);
                setError("Failed to load supplier profile.");
                toast.error("Failed to load supplier profile.");
            }
        };

        void fetchProfile();

        return () => {
            active = false;
        };
    }, []);

    const handleChange = (event) => {
        const { name, value } = event.target;
        setFormData((prev) => ({
            ...prev,
            [name]: value,
        }));
    };

    const handleSubmit = async (event) => {
        event.preventDefault();

        if (!formData.name.trim()) {
            toast.warning("Supplier name is required.");
            return;
        }

        if (!formData.phone.trim()) {
            toast.warning("Phone is required.");
            return;
        }

        try {
            setSaving(true);
            const response = await updateSupplierProfile({
                name: formData.name.trim(),
                company: formData.company.trim(),
                phone: formData.phone.trim(),
                address: formData.address.trim(),
                website: formData.website.trim(),
                business_license: formData.business_license.trim(),
                tax_number: formData.tax_number.trim(),
            });

            const data = response?.supplier || response;
            setProfile(data);
            toast.success("Profile updated successfully.");
        } catch (error) {
            console.error("Failed to update supplier profile:", error);
            const serverMessage =
                error.response?.data?.detail ||
                error.response?.data?.message ||
                "Failed to update profile.";
            toast.error(serverMessage);
        } finally {
            setSaving(false);
        }
    };

    if (!profile && !error) {
        return (
            <div className="container py-4">
                <div className="text-center py-5">
                    <div className="spinner-border" role="status" />
                    <p className="mt-3 mb-0">Loading profile...</p>
                </div>
            </div>
        );
    }

    if (error && !profile) {
        return (
            <div className="container py-4">
                <div className="alert alert-danger" role="alert">
                    {error}
                </div>
            </div>
        );
    }

    return (
        <div className="container py-4">
            <div className="mb-4">
                <h2 className="fw-bold mb-1">My Profile</h2>
                <p className="text-muted mb-0">Manage your supplier account details.</p>
            </div>

            <div className="row">
                <div className="col-lg-4 mb-4">
                    <div className="card h-100 shadow-sm border-0">
                        <div className="card-body">
                            <h5 className="fw-bold mb-3">Profile Summary</h5>

                            <div className="mb-3">
                                <small className="text-muted d-block">Username</small>
                                <strong>{profile?.username || "-"}</strong>
                            </div>

                            <div className="mb-3">
                                <small className="text-muted d-block">Email</small>
                                <strong>{profile?.email || "-"}</strong>
                            </div>

                            <div className="mb-3">
                                <small className="text-muted d-block">Account Status</small>
                                <span className={`badge ${profile?.is_active ? "bg-success" : "bg-secondary"}`}>
                                    {profile?.is_active ? "Active" : "Inactive"}
                                </span>
                            </div>

                            <div className="mb-3">
                                <small className="text-muted d-block">Approval Status</small>
                                <span className={`badge ${profile?.is_approved ? "bg-success" : "bg-warning text-dark"}`}>
                                    {profile?.is_approved ? "Approved" : "Pending"}
                                </span>
                            </div>

                            <div>
                                <small className="text-muted d-block">Created Date</small>
                                <strong>
                                    {profile?.created_at
                                        ? new Date(profile.created_at).toLocaleDateString()
                                        : "-"}
                                </strong>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="col-lg-8">
                    <div className="card shadow-sm border-0">
                        <div className="card-body">
                            <h5 className="fw-bold mb-3">Edit Profile</h5>

                            <form onSubmit={handleSubmit}>
                                <div className="row">
                                    <div className="col-md-6 mb-3">
                                        <label className="form-label">Name</label>
                                        <input
                                            type="text"
                                            name="name"
                                            className="form-control"
                                            value={formData.name}
                                            onChange={handleChange}
                                        />
                                    </div>

                                    <div className="col-md-6 mb-3">
                                        <label className="form-label">Company</label>
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
                                        <label className="form-label">Phone</label>
                                        <input
                                            type="text"
                                            name="phone"
                                            className="form-control"
                                            value={formData.phone}
                                            onChange={handleChange}
                                        />
                                    </div>

                                    <div className="col-md-6 mb-3">
                                        <label className="form-label">Website</label>
                                        <input
                                            type="url"
                                            name="website"
                                            className="form-control"
                                            value={formData.website}
                                            onChange={handleChange}
                                        />
                                    </div>
                                </div>

                                <div className="mb-3">
                                    <label className="form-label">Address</label>
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
                                        <label className="form-label">Business License</label>
                                        <input
                                            type="text"
                                            name="business_license"
                                            className="form-control"
                                            value={formData.business_license}
                                            onChange={handleChange}
                                        />
                                    </div>

                                    <div className="col-md-6 mb-3">
                                        <label className="form-label">Tax Number</label>
                                        <input
                                            type="text"
                                            name="tax_number"
                                            className="form-control"
                                            value={formData.tax_number}
                                            onChange={handleChange}
                                        />
                                    </div>
                                </div>

                                <div className="border rounded p-3 bg-light mb-3">
                                    <p className="mb-2"><strong>Read-only fields</strong></p>
                                    <ul className="mb-0 text-muted small">
                                        <li>Username</li>
                                        <li>Email</li>
                                        <li>Role</li>
                                        <li>Approval Status</li>
                                    </ul>
                                </div>

                                <button type="submit" className="btn btn-primary" disabled={saving}>
                                    {saving ? "Saving..." : "Save Changes"}
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SupplierProfile;