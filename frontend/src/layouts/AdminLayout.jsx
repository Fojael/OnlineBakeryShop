import { useEffect, useState } from "react";
import AdminSidebar from "../components/Admin/AdminSidebar";
import Topbar from "../components/Admin/Topbar/Topbar";

const AdminLayout = ({ children }) => {
    const [sidebarOpen, setSidebarOpen] = useState(false);

    useEffect(() => {
        if (!sidebarOpen) {
            return undefined;
        }

        const handleKeyDown = (event) => {
            if (event.key === "Escape") {
                setSidebarOpen(false);
            }
        };

        window.addEventListener("keydown", handleKeyDown);
        return () => window.removeEventListener("keydown", handleKeyDown);
    }, [sidebarOpen]);

    return (
        <div className="d-flex">
            <AdminSidebar
                isOpen={sidebarOpen}
                onClose={() => setSidebarOpen(false)}
            />
            <div className="admin-layout__content">
                <Topbar
                    sidebarOpen={sidebarOpen}
                    onToggleSidebar={() => setSidebarOpen((open) => !open)}
                />
                <main className="container mt-4">
                    {children}
                </main>
            </div>
        </div>
    );
};

export default AdminLayout;
