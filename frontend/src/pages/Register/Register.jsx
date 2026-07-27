import { useState } from "react";
import { register } from "../../services/authService";

const Register = () => {
    const [formData, setFormData] = useState({
        username: "",
        email: "",
        phone: "",
        password: "",
        confirmPassword: "",
    });

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = async (e) => {
    e.preventDefault();

    if (formData.password !== formData.confirmPassword) {
        alert("Passwords do not match!");
        return;
    }

    try {
        const response = await register({
            username: formData.username,
            email: formData.email,
            phone: formData.phone,
            password: formData.password,
        });

        console.log(response.data);

        alert("Registration Successful!");

        setFormData({
            username: "",
            email: "",
            phone: "",
            password: "",
            confirmPassword: "",
        });

    } catch (error) {

        console.log(error.response);

        alert("Registration Failed!");

    }
};

    return (
        <div className="container py-5">
            <div className="row justify-content-center">

                <div className="col-md-6">

                    <div className="card shadow p-4">

                        <h2 className="text-center mb-4">
                            Customer Registration
                        </h2>

                        <form onSubmit={handleSubmit}>

                            {/* Username */}
                            <div className="mb-3">
                                <label className="form-label">
                                    Username
                                </label>

                                <input
                                    type="text"
                                    name="username"
                                    className="form-control"
                                    placeholder="Enter your username"
                                    value={formData.username}
                                    onChange={handleChange}
                                    required
                                />
                            </div>

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
                                    value={formData.email}
                                    onChange={handleChange}
                                    required
                                />
                            </div>

                            {/* Phone */}
                            <div className="mb-3">
                                <label className="form-label">
                                    Phone Number
                                </label>

                                <input
                                    type="text"
                                    name="phone"
                                    className="form-control"
                                    placeholder="Enter your phone number"
                                    value={formData.phone}
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
                                    value={formData.password}
                                    onChange={handleChange}
                                    required
                                />
                            </div>

                            {/* Confirm Password */}
                            <div className="mb-4">
                                <label className="form-label">
                                    Confirm Password
                                </label>

                                <input
                                    type="password"
                                    name="confirmPassword"
                                    className="form-control"
                                    placeholder="Confirm your password"
                                    value={formData.confirmPassword}
                                    onChange={handleChange}
                                    required
                                />
                            </div>

                            {/* Register Button */}
                            <button
                                type="submit"
                                className="btn btn-success w-100"
                            >
                                Register
                            </button>

                        </form>

                    </div>

                </div>

            </div>
        </div>
    );
};

export default Register;