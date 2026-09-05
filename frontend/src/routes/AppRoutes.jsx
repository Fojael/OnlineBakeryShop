
import {
    Route,
    Routes,
} from "react-router-dom";

import ProtectedRoute
    from "../components/ProtectedRoute/ProtectedRoute";

import ProtectedAdminRoute
    from "../components/Admin/ProtectedAdminRoute/ProtectedAdminRoute";

// ============================================================
// PUBLIC PAGES
// ============================================================

import Home
    from "../pages/Home/Home";

import Products
    from "../pages/Products/Products";

import ProductDetails
    from "../pages/ProductDetails/ProductDetails";

import Login
    from "../pages/Login/Login";

import Register
    from "../pages/Register/Register";

import About
    from "../pages/About/About";

import Contact
    from "../pages/Contact/Contact";

import NotFound
    from "../pages/NotFound/NotFound";

// ============================================================
// CUSTOMER PAGES
// ============================================================

import Cart
    from "../pages/Cart/Cart";

import Checkout
    from "../pages/Checkout/Checkout";

import Orders
    from "../pages/Orders/Orders";

import OrderDetails
    from "../pages/Orders/OrderDetails";

import Profile
    from "../pages/Profile/Profile";

import CustomerDashboard
    from "../pages/Customer/CustomerDashboard";

import Wishlist
    from "../pages/Customer/Wishlist";

import Address
    from "../pages/Address/Address";

import AddAddress
    from "../pages/Address/AddAddress";

import EditAddress
    from "../pages/Address/EditAddress";

// ============================================================
// CUSTOMER NOTIFICATIONS
// ============================================================

import NotificationsPage
    from "../pages/Notifications/NotificationsPage";

// ============================================================
// PAYMENT RESULT PAGES
// ============================================================

import PaymentSuccess
    from "../pages/Checkout/PaymentSuccess";

import PaymentFailed
    from "../pages/Checkout/PaymentFailed";

import PaymentCancelled
    from "../pages/Checkout/PaymentCancelled";

// ============================================================
// ADMIN DASHBOARD
// ============================================================

import Dashboard
    from "../pages/Admin/Dashboard/Dashboard";

// ============================================================
// ADMIN PRODUCT PAGES
// ============================================================

import AdminProducts
    from "../pages/Admin/Products/AdminProducts";

import AddProduct
    from "../pages/Admin/Products/AddProduct";

import EditProduct
    from "../pages/Admin/Products/EditProduct";

// ============================================================
// ADMIN CATEGORY PAGES
// ============================================================

import Categories
    from "../pages/Admin/Categories/Categories";

import AddCategory
    from "../pages/Admin/Categories/AddCategory";

import EditCategory
    from "../pages/Admin/Categories/EditCategory";

// ============================================================
// ADMIN INVENTORY PAGES
// ============================================================

import Inventory
    from "../pages/Admin/Inventory/Inventory";

import UpdateInventory
    from "../pages/Admin/Inventory/UpdateInventory";

import InventoryTransactions
    from "../pages/Admin/Inventory/InventoryTransactions";

import ProductionBatches
    from "../pages/Admin/Inventory/ProductionBatches";

// ============================================================
// ADMIN SUPPLIER PAGES
// ============================================================

import Suppliers
    from "../pages/Admin/Suppliers/Suppliers";

import AddSupplier
    from "../pages/Admin/Suppliers/AddSupplier";

import EditSupplier
    from "../pages/Admin/Suppliers/EditSupplier";

// ============================================================
// ADMIN DELIVERY RIDER PAGES
// ============================================================

import DeliveryRiders
    from "../pages/Admin/DeliveryRiders/DeliveryRiders";

import RiderDeliveries
    from "../pages/Admin/DeliveryRiders/RiderDeliveries";

import DeliveryManagement
    from "../pages/Admin/Delivery/DeliveryManagement";

// ============================================================
// ADMIN ORDER PAGES
// ============================================================

import AdminOrders from "../pages/Admin/Orders/AdminOrders";

import UpdateOrder from "../pages/Admin/Orders/UpdateOrder";
// ============================================================
// ADMIN CUSTOMER PAGES
// ============================================================

import Customers
    from "../pages/Admin/Customers/Customers";

// ============================================================
// ADMIN OTHER PAGES
// ============================================================

import Reports
    from "../pages/Admin/Reports/Reports";

import AIPrediction
    from "../pages/Admin/AIPrediction/AIPrediction";

import Notifications
    from "../pages/Admin/Notifications/Notifications";

import Payments
    from "../pages/Admin/Payments/Payments";

import Refunds
    from "../pages/Admin/Refunds/Refunds";

import AdminProfile
    from "../pages/Admin/Profile/AdminProfile";


/// ============================================================
// SUPPLIER ROUTES
// ============================================================

import SupplierDashboard
    from "../pages/Supplier/Dashboard/SupplierDashboard";

import SupplierProfile
    from "../pages/Supplier/Profile/SupplierProfile";

import SupplierProducts
    from "../pages/Supplier/Products/SupplierProducts";

import SupplierInventory
    from "../pages/Supplier/Inventory/SupplierInventory";

import SupplierOrders
    from "../pages/Supplier/Orders/SupplierOrders";

import SupplierOrderDetails
    from "../pages/Supplier/Orders/SupplierOrderDetails";

import SupplierPayments
    from "../pages/Supplier/Payments/SupplierPayments";

// ============================================================
// DELIVERY RIDER ROUTES
// ============================================================

import DeliveryDashboard
    from "../delivery/DeliveryDashboard";

import DeliveryOrders
    from "../delivery/DeliveryOrders";

import DeliveryOrderDetails
    from "../delivery/DeliveryOrderDetails";

import DeliveryProfile
    from "../delivery/DeliveryProfile";


// ============================================================
// APP ROUTES
// ============================================================

const AppRoutes = () => {

    return (

        <Routes>

            {/* ==================================================
                PUBLIC ROUTES
            ================================================== */}

            <Route
                path="/"
                element={<Home />}
            />

            <Route
                path="/products"
                element={<Products />}
            />

            <Route
                path="/products/:id"
                element={<ProductDetails />}
            />

            <Route
                path="/about"
                element={<About />}
            />

            <Route
                path="/contact"
                element={<Contact />}
            />

            <Route
                path="/login"
                element={<Login />}
            />

            <Route
                path="/register"
                element={<Register />}
            />


            {/* ==================================================
                CUSTOMER ROUTES
            ================================================== */}

            <Route
                path="/cart"
                element={
                    <ProtectedRoute allowedRoles={["CUSTOMER"]}>
                        <Cart />
                    </ProtectedRoute>
                }
            />

            <Route
                path="/checkout"
                element={
                    <ProtectedRoute allowedRoles={["CUSTOMER"]}>
                        <Checkout />
                    </ProtectedRoute>
                }
            />

            <Route
                path="/orders"
                element={
                    <ProtectedRoute allowedRoles={["CUSTOMER"]}>
                        <Orders />
                    </ProtectedRoute>
                }
            />

            <Route
                path="/orders/:orderId"
                element={
                    <ProtectedRoute allowedRoles={["CUSTOMER"]}>
                        <OrderDetails />
                    </ProtectedRoute>
                }
            />

            <Route
                path="/profile"
                element={
                    <ProtectedRoute>
                        <Profile />
                    </ProtectedRoute>
                }
            />


            {/* ==================================================
                CUSTOMER NOTIFICATIONS
            ================================================== */}

            <Route
                path="/notifications"
                element={
                    <ProtectedRoute>
                        <NotificationsPage />
                    </ProtectedRoute>
                }
            />


            {/* ==================================================
                PAYMENT RESULT ROUTES
            ================================================== */}

            <Route
                path="/checkout/success"
                element={
                    <ProtectedRoute allowedRoles={["CUSTOMER"]}>
                        <PaymentSuccess />
                    </ProtectedRoute>
                }
            />

            <Route
                path="/checkout/failed"
                element={
                    <ProtectedRoute allowedRoles={["CUSTOMER"]}>
                        <PaymentFailed />
                    </ProtectedRoute>
                }
            />

            <Route
                path="/checkout/cancelled"
                element={
                    <ProtectedRoute allowedRoles={["CUSTOMER"]}>
                        <PaymentCancelled />
                    </ProtectedRoute>
                }
            />


            {/* ==================================================
                CUSTOMER DASHBOARD
            ================================================== */}

            <Route
                path="/customer/dashboard"
                element={
                    <ProtectedRoute allowedRoles={["CUSTOMER"]}>
                        <CustomerDashboard />
                    </ProtectedRoute>
                }
            />

            <Route
                path="/wishlist"
                element={
                    <ProtectedRoute allowedRoles={["CUSTOMER"]}>
                        <Wishlist />
                    </ProtectedRoute>
                }
            />


            {/* ==================================================
                CUSTOMER ADDRESS BOOK
            ================================================== */}

            <Route
                path="/address"
                element={
                    <ProtectedRoute allowedRoles={["CUSTOMER"]}>
                        <Address />
                    </ProtectedRoute>
                }
            />

            <Route
                path="/address/add"
                element={
                    <ProtectedRoute allowedRoles={["CUSTOMER"]}>
                        <AddAddress />
                    </ProtectedRoute>
                }
            />

            <Route
                path="/address/edit/:id"
                element={
                    <ProtectedRoute allowedRoles={["CUSTOMER"]}>
                        <EditAddress />
                    </ProtectedRoute>
                }
            />


            {/* ==================================================
                ADMIN DASHBOARD
            ================================================== */}

            <Route
                path="/admin/dashboard"
                element={
                    <ProtectedAdminRoute>
                        <Dashboard />
                    </ProtectedAdminRoute>
                }
            />


            {/* ==================================================
                ADMIN PRODUCTS
            ================================================== */}

            <Route
                path="/admin/products"
                element={
                    <ProtectedAdminRoute>
                        <AdminProducts />
                    </ProtectedAdminRoute>
                }
            />

            <Route
                path="/admin/products/add"
                element={
                    <ProtectedAdminRoute>
                        <AddProduct />
                    </ProtectedAdminRoute>
                }
            />

            <Route
                path="/admin/products/edit/:id"
                element={
                    <ProtectedAdminRoute>
                        <EditProduct />
                    </ProtectedAdminRoute>
                }
            />


            {/* ==================================================
                ADMIN CATEGORIES
            ================================================== */}

            <Route
                path="/admin/categories"
                element={
                    <ProtectedAdminRoute>
                        <Categories />
                    </ProtectedAdminRoute>
                }
            />

            <Route
                path="/admin/categories/add"
                element={
                    <ProtectedAdminRoute>
                        <AddCategory />
                    </ProtectedAdminRoute>
                }
            />

            <Route
                path="/admin/categories/edit/:id"
                element={
                    <ProtectedAdminRoute>
                        <EditCategory />
                    </ProtectedAdminRoute>
                }
            />


            {/* ==================================================
                ADMIN INVENTORY
            ================================================== */}

            <Route
                path="/admin/inventory"
                element={
                    <ProtectedAdminRoute>
                        <Inventory />
                    </ProtectedAdminRoute>
                }
            />

            <Route
                path="/admin/inventory/update/:id"
                element={
                    <ProtectedAdminRoute>
                        <UpdateInventory />
                    </ProtectedAdminRoute>
                }
            />

            <Route
                path="/admin/inventory/transactions"
                element={
                    <ProtectedAdminRoute>
                        <InventoryTransactions />
                    </ProtectedAdminRoute>
                }
            />

            <Route
                path="/admin/inventory/batches"
                element={
                    <ProtectedAdminRoute>
                        <ProductionBatches />
                    </ProtectedAdminRoute>
                }
            />


            {/* ==================================================
                ADMIN SUPPLIERS
            ================================================== */}

            <Route
                path="/admin/suppliers"
                element={
                    <ProtectedAdminRoute>
                        <Suppliers />
                    </ProtectedAdminRoute>
                }
            />

            <Route
                path="/admin/suppliers/add"
                element={
                    <ProtectedAdminRoute>
                        <AddSupplier />
                    </ProtectedAdminRoute>
                }
            />

            <Route
                path="/admin/suppliers/edit/:id"
                element={
                    <ProtectedAdminRoute>
                        <EditSupplier />
                    </ProtectedAdminRoute>
                }
            />

            {/* ==================================================
                ADMIN DELIVERY RIDERS
            ================================================== */}

            <Route
                path="/admin/delivery-riders"
                element={
                    <ProtectedAdminRoute>
                        <DeliveryRiders />
                    </ProtectedAdminRoute>
                }
            />

            <Route
                path="/admin/riders"
                element={
                    <ProtectedAdminRoute>
                        <DeliveryRiders />
                    </ProtectedAdminRoute>
                }
            />

            <Route
                path="/admin/riders/:riderId/deliveries"
                element={
                    <ProtectedAdminRoute>
                        <RiderDeliveries />
                    </ProtectedAdminRoute>
                }
            />


            {/* ==================================================
                ADMIN ORDERS
            ================================================== */}

            <Route
                path="/admin/orders"
                element={
                    <ProtectedAdminRoute>
                        <AdminOrders />
                    </ProtectedAdminRoute>
                }
            />

            <Route
                path="/admin/orders/update/:id"
                element={
                    <ProtectedAdminRoute>
                        <UpdateOrder />
                    </ProtectedAdminRoute>
                }
            />

            <Route
                path="/admin/delivery-management"
                element={
                    <ProtectedAdminRoute>
                        <DeliveryManagement />
                    </ProtectedAdminRoute>
                }
            />

            <Route
                path="/admin/delivery"
                element={
                    <ProtectedAdminRoute>
                        <DeliveryManagement />
                    </ProtectedAdminRoute>
                }
            />

            <Route
                path="/admin/delivery-management"
                element={
                    <ProtectedAdminRoute>
                        <DeliveryManagement />
                    </ProtectedAdminRoute>
                }
            />

            <Route
                path="/admin/rider-management"
                element={
                    <ProtectedAdminRoute>
                        <DeliveryRiders />
                    </ProtectedAdminRoute>
                }
            />


            {/* ==================================================
                ADMIN CUSTOMERS
            ================================================== */}

            <Route
                path="/admin/customers"
                element={
                    <ProtectedAdminRoute>
                        <Customers />
                    </ProtectedAdminRoute>
                }
            />


            {/* ==================================================
                ADMIN REPORTS
            ================================================== */}

            <Route
                path="/admin/reports"
                element={
                    <ProtectedAdminRoute>
                        <Reports />
                    </ProtectedAdminRoute>
                }
            />


            {/* ==================================================
                ADMIN AI PREDICTION
            ================================================== */}

            <Route
                path="/admin/ai-prediction"
                element={
                    <ProtectedAdminRoute>
                        <AIPrediction />
                    </ProtectedAdminRoute>
                }
            />


            {/* ==================================================
                ADMIN NOTIFICATIONS
            ================================================== */}

            <Route
                path="/admin/notifications"
                element={
                    <ProtectedAdminRoute>
                        <Notifications />
                    </ProtectedAdminRoute>
                }
            />

            <Route
                path="/admin/payments"
                element={
                    <ProtectedAdminRoute>
                        <Payments />
                    </ProtectedAdminRoute>
                }
            />

            <Route
                path="/admin/payment-management"
                element={
                    <ProtectedAdminRoute>
                        <Payments />
                    </ProtectedAdminRoute>
                }
            />

            <Route
                path="/admin/refunds"
                element={
                    <ProtectedAdminRoute>
                        <Refunds />
                    </ProtectedAdminRoute>
                }
            />

            <Route
                path="/admin/profile"
                element={
                    <ProtectedAdminRoute>
                        <AdminProfile />
                    </ProtectedAdminRoute>
                }
            />

           {/* ======================================================
    SUPPLIER DASHBOARD
====================================================== */}

<Route
    path="/supplier/dashboard"
    element={
        <ProtectedRoute
            allowedRoles={["SUPPLIER"]}
        >
            <SupplierDashboard />
        </ProtectedRoute>
    }
/>


{/* ======================================================
    SUPPLIER PROFILE
====================================================== */}

<Route
    path="/supplier/profile"
    element={
        <ProtectedRoute
            allowedRoles={["SUPPLIER"]}
        >
            <SupplierProfile />
        </ProtectedRoute>
    }
/>


{/* ======================================================
    SUPPLIER PRODUCTS
====================================================== */}

<Route
    path="/supplier/products"
    element={
        <ProtectedRoute
            allowedRoles={["SUPPLIER"]}
        >
            <SupplierProducts />
        </ProtectedRoute>
    }
/>


{/* ======================================================
    SUPPLIER INVENTORY
====================================================== */}

<Route
    path="/supplier/inventory"
    element={
        <ProtectedRoute
            allowedRoles={["SUPPLIER"]}
        >
            <SupplierInventory />
        </ProtectedRoute>
    }
/>


{/* ======================================================
    SUPPLIER ORDERS
====================================================== */}

<Route
    path="/supplier/orders"
    element={
        <ProtectedRoute
            allowedRoles={["SUPPLIER"]}
        >
            <SupplierOrders />
        </ProtectedRoute>
    }
/>


{/* ======================================================
    SUPPLIER ORDER DETAILS
====================================================== */}

<Route
    path="/supplier/orders/:id"
    element={
        <ProtectedRoute
            allowedRoles={["SUPPLIER"]}
        >
            <SupplierOrderDetails />
        </ProtectedRoute>
    }
/>


{/* ======================================================
    SUPPLIER PAYMENTS
====================================================== */}

<Route
    path="/supplier/payments"
    element={
        <ProtectedRoute
            allowedRoles={["SUPPLIER"]}
        >
            <SupplierPayments />
        </ProtectedRoute>
    }
/>


            {/* ==================================================
                DELIVERY RIDER ROUTES
            ================================================== */}

            <Route
                path="/delivery/dashboard"
                element={
                    <ProtectedRoute allowedRoles={["DELIVERY", "DELIVERY_RIDER"]}>
                        <DeliveryDashboard />
                    </ProtectedRoute>
                }
            />

            <Route
                path="/rider/dashboard"
                element={
                    <ProtectedRoute allowedRoles={["DELIVERY_RIDER"]}>
                        <DeliveryDashboard />
                    </ProtectedRoute>
                }
            />

            <Route
                path="/delivery/orders"
                element={
                    <ProtectedRoute allowedRoles={["DELIVERY", "DELIVERY_RIDER"]}>
                        <DeliveryOrders />
                    </ProtectedRoute>
                }
            />

            <Route
                path="/rider/deliveries"
                element={
                    <ProtectedRoute allowedRoles={["DELIVERY_RIDER"]}>
                        <DeliveryOrders />
                    </ProtectedRoute>
                }
            />

            <Route
                path="/delivery/orders/:orderId"
                element={
                    <ProtectedRoute allowedRoles={["DELIVERY", "DELIVERY_RIDER"]}>
                        <DeliveryOrderDetails />
                    </ProtectedRoute>
                }
            />

            <Route
                path="/delivery/profile"
                element={
                    <ProtectedRoute allowedRoles={["DELIVERY", "DELIVERY_RIDER"]}>
                        <DeliveryProfile />
                    </ProtectedRoute>
                }
            />

            {/* ==================================================
                404
            ================================================== */}

            <Route
                path="*"
                element={<NotFound />}
            />

        </Routes>

    );

};

export default AppRoutes;

