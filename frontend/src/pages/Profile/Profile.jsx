import { useEffect, useState } from "react";
import { toast } from "react-toastify";
import {
    getProfile,
    changePassword,
} from "../../services/authService";

const Profile = () => {
    // User Information
    const [user, setUser] = useState({
        username: "",
        email: "",
        phone: "",
        role: "",
    });

    // Enable/Disable Edit Mode
    const [editMode, setEditMode] = useState(false);

    // Password Data
    const [passwordData, setPasswordData] = useState({
        oldPassword: "",
        newPassword: "",
    });

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const response = await getProfile();

                if (response?.data) {
                    setUser((prev) => ({ ...prev, ...response.data }));
                } else {
                    console.warn("getProfile returned unexpected response:", response);
                }
            } catch (error) {
                console.log(error?.response || error?.message || error);
            }
        };

        fetchProfile();
    }, []);

    const handleUserChange = (e) => {
        setUser({
            ...user,
            [e.target.name]: e.target.value,
        });
    };

    const handlePasswordInputChange = (e) => {
        setPasswordData({
            ...passwordData,
            [e.target.name]: e.target.value,
        });
    };

    const handleUpdateProfile = () => {
       toast.success("Profile updated successfully!");
        setEditMode(false);
    };

    const handleChangePassword = async () => {
        try {
            await changePassword({
                old_password: passwordData.oldPassword,
                new_password: passwordData.newPassword,
            });

            alert("Password Changed Successfully!");
            setPasswordData({
                oldPassword: "",
                newPassword: "",
            });
        } catch (error) {
            console.log(error?.response || error?.message || error);
            toast.error("Failed to change password.");
        }
    };

    return (
        <div className="container py-5">

            <h1 className="text-center mb-5">
                My Profile
            </h1>

            <div className="row">

                {/* Customer Information */}
                <div className="col-lg-6 mb-4">

                    <div className="card shadow p-4">

                        <h3 className="mb-4">
                            Customer Information
                        </h3>

                        {/* Username */}
                        <div className="mb-3">
                            <label className="form-label">
                                Username
                            </label>

                            <input
                                type="text"
                                name="username"
                                className="form-control"
                                value={user.username}
                                disabled={!editMode}
                                onChange={handleUserChange}
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
                                value={user.email}
                                disabled={!editMode}
                                onChange={handleUserChange}
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
                                value={user.phone}
                                disabled={!editMode}
                                onChange={handleUserChange}
                            />
                        </div>

                        {/* Role */}
                        <div className="mb-4">
                            <label className="form-label">
                                Role
                            </label>

                            <input
                                type="text"
                                className="form-control"
                                value={user.role}
                                disabled
                            />
                        </div>

                        {/* Edit/Save Button */}
                        {!editMode ? (
                            <button
                                className="btn btn-primary"
                                onClick={() => setEditMode(true)}
                            >
                                Edit Profile
                            </button>
                        ) : (
                            <button
                                className="btn btn-success"
                                onClick={handleUpdateProfile}
                            >
                                Save Changes
                            </button>
                        )}

                    </div>

                </div>

                {/* Change Password */}
                <div className="col-lg-6">

                    <div className="card shadow p-4">

                        <h3 className="mb-4">
                            Change Password
                        </h3>

                        {/* Old Password */}
                        <div className="mb-3">
                            <label className="form-label">
                                Old Password
                            </label>

                            <input
                                type="password"
                                name="oldPassword"
                                className="form-control"
                                value={passwordData.oldPassword}
                                onChange={handlePasswordInputChange}
                            />
                        </div>

                        {/* New Password */}
                        <div className="mb-4">
                            <label className="form-label">
                                New Password
                            </label>

                            <input
                                type="password"
                                name="newPassword"
                                className="form-control"
                                value={passwordData.newPassword}
                                onChange={handlePasswordInputChange}
                            />
                        </div>

                        {/* Change Password Button */}
                        <button
                            className="btn btn-warning"
                            onClick={handleChangePassword}
                        >
                            Change Password
                        </button>

                    </div>

                </div>

            </div>

        </div>
    );
};

export default Profile;