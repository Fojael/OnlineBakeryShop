import { Navigate, useLocation } from "react-router-dom";

const ProtectedRoute = ({ children }) => {
    const accessToken = localStorage.getItem("access");
    const refreshToken = localStorage.getItem("refresh");

    const location = useLocation();

    // User is not logged in
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

    return children;
};

export default ProtectedRoute;