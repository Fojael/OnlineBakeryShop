import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { toast } from "react-toastify";

import { addAddress } from "../../services/addressService";

const AddAddress = () => {
    const navigate = useNavigate();

    // ==========================================
    // FORM STATE
    // ==========================================

    const [formData, setFormData] = useState({
        full_name: "",
        phone: "",
        division: "",
        district: "",
        upazila: "",
        address_line: "",
        postal_code: "",
        is_default: false,
    });

    const [loading, setLoading] = useState(false);

    const [errors, setErrors] = useState({});

    // ==========================================
    // INPUT CHANGE
    // ==========================================

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;

        setFormData((prev) => ({
            ...prev,
            [name]:
                type === "checkbox"
                    ? checked
                    : value,
        }));

        setErrors((prev) => ({
            ...prev,
            [name]: "",
        }));
    };

    // ==========================================
    // VALIDATION
    // ==========================================

    const validate = () => {
        const newErrors = {};

        if (!formData.full_name.trim()) {
            newErrors.full_name =
                "Full name is required.";
        }

        if (!formData.phone.trim()) {
            newErrors.phone =
                "Phone number is required.";
        } else if (
            !/^01[3-9]\d{8}$/.test(formData.phone)
        ) {
            newErrors.phone =
                "Enter a valid Bangladeshi phone number.";
        }

        if (!formData.division.trim()) {
            newErrors.division =
                "Division is required.";
        }

        if (!formData.district.trim()) {
            newErrors.district =
                "District is required.";
        }

        if (!formData.upazila.trim()) {
            newErrors.upazila =
                "Upazila is required.";
        }

        if (!formData.address_line.trim()) {
            newErrors.address_line =
                "Address is required.";
        }

        if (!formData.postal_code.trim()) {
            newErrors.postal_code =
                "Postal code is required.";
        }

        setErrors(newErrors);

        return Object.keys(newErrors).length === 0;
    };

    // ==========================================
    // SUBMIT
    // ==========================================

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!validate()) {
            return;
        }

        try {
            setLoading(true);

            await addAddress(formData);

            toast.success(
                "Address added successfully."
            );

            navigate("/address");
        } catch (error) {
            console.error(error);

            toast.error(
                error?.response?.data?.detail ||
                    "Unable to create address."
            );
        } finally {
            setLoading(false);
        }
    };

    // ==========================================
    // PAGE
    // ==========================================

    return (
        <div className="container py-5">

            <div className="row justify-content-center">

                <div className="col-lg-8">

                    <div className="card shadow-sm border-0">

                        <div className="card-header bg-primary text-white">
                            <h3 className="mb-0">
                                ➕ Add New Address
                            </h3>
                        </div>

                        <div className="card-body">

                            <form onSubmit={handleSubmit}>

                                {/* Full Name */}

                                <div className="mb-3">
                                    <label className="form-label">
                                        Full Name
                                    </label>

                                    <input
                                        type="text"
                                        name="full_name"
                                        className={`form-control ${
                                            errors.full_name
                                                ? "is-invalid"
                                                : ""
                                        }`}
                                        value={
                                            formData.full_name
                                        }
                                        onChange={
                                            handleChange
                                        }
                                    />

                                    <div className="invalid-feedback">
                                        {
                                            errors.full_name
                                        }
                                    </div>
                                </div>

                                {/* Phone */}

                                <div className="mb-3">
                                    <label className="form-label">
                                        Phone Number
                                    </label>

                                    <input
                                        type="text"
                                        name="phone"
                                        className={`form-control ${
                                            errors.phone
                                                ? "is-invalid"
                                                : ""
                                        }`}
                                        value={
                                            formData.phone
                                        }
                                        onChange={
                                            handleChange
                                        }
                                    />

                                    <div className="invalid-feedback">
                                        {errors.phone}
                                    </div>
                                </div>

                                {/* Division */}

                                <div className="mb-3">
                                    <label className="form-label">
                                        Division
                                    </label>

                                    <input
                                        type="text"
                                        name="division"
                                        className={`form-control ${
                                            errors.division
                                                ? "is-invalid"
                                                : ""
                                        }`}
                                        value={
                                            formData.division
                                        }
                                        onChange={
                                            handleChange
                                        }
                                    />

                                    <div className="invalid-feedback">
                                        {
                                            errors.division
                                        }
                                    </div>
                                </div>

                                {/* District */}

                                <div className="mb-3">
                                    <label className="form-label">
                                        District
                                    </label>

                                    <input
                                        type="text"
                                        name="district"
                                        className={`form-control ${
                                            errors.district
                                                ? "is-invalid"
                                                : ""
                                        }`}
                                        value={
                                            formData.district
                                        }
                                        onChange={
                                            handleChange
                                        }
                                    />

                                    <div className="invalid-feedback">
                                        {
                                            errors.district
                                        }
                                    </div>
                                </div>

                                {/* Upazila */}

                                <div className="mb-3">
                                    <label className="form-label">
                                        Upazila
                                    </label>

                                    <input
                                        type="text"
                                        name="upazila"
                                        className={`form-control ${
                                            errors.upazila
                                                ? "is-invalid"
                                                : ""
                                        }`}
                                        value={
                                            formData.upazila
                                        }
                                        onChange={
                                            handleChange
                                        }
                                    />

                                    <div className="invalid-feedback">
                                        {
                                            errors.upazila
                                        }
                                    </div>
                                </div>

                                {/* Address */}

                                <div className="mb-3">
                                    <label className="form-label">
                                        Address
                                    </label>

                                    <textarea
                                        rows="3"
                                        name="address_line"
                                        className={`form-control ${
                                            errors.address_line
                                                ? "is-invalid"
                                                : ""
                                        }`}
                                        value={
                                            formData.address_line
                                        }
                                        onChange={
                                            handleChange
                                        }
                                    />

                                    <div className="invalid-feedback">
                                        {
                                            errors.address_line
                                        }
                                    </div>
                                </div>

                                {/* Postal Code */}

                                <div className="mb-3">
                                    <label className="form-label">
                                        Postal Code
                                    </label>

                                    <input
                                        type="text"
                                        name="postal_code"
                                        className={`form-control ${
                                            errors.postal_code
                                                ? "is-invalid"
                                                : ""
                                        }`}
                                        value={
                                            formData.postal_code
                                        }
                                        onChange={
                                            handleChange
                                        }
                                    />

                                    <div className="invalid-feedback">
                                        {
                                            errors.postal_code
                                        }
                                    </div>
                                </div>

                                {/* Default */}

                                <div className="form-check mb-4">
                                    <input
                                        className="form-check-input"
                                        type="checkbox"
                                        name="is_default"
                                        checked={
                                            formData.is_default
                                        }
                                        onChange={
                                            handleChange
                                        }
                                    />

                                    <label className="form-check-label">
                                        Set as default
                                        address
                                    </label>
                                </div>

                                {/* Buttons */}

                                <div className="d-flex gap-3">

                                    <button
                                        type="submit"
                                        className="btn btn-primary"
                                        disabled={loading}
                                    >
                                        {loading
                                            ? "Saving..."
                                            : "Save Address"}
                                    </button>

                                    <Link
                                        to="/address"
                                        className="btn btn-secondary"
                                    >
                                        Cancel
                                    </Link>

                                </div>

                            </form>

                        </div>

                    </div>

                </div>

            </div>

        </div>
    );
};

export default AddAddress;