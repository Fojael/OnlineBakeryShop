import { useState } from "react";

const Profile = () => {
    const [user, setUser] = useState({
        username: "customer1",
        email: "customer1@gmail.com",
        phone: "01700000000",
        role: "CUSTOMER",
    });

    const [editMode, setEditMode] = useState(false);

    const [passwordData, setPasswordData] = useState({
        oldPassword: "",
        newPassword: "",
    });

    // Handle Profile Changes
    const handleUserChange = (e) => {
        setUser({
            ...user,
            [e.target.name]: e.target.value,
        });
    };

    // Handle Password Changes
    const handlePasswordChange = (e) => {
        setPasswordData({
            ...passwordData,
            [e.target.name]: e.target.value,
        });
    };

    // Update Profile
    const handleUpdateProfile = () => {
        alert("Profile Updated Successfully!");
        setEditMode(false);
    };

    // Change Password
    const handleChangePassword = () => {
        alert("Password Changed Successfully!");

        setPasswordData({
            oldPassword: "",
            newPassword: "",
        });
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

                        {!editMode ? (
                            <button
                                className="btn btn-primary"
                                onClick={() =>
                                    setEditMode(true)
                                }
                            >
                                Edit Profile
                            </button>
                        ) : (
                            <button
                                className="btn btn-success"
                                onClick={
                                    handleUpdateProfile
                                }
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

                        <div className="mb-3">
                            <label className="form-label">
                                Old Password
                            </label>

                            <input
                                type="password"
                                name="oldPassword"
                                className="form-control"
                                value={
                                    passwordData.oldPassword
                                }
                                onChange={
                                    handlePasswordChange
                                }
                            />
                        </div>

                        <div className="mb-4">
                            <label className="form-label">
                                New Password
                            </label>

                            <input
                                type="password"
                                name="newPassword"
                                className="form-control"
                                value={
                                    passwordData.newPassword
                                }
                                onChange={
                                    handlePasswordChange
                                }
                            />
                        </div>

                        <button
                            className="btn btn-warning"
                            onClick={
                                handleChangePassword
                            }
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