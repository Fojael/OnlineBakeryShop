import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "../../services/authService";
import { toast } from "react-toastify";

const Login = () => {
    const navigate = useNavigate();

    const [loginData, setLoginData] = useState({
        email: "",
        password: "",
    });

    // Handle input changes
    const handleChange = (e) => {
        setLoginData({
            ...loginData,
            [e.target.name]: e.target.value,
        });
    };

    // Handle login
    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            const response = await login(loginData);

            // Save JWT tokens
            localStorage.setItem(
                "access",
                response.data.access
            );

            localStorage.setItem(
                "refresh",
                response.data.refresh
            );

            // Save user role
            localStorage.setItem(
                "role",
                response.data.user.role
            );

            // Optional: save user information
            localStorage.setItem(
                "username",
                response.data.user.username
            );

            localStorage.setItem(
                "email",
                response.data.user.email
            );

            const role = response.data.user.role;

            toast.success("Login successful!");

            // Role-based redirection
            if (role === "ADMIN") {
                navigate("/admin/dashboard");
            } else if (role === "CUSTOMER") {
                navigate("/");
            } else if (role === "SUPPLIER") {
                navigate("/");
            } else if (role === "DELIVERY_RIDER") {
                navigate("/");
            } else {
                navigate("/");
            }

        } catch (error) {
            console.log(error.response);

            toast.error("Invalid email or password.");
        }
    };

    return (
        <div className="container py-5">
            <div className="row justify-content-center">

                <div className="col-md-6">

                    <div className="card shadow p-4">

                        <h2 className="text-center mb-4">
                            Login
                        </h2>

                        <form onSubmit={handleSubmit}>

                            {/* Email */}
                            <div className="mb-3">
                                <label className="form-label">
                                    Email Address
                                </label>

                                <input
                                    type="email"
                                    name="email"
                                    className="form-control"
                                    placeholder="Enter your email"
                                    value={loginData.email}
                                    onChange={handleChange}
                                    required
                                />
                            </div>

                            {/* Password */}
                            <div className="mb-3">
                                <label className="form-label">
                                    Password
                                </label>

                                <input
                                    type="password"
                                    name="password"
                                    className="form-control"
                                    placeholder="Enter your password"
                                    value={loginData.password}
                                    onChange={handleChange}
                                    required
                                />
                            </div>

                            {/* Remember Me */}
                            <div className="form-check mb-3">
                                <input
                                    type="checkbox"
                                    className="form-check-input"
                                    id="rememberMe"
                                />

                                <label
                                    className="form-check-label"
                                    htmlFor="rememberMe"
                                >
                                    Remember Me
                                </label>
                            </div>

                            {/* Login Button */}
                            <button
                                type="submit"
                                className="btn btn-primary w-100"
                            >
                                Login
                            </button>

                        </form>

                    </div>

                </div>

            </div>
        </div>
    );
};

export default Login;