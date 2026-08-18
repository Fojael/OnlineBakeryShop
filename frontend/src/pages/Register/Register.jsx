import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
    FaEnvelope,
    FaEye,
    FaEyeSlash,
    FaLock,
    FaPhone,
    FaUser,
} from "react-icons/fa";
import { toast } from "react-toastify";

import { register } from "../../services/authService";

const Register = () => {
    const navigate = useNavigate();

    // ==========================================
    // State
    // ==========================================

    const [formData, setFormData] = useState({
        username: "",
        email: "",
        phone: "",
        password: "",
        confirmPassword: "",
    });

    const [loading, setLoading] =
        useState(false);

    const [showPassword, setShowPassword] =
        useState(false);

    const [
        showConfirmPassword,
        setShowConfirmPassword,
    ] = useState(false);

    // ==========================================
    // Password Strength
    // ==========================================

    const getPasswordStrength = (
        password
    ) => {
        if (password.length === 0)
            return "";

        if (password.length < 6)
            return {
                text: "Weak",
                className: "text-danger",
            };

        if (password.length < 10)
            return {
                text: "Medium",
                className: "text-warning",
            };

        return {
            text: "Strong",
            className: "text-success",
        };
    };

    const strength =
        getPasswordStrength(
            formData.password
        );

    // ==========================================
    // Handle Input
    // ==========================================

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]:
                e.target.value,
        });
    };

    // ==========================================
    // Register
    // ==========================================

    const handleSubmit = async (
        e
    ) => {
        e.preventDefault();

        if (
            formData.password !==
            formData.confirmPassword
        ) {
            toast.error(
                "Passwords do not match."
            );
            return;
        }

        try {
            setLoading(true);

            await register({
                username:
                    formData.username,
                email: formData.email,
                phone: formData.phone,
                password:
                    formData.password,
            });

            toast.success(
                "Registration successful!"
            );

            setFormData({
                username: "",
                email: "",
                phone: "",
                password: "",
                confirmPassword: "",
            });

            setTimeout(() => {
                navigate("/login");
            }, 1500);
        } catch (error) {
            console.error(error);

            if (
                error.response?.data
            ) {
                const errors =
                    error.response.data;

                Object.keys(errors).forEach(
                    (key) => {
                        const message =
                            Array.isArray(
                                errors[key]
                            )
                                ? errors[
                                      key
                                  ][0]
                                : errors[
                                      key
                                  ];

                        toast.error(
                            `${key}: ${message}`
                        );
                    }
                );
            } else {
                toast.error(
                    "Registration failed."
                );
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container py-5">

            <div className="row justify-content-center">

                <div className="col-lg-6 col-md-8">

                    <div className="card border-0 shadow-lg rounded-4">

                        <div className="card-body p-5">

                            <h2 className="fw-bold text-center mb-2">
                                Create Account
                            </h2>

                            <p className="text-center text-muted mb-4">
                                Register to start
                                shopping
                            </p>

                            <form
                                onSubmit={
                                    handleSubmit
                                }
                            >

                                {/* Username */}

                                <div className="mb-3">

                                    <label className="form-label">
                                        Username
                                    </label>

                                    <div className="input-group">

                                        <span className="input-group-text">
                                            <FaUser />
                                        </span>

                                        <input
                                            type="text"
                                            name="username"
                                            className="form-control"
                                            placeholder="Enter username"
                                            value={
                                                formData.username
                                            }
                                            onChange={
                                                handleChange
                                            }
                                            required
                                        />

                                    </div>

                                </div>

                                {/* Email */}

                                <div className="mb-3">

                                    <label className="form-label">
                                        Email
                                    </label>

                                    <div className="input-group">

                                        <span className="input-group-text">
                                            <FaEnvelope />
                                        </span>

                                        <input
                                            type="email"
                                            name="email"
                                            className="form-control"
                                            placeholder="Enter email"
                                            value={
                                                formData.email
                                            }
                                            onChange={
                                                handleChange
                                            }
                                            required
                                        />

                                    </div>

                                </div>

                                {/* Phone */}

                                <div className="mb-3">

                                    <label className="form-label">
                                        Phone
                                    </label>

                                    <div className="input-group">

                                        <span className="input-group-text">
                                            <FaPhone />
                                        </span>

                                        <input
                                            type="text"
                                            name="phone"
                                            className="form-control"
                                            placeholder="Enter phone number"
                                            value={
                                                formData.phone
                                            }
                                            onChange={
                                                handleChange
                                            }
                                            required
                                        />

                                    </div>

                                </div>

                                {/* Password */}

                                <div className="mb-3">

                                    <label className="form-label">
                                        Password
                                    </label>

                                    <div className="input-group">

                                        <span className="input-group-text">
                                            <FaLock />
                                        </span>

                                        <input
                                            type={
                                                showPassword
                                                    ? "text"
                                                    : "password"
                                            }
                                            name="password"
                                            className="form-control"
                                            placeholder="Enter password"
                                            value={
                                                formData.password
                                            }
                                            onChange={
                                                handleChange
                                            }
                                            required
                                        />

                                        <button
                                            type="button"
                                            className="btn btn-outline-secondary"
                                            onClick={() =>
                                                setShowPassword(
                                                    !showPassword
                                                )
                                            }
                                        >
                                            {showPassword ? (
                                                <FaEyeSlash />
                                            ) : (
                                                <FaEye />
                                            )}
                                        </button>

                                    </div>

                                    {strength && (
                                        <small
                                            className={
                                                strength.className
                                            }
                                        >
                                            Password
                                            Strength:{" "}
                                            {
                                                strength.text
                                            }
                                        </small>
                                    )}

                                </div>

                                {/* Confirm Password */}

                                <div className="mb-4">

                                    <label className="form-label">
                                        Confirm
                                        Password
                                    </label>

                                    <div className="input-group">

                                        <span className="input-group-text">
                                            <FaLock />
                                        </span>

                                        <input
                                            type={
                                                showConfirmPassword
                                                    ? "text"
                                                    : "password"
                                            }
                                            name="confirmPassword"
                                            className="form-control"
                                            placeholder="Confirm password"
                                            value={
                                                formData.confirmPassword
                                            }
                                            onChange={
                                                handleChange
                                            }
                                            required
                                        />

                                        <button
                                            type="button"
                                            className="btn btn-outline-secondary"
                                            onClick={() =>
                                                setShowConfirmPassword(
                                                    !showConfirmPassword
                                                )
                                            }
                                        >
                                            {showConfirmPassword ? (
                                                <FaEyeSlash />
                                            ) : (
                                                <FaEye />
                                            )}
                                        </button>

                                    </div>

                                    {formData.confirmPassword &&
                                        (formData.password ===
                                        formData.confirmPassword ? (
                                            <small className="text-success">
                                                ✓
                                                Passwords
                                                match
                                            </small>
                                        ) : (
                                            <small className="text-danger">
                                                ✗
                                                Passwords
                                                do not
                                                match
                                            </small>
                                        ))}

                                </div>

                                {/* Register Button */}

                                <button
                                    type="submit"
                                    className="btn btn-success w-100"
                                    disabled={
                                        loading
                                    }
                                >
                                    {loading ? (
                                        <>
                                            <span
                                                className="spinner-border spinner-border-sm me-2"
                                                role="status"
                                            />
                                            Registering...
                                        </>
                                    ) : (
                                        "Register"
                                    )}
                                </button>

                            </form>

                            <hr className="my-4" />

                            <div className="text-center">

                                Already have an
                                account?

                                <Link
                                    to="/login"
                                    className="ms-2 text-decoration-none fw-semibold"
                                >
                                    Login
                                </Link>

                            </div>

                        </div>

                    </div>

                </div>

            </div>

        </div>
    );
};

export default Register;