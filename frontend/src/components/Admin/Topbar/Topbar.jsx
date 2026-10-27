const Topbar = ({ sidebarOpen, onToggleSidebar }) => {
    return (
        <header className="bg-light p-3 border-bottom">
            <div className="d-flex align-items-center gap-3">
                <button
                    type="button"
                    className="btn btn-outline-dark d-md-none"
                    aria-label="Toggle admin navigation"
                    aria-controls="admin-sidebar"
                    aria-expanded={sidebarOpen}
                    onClick={onToggleSidebar}
                >
                    <i className="bi bi-list" aria-hidden="true" />
                </button>
                <h4 className="mb-0">Online Bakery Shop - Admin Dashboard</h4>
            </div>
        </header>
    );
};

export default Topbar;