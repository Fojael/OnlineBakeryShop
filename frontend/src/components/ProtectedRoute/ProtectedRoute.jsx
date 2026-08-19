import { Navigate, useLocation } from "react-router-dom";

const ProtectedRoute = ({
    children,
    allowedRoles = [],
}) => {
    const location = useLocation();

    // =========================================================
    // GET AUTH DATA
    // =========================================================

    const accessToken =
        localStorage.getItem("access");

    const refreshToken =
        localStorage.getItem("refresh");

    const userData =
        localStorage.getItem("user");

    const storedRole =
        localStorage.getItem("role");

    // =========================================================
    // NOT AUTHENTICATED
    // =========================================================

    if (!accessToken || !refreshToken) {
        return (
            <Navigate
                to="/login"
                replace
                state={{
                    from: location,
                }}
            />
        );
    }

    // =========================================================
    // GET USER ROLE
    // =========================================================

    let userRole = storedRole;

    // If role is not separately stored, try to get it
    // from the stored user object.

    if (!userRole && userData) {
        try {
            const user = JSON.parse(userData);

            userRole = user?.role || null;
        } catch (error) {
            console.error(
                "Failed to parse stored user:",
                error
            );
        }
    }

    // =========================================================
    // NORMALIZE ROLE
    // =========================================================

    userRole = String(userRole || "")
        .trim()
        .toUpperCase();

    // =========================================================
    // ROLE PROTECTION
    // =========================================================

    if (
        allowedRoles.length > 0 &&
        !allowedRoles
            .map((role) =>
                String(role)
                    .trim()
                    .toUpperCase()
            )
            .includes(userRole)
    ) {
        // User is authenticated but does not
        // have permission to access this page.

        return (
            <Navigate
                to="/"
                replace
            />
        );
    }

    // =========================================================
    // AUTHENTICATED + AUTHORIZED
    // =========================================================

    return children;
};

export default ProtectedRoute;