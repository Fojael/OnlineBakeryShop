import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
    FaEnvelope,
    FaEye,
    FaEyeSlash,
    FaLock,
} from "react-icons/fa";
import { toast } from "react-toastify";

import { login } from "../../services/authService";

const Login = () => {
    const navigate = useNavigate();

    const [loginData, setLoginData] = useState({
        email: "",
        password: "",
    });

    const [showPassword, setShowPassword] =
        useState(false);

    const [rememberMe, setRememberMe] =
        useState(false);

    const [loading, setLoading] =
        useState(false);
    // ==========================================
    // HANDLE INPUT CHANGE
    // ==========================================

    const handleChange = (e) => {
        setLoginData((previousData) => ({
            ...previousData,
            [e.target.name]: e.target.value,
        }));
    };

    // ==========================================
    // HANDLE LOGIN
    // ==========================================

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!loginData.email.trim()) {
            toast.error("Please enter your email.");
            return;
        }

        if (!loginData.password) {
            toast.error("Please enter your password.");
            return;
        }

        try {
            setLoading(true);

            const response = await login({
                email: loginData.email.trim(),
                password: loginData.password,
            });

            console.log("Login response:", response.data);

            const {
                access,
                refresh,
                user,
            } = response.data;

            // ==========================================
            // VALIDATE LOGIN RESPONSE
            // ==========================================

            if (!access || !refresh) {
                toast.error(
                    "Login failed. Authentication tokens were not received."
                );
                return;
            }

            if (!user) {
                toast.error(
                    "Login failed. User information was not received."
                );
                return;
            }

            // ==========================================
            // CLEAR OLD AUTH DATA
            // ==========================================

            localStorage.removeItem("access");
            localStorage.removeItem("refresh");
            localStorage.removeItem("user");
            localStorage.removeItem("role");
            localStorage.removeItem("username");
            localStorage.removeItem("email");

            sessionStorage.removeItem("access");
            sessionStorage.removeItem("refresh");
            sessionStorage.removeItem("user");

            // ==========================================
            // SAVE AUTH DATA
            //
            // Your api.js and ProtectedRoute currently
            // read from localStorage.
            //
            // Therefore JWT must be stored there.
            // ==========================================

            localStorage.setItem(
                "access",
                access
            );

            localStorage.setItem(
                "refresh",
                refresh
            );

            localStorage.setItem(
                "user",
                JSON.stringify(user)
            );

            // ==========================================
            // SAVE ROLE SEPARATELY
            // ==========================================

            if (user.role) {
                localStorage.setItem(
                    "role",
                    user.role
                );
            }

            if (user.username) {
                localStorage.setItem(
                    "username",
                    user.username
                );
            }

            if (user.email) {
                localStorage.setItem(
                    "email",
                    user.email
                );
            }

            // ==========================================
            // REMEMBER ME
            //
            // Currently the application authentication
            // system uses localStorage.
            //
            // Keep the value for future enhancement,
            // but do not move tokens to sessionStorage
            // because api.js does not read them there.
            // ==========================================

            localStorage.setItem(
                "rememberMe",
                rememberMe ? "true" : "false"
            );

            // ==========================================
            // SUCCESS MESSAGE
            // ==========================================

            toast.success(
                `Welcome, ${
                    user.username ||
                    user.email ||
                    "User"
                }!`
            );

            // ==========================================
            // ROLE-BASED REDIRECTION
            // ==========================================

            const userRole =
                String(user.role || "")
                    .trim()
                    .toUpperCase();

            console.log(
                "Logged-in user role:",
                userRole
            );

            // ==========================================
            // ADMIN
            // ==========================================

            if (userRole === "ADMIN") {
                navigate(
                    "/admin/dashboard",
                    { replace: true }
                );
                return;
            }

            // ==========================================
            // CUSTOMER
            // ==========================================

            if (userRole === "CUSTOMER") {
                navigate(
                    "/",
                    { replace: true }
                );
                return;
            }

            // ==========================================
            // SUPPLIER
            // ==========================================

            if (userRole === "SUPPLIER") {
                navigate(
                    "/",
                    { replace: true }
                );
                return;
            }

            // ==========================================
            // DELIVERY RIDER
            // ==========================================

            if (
                userRole === "DELIVERY_RIDER" ||
                userRole === "DELIVERY RIDER"
            ) {
                navigate(
                    "/",
                    { replace: true }
                );
                return;
            }

            // ==========================================
            // IF ROLE IS UNKNOWN
            // ==========================================

            console.warn(
                "Unknown user role:",
                user.role
            );

            navigate(
                "/",
                { replace: true }
            );

        } catch (error) {
            console.error(
                "Login failed:",
                error
            );

            const responseData =
                error?.response?.data;

            const message =
                responseData?.detail ||
                responseData?.message ||
                responseData?.error ||
                "Invalid email or password.";

            toast.error(message);

        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container py-5">

            <div className="row justify-content-center">

                <div className="col-lg-5 col-md-7">

                    <div className="card border-0 shadow-lg rounded-4">

                        <div className="card-body p-5">

                            {/* =================================
                                HEADER
                            ================================= */}

                            <h2 className="fw-bold text-center mb-2">
                                Welcome Back
                            </h2>

                            <p className="text-center text-muted mb-4">
                                Sign in to your account
                            </p>

                            {/* =================================
                                LOGIN FORM
                            ================================= */}

                            <form onSubmit={handleSubmit}>

                                {/* EMAIL */}

                                <div className="mb-3">

                                    <label
                                        htmlFor="login-email"
                                        className="form-label"
                                    >
                                        Email Address
                                    </label>

                                    <div className="input-group">

                                        <span className="input-group-text">
                                            <FaEnvelope />
                                        </span>

                                        <input
                                            id="login-email"
                                            type="email"
                                            name="email"
                                            className="form-control"
                                            placeholder="Enter your email"
                                            value={
                                                loginData.email
                                            }
                                            onChange={
                                                handleChange
                                            }
                                            autoComplete="email"
                                            required
                                        />

                                    </div>

                                </div>

                                {/* PASSWORD */}

                                <div className="mb-3">

                                    <label
                                        htmlFor="login-password"
                                        className="form-label"
                                    >
                                        Password
                                    </label>

                                    <div className="input-group">

                                        <span className="input-group-text">
                                            <FaLock />
                                        </span>

                                        <input
                                            id="login-password"
                                            type={
                                                showPassword
                                                    ? "text"
                                                    : "password"
                                            }
                                            name="password"
                                            className="form-control"
                                            placeholder="Enter your password"
                                            value={
                                                loginData.password
                                            }
                                            onChange={
                                                handleChange
                                            }
                                            autoComplete="current-password"
                                            required
                                        />

                                        <button
                                            type="button"
                                            className="btn btn-outline-secondary"
                                            onClick={() =>
                                                setShowPassword(
                                                    (previous) =>
                                                        !previous
                                                )
                                            }
                                            aria-label={
                                                showPassword
                                                    ? "Hide password"
                                                    : "Show password"
                                            }
                                        >
                                            {showPassword ? (
                                                <FaEyeSlash />
                                            ) : (
                                                <FaEye />
                                            )}
                                        </button>

                                    </div>

                                </div>

                                {/* REMEMBER ME */}

                                <div className="d-flex justify-content-between align-items-center mb-4">

                                    <div className="form-check">

                                        <input
                                            className="form-check-input"
                                            type="checkbox"
                                            id="rememberMe"
                                            checked={
                                                rememberMe
                                            }
                                            onChange={(e) =>
                                                setRememberMe(
                                                    e.target.checked
                                                )
                                            }
                                        />

                                        <label
                                            className="form-check-label"
                                            htmlFor="rememberMe"
                                        >
                                            Remember Me
                                        </label>

                                    </div>

                                    <Link
                                        to="/forgot-password"
                                        className="text-decoration-none"
                                    >
                                        Forgot Password?
                                    </Link>

                                </div>

                                {/* LOGIN BUTTON */}

                                <button
                                    type="submit"
                                    className="btn btn-primary w-100"
                                    disabled={loading}
                                >
                                    {loading ? (
                                        <>
                                            <span
                                                className="spinner-border spinner-border-sm me-2"
                                                role="status"
                                                aria-hidden="true"
                                            />

                                            Signing In...
                                        </>
                                    ) : (
                                        "Login"
                                    )}
                                </button>

                            </form>

                            <hr className="my-4" />

                            {/* REGISTER */}

                            <div className="text-center">

                                Don't have an account?

                                <Link
                                    to="/register"
                                    className="ms-2 text-decoration-none fw-semibold"
                                >
                                    Register
                                </Link>

                            </div>

                        </div>

                    </div>

                </div>

            </div>

        </div>
    );
};

export default Login;