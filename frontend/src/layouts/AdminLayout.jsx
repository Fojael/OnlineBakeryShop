import AdminSidebar from "../components/Admin/AdminSidebar";
import Topbar from "../components/Admin/Topbar/Topbar";

const AdminLayout = ({ children }) => (
    <div className="d-flex">
        <AdminSidebar />
        <div className="flex-grow-1">
            <Topbar />
            <div className="container mt-4">
                {children}
            </div>
        </div>
    </div>
);

export default AdminLayout;
