import { useEffect, useMemo, useState } from "react";
import { toast } from "react-toastify";

import {
    getProfile,
    updateProfile,
    changePassword,
} from "../../services/authService";

const Profile = () => {
    // ==========================================================
    // STATE
    // ==========================================================

    const [loading, setLoading] = useState(true);

    const [user, setUser] = useState({
        username: "",
        email: "",
        phone: "",
        role: "",
        profile_image: "",
    });

    const [editMode, setEditMode] = useState(false);

    const [avatarFile, setAvatarFile] = useState(null);

    const [showOldPassword, setShowOldPassword] =
        useState(false);

    const [showNewPassword, setShowNewPassword] =
        useState(false);

    const [showConfirmPassword, setShowConfirmPassword] =
        useState(false);

    const [passwordData, setPasswordData] = useState({
        oldPassword: "",
        newPassword: "",
        confirmPassword: "",
    });

    // ==========================================================
    // LOAD PROFILE
    // ==========================================================

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const response = await getProfile();

                setUser((prev) => ({
                    ...prev,
                    ...response.data,
                }));
            } catch (error) {
                console.log(error);

                toast.error("Failed to load profile.");
            } finally {
                setLoading(false);
            }
        };

        void fetchProfile();
    }, []);

    // ==========================================================
    // HANDLE PROFILE INPUTS
    // ==========================================================

    const handleUserChange = (e) => {
        setUser({
            ...user,
            [e.target.name]: e.target.value,
        });
    };

    // ==========================================================
    // HANDLE PASSWORD INPUTS
    // ==========================================================

    const handlePasswordChange = (e) => {
        setPasswordData({
            ...passwordData,
            [e.target.name]: e.target.value,
        });
    };

    // ==========================================================
    // AVATAR PREVIEW
    // ==========================================================

    const handleAvatar = (e) => {
        const file = e.target.files[0];

        if (!file) return;

        setAvatarFile(file);

        setUser({
            ...user,
            profile_image: URL.createObjectURL(file),
        });
    };

    // ==========================================================
    // PASSWORD STRENGTH
    // ==========================================================

    const passwordStrength = useMemo(() => {
        const password = passwordData.newPassword;

        let score = 0;

        if (password.length >= 8) score++;
        if (/[A-Z]/.test(password)) score++;
        if (/[0-9]/.test(password)) score++;
        if (/[^A-Za-z0-9]/.test(password)) score++;

        return score;
    }, [passwordData.newPassword]);

    const strengthText = [
        "Very Weak",
        "Weak",
        "Medium",
        "Strong",
        "Very Strong",
    ][passwordStrength];

    const strengthColor = [
        "danger",
        "warning",
        "info",
        "primary",
        "success",
    ][passwordStrength];

    // ==========================================================
    // UPDATE PROFILE
    // ==========================================================

    const handleSaveProfile = async () => {
        try {
            const formData = new FormData();

            formData.append("username", user.username);
            formData.append("email", user.email);
            formData.append("phone", user.phone);

            if (avatarFile) {
                formData.append(
                    "profile_image",
                    avatarFile
                );
            }

            const response = await updateProfile(formData);

            setUser((prev) => ({
                ...prev,
                ...response.data,
            }));

            toast.success(
                "Profile updated successfully."
            );

            setEditMode(false);
        } catch (error) {
            console.log(error);

            toast.error(
                error.response?.data?.detail ||
                error.response?.data?.error ||
                "Failed to update profile."
            );
        }
    };

    // ==========================================================
    // CHANGE PASSWORD
    // ==========================================================

    const handleChangePassword = async () => {
        if (
            passwordData.newPassword !==
            passwordData.confirmPassword
        ) {
            toast.error("Passwords do not match.");

            return;
        }

        try {
            await changePassword({
                old_password: passwordData.oldPassword,
                new_password: passwordData.newPassword,
            });

            toast.success(
                "Password changed successfully."
            );

            setPasswordData({
                oldPassword: "",
                newPassword: "",
                confirmPassword: "",
            });
        } catch (error) {
            console.log(error);

            toast.error(
                error.response?.data?.detail ||
                error.response?.data?.error ||
                "Failed to change password."
            );
        }
    };

    // ==========================================================
    // LOADING
    // ==========================================================

    if (loading) {
        return (
            <div className="container py-5 text-center">
                <div
                    className="spinner-border text-primary"
                    role="status"
                >
                    <span className="visually-hidden">
                        Loading...
                    </span>
                </div>

                <h5 className="mt-3">
                    Loading Profile...
                </h5>
            </div>
        );
    }
        return (
        <div className="container py-5">

            <div className="row">

                {/* ======================================================
                    PROFILE INFORMATION
                ======================================================= */}

                <div className="col-lg-7 mb-4">

                    <div className="card shadow border-0">

                        <div className="card-body">

                            <div className="text-center mb-4">

                                <img
                                    src={
                                        user.profile_image ||
                                        "https://ui-avatars.com/api/?name=" +
                                            encodeURIComponent(
                                                user.username || "User"
                                            ) +
                                            "&background=0D6EFD&color=fff&size=200"
                                    }
                                    alt="Profile"
                                    className="rounded-circle border shadow"
                                    width="130"
                                    height="130"
                                    style={{
                                        objectFit: "cover",
                                    }}
                                />

                                {editMode && (
                                    <div className="mt-3">

                                        <input
                                            type="file"
                                            className="form-control"
                                            accept="image/*"
                                            onChange={handleAvatar}
                                        />

                                    </div>
                                )}

                                <h3 className="mt-3 fw-bold">
                                    {user.username}
                                </h3>

                                <span className="badge bg-primary px-3 py-2">
                                    {user.role}
                                </span>

                            </div>

                            {/* Username */}

                            <div className="mb-3">

                                <label className="form-label fw-semibold">
                                    Username
                                </label>

                                <input
                                    type="text"
                                    className="form-control"
                                    name="username"
                                    value={user.username}
                                    disabled={!editMode}
                                    onChange={handleUserChange}
                                />

                            </div>

                            {/* Email */}

                            <div className="mb-3">

                                <label className="form-label fw-semibold">
                                    Email Address
                                </label>

                                <input
                                    type="email"
                                    className="form-control"
                                    name="email"
                                    value={user.email}
                                    disabled={!editMode}
                                    onChange={handleUserChange}
                                />

                            </div>

                            {/* Phone */}

                            <div className="mb-4">

                                <label className="form-label fw-semibold">
                                    Phone Number
                                </label>

                                <input
                                    type="text"
                                    className="form-control"
                                    name="phone"
                                    value={user.phone}
                                    disabled={!editMode}
                                    onChange={handleUserChange}
                                />

                            </div>

                            {/* Buttons */}

                            {!editMode ? (

                                <button
                                    className="btn btn-primary"
                                    onClick={() =>
                                        setEditMode(true)
                                    }
                                >
                                    <i className="bi bi-pencil-square me-2"></i>

                                    Edit Profile
                                </button>

                            ) : (

                                <div className="d-flex gap-2">

                                    <button
                                        className="btn btn-success"
                                        onClick={handleSaveProfile}
                                    >
                                        <i className="bi bi-check-circle me-2"></i>

                                        Save Changes
                                    </button>

                                    <button
                                        className="btn btn-outline-secondary"
                                        onClick={() =>
                                            setEditMode(false)
                                        }
                                    >
                                        <i className="bi bi-x-circle me-2"></i>

                                        Cancel
                                    </button>

                                </div>

                            )}

                        </div>

                    </div>

                </div>
                                {/* ================= Password ================= */}

                <div className="col-lg-5">

                    <div className="card shadow border-0">

                        <div className="card-body">

                            <h4 className="mb-4">
                                Change Password
                            </h4>

                            {/* Old Password */}

                            <div className="mb-3">

                                <label className="form-label">
                                    Old Password
                                </label>

                                <div className="input-group">

                                    <input
                                        type={
                                            showOldPassword
                                                ? "text"
                                                : "password"
                                        }
                                        className="form-control"
                                        name="oldPassword"
                                        value={
                                            passwordData.oldPassword
                                        }
                                        onChange={
                                            handlePasswordChange
                                        }
                                    />

                                    <button
                                        type="button"
                                        className="btn btn-outline-secondary"
                                        onClick={() =>
                                            setShowOldPassword(
                                                !showOldPassword
                                            )
                                        }
                                    >
                                        <i
                                            className={
                                                showOldPassword
                                                    ? "bi bi-eye-slash"
                                                    : "bi bi-eye"
                                            }
                                        ></i>
                                    </button>

                                </div>

                            </div>

                            {/* New Password */}

                            <div className="mb-3">

                                <label className="form-label">
                                    New Password
                                </label>

                                <div className="input-group">

                                    <input
                                        type={
                                            showNewPassword
                                                ? "text"
                                                : "password"
                                        }
                                        className="form-control"
                                        name="newPassword"
                                        value={
                                            passwordData.newPassword
                                        }
                                        onChange={
                                            handlePasswordChange
                                        }
                                    />

                                    <button
                                        type="button"
                                        className="btn btn-outline-secondary"
                                        onClick={() =>
                                            setShowNewPassword(
                                                !showNewPassword
                                            )
                                        }
                                    >
                                        <i
                                            className={
                                                showNewPassword
                                                    ? "bi bi-eye-slash"
                                                    : "bi bi-eye"
                                            }
                                        ></i>
                                    </button>

                                </div>

                                {/* Password Strength */}

                                {passwordData.newPassword && (

                                    <>
                                        <div className="progress mt-2">

                                            <div
                                                className={`progress-bar bg-${strengthColor}`}
                                                role="progressbar"
                                                style={{
                                                    width: `${(passwordStrength + 1) * 20}%`,
                                                }}
                                            ></div>

                                        </div>

                                        <small
                                            className={`text-${strengthColor}`}
                                        >
                                            Password Strength :
                                            <strong>
                                                {" "}
                                                {strengthText}
                                            </strong>
                                        </small>
                                    </>

                                )}

                            </div>

                            {/* Confirm Password */}

                            <div className="mb-3">

                                <label className="form-label">
                                    Confirm Password
                                </label>

                                <div className="input-group">

                                    <input
                                        type={
                                            showConfirmPassword
                                                ? "text"
                                                : "password"
                                        }
                                        className="form-control"
                                        name="confirmPassword"
                                        value={
                                            passwordData.confirmPassword
                                        }
                                        onChange={
                                            handlePasswordChange
                                        }
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
                                        <i
                                            className={
                                                showConfirmPassword
                                                    ? "bi bi-eye-slash"
                                                    : "bi bi-eye"
                                            }
                                        ></i>
                                    </button>

                                </div>

                                {passwordData.confirmPassword && (

                                    passwordData.newPassword ===
                                    passwordData.confirmPassword ? (

                                        <small className="text-success">
                                            ✓ Passwords match
                                        </small>

                                    ) : (

                                        <small className="text-danger">
                                            ✗ Passwords do not match
                                        </small>

                                    )

                                )}

                            </div>

                            {/* Change Password Button */}

                            <button
                                className="btn btn-warning w-100"
                                onClick={handleChangePassword}
                            >
                                <i className="bi bi-key-fill me-2"></i>

                                Change Password
                            </button>

                        </div>

                    </div>

                </div>

            </div>

        </div>
    );
};

export default Profile;