import { Navigate, useLocation } from "react-router-dom";

const ProtectedAdminRoute = ({ children }) => {
    const location = useLocation();

    // ============================================================
    // GET AUTHENTICATION DATA
    // ============================================================

    const accessToken =
        localStorage.getItem("access") ||
        sessionStorage.getItem("access");

    const refreshToken =
        localStorage.getItem("refresh") ||
        sessionStorage.getItem("refresh");

    const storedUser =
        localStorage.getItem("user") ||
        sessionStorage.getItem("user");

    // ============================================================
    // CHECK LOGIN
    // ============================================================

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

    // ============================================================
    // CHECK USER DATA
    // ============================================================

    if (!storedUser) {
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

    // ============================================================
    // PARSE USER
    // ============================================================

    let user;

    try {
        user = JSON.parse(storedUser);
    } catch (error) {
        console.error(
            "Invalid stored user data:",
            error
        );

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

    // ============================================================
    // ADMIN ROLE CHECK
    // ============================================================

    if (user?.role !== "ADMIN") {
        return (
            <Navigate
                to="/"
                replace
            />
        );
    }

    // ============================================================
    // ADMIN AUTHORIZED
    // ============================================================

    return children;
};

export default ProtectedAdminRoute;