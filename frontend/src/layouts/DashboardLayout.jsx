import Sidebar from "../components/Admin/Sidebar/Sidebar";
import Topbar from "../components/Admin/Topbar/Topbar";

const DashboardLayout = ({ children }) => {
    return (
        <div className="d-flex">

            {/* Sidebar */}
            <Sidebar />

            {/* Main Content */}
            <div className="flex-grow-1">

                {/* Topbar */}
                <Topbar />

                {/* Page Content */}
                <div className="container mt-4">
                    {children}
                </div>

            </div>

        </div>
    );
};

export default DashboardLayout;