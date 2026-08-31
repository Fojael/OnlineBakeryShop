import {
    useState,
} from "react";

import SupplierSidebar
    from "../../../components/Supplier/SupplierSidebar";

import SupplierNavbar
    from "../../../components/Supplier/SupplierNavbar";

import SupplierStatCard
    from "../../../components/Supplier/SupplierStatCard";

import SupplierRecentActivity
    from "../../../components/Supplier/SupplierRecentActivity";

import "../../../styles/SupplierDashboard.css";


const SupplierDashboard = () => {

    const [dashboardData] = useState({

        totalProducts: 0,

        pendingOrders: 0,

        completedOrders: 0,

        pendingPayments: 0,

    });


    const recentActivities = [];


    return (

        <div className="supplier-dashboard-wrapper">

            {/* SIDEBAR */}

            <SupplierSidebar />


            {/* MAIN */}

            <div className="supplier-main-content">

                <SupplierNavbar />


                <main className="supplier-dashboard-content">

                    {/* PAGE HEADER */}

                    <div className="mb-4">

                        <h2 className="fw-bold">
                            Dashboard
                        </h2>

                        <p className="text-muted mb-0">
                            Welcome to your supplier dashboard.
                        </p>

                    </div>


                    {/* STATISTICS */}

                    <div className="row g-4 mb-4">

                        <div className="col-xl-3 col-md-6">

                            <SupplierStatCard
                                title="Supply Products"
                                value={
                                    dashboardData.totalProducts
                                }
                                icon="bi bi-box-seam"
                                iconClass="text-primary"
                                description="Products you supply"
                            />

                        </div>


                        <div className="col-xl-3 col-md-6">

                            <SupplierStatCard
                                title="Pending Orders"
                                value={
                                    dashboardData.pendingOrders
                                }
                                icon="bi bi-hourglass-split"
                                iconClass="text-warning"
                                description="Orders waiting"
                            />

                        </div>


                        <div className="col-xl-3 col-md-6">

                            <SupplierStatCard
                                title="Completed Orders"
                                value={
                                    dashboardData.completedOrders
                                }
                                icon="bi bi-check-circle"
                                iconClass="text-success"
                                description="Successfully completed"
                            />

                        </div>


                        <div className="col-xl-3 col-md-6">

                            <SupplierStatCard
                                title="Pending Payments"
                                value={
                                    dashboardData.pendingPayments
                                }
                                icon="bi bi-cash-stack"
                                iconClass="text-danger"
                                description="Payments awaiting"
                            />

                        </div>

                    </div>


                    {/* CONTENT */}

                    <div className="row g-4">

                        <div className="col-lg-8">

                            <SupplierRecentActivity
                                activities={
                                    recentActivities
                                }
                            />

                        </div>


                        <div className="col-lg-4">

                            <div className="card border-0 shadow-sm h-100">

                                <div className="card-body">

                                    <h5 className="fw-bold mb-4">
                                        Quick Actions
                                    </h5>


                                    <div className="d-grid gap-3">

                                        <button
                                            type="button"
                                            className="btn btn-primary"
                                        >
                                            View Supply Orders
                                        </button>


                                        <button
                                            type="button"
                                            className="btn btn-outline-primary"
                                        >
                                            Manage Supplies
                                        </button>


                                        <button
                                            type="button"
                                            className="btn btn-outline-secondary"
                                        >
                                            View Payments
                                        </button>

                                    </div>

                                </div>

                            </div>

                        </div>

                    </div>

                </main>

            </div>

        </div>

    );
};


export default SupplierDashboard;