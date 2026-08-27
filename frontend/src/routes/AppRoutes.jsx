import { BrowserRouter, Route, Routes } from "react-router-dom";

import ProtectedRoute from "../components/ProtectedRoute/ProtectedRoute";
import ProtectedAdminRoute from "../components/Admin/ProtectedAdminRoute/ProtectedAdminRoute";

// ============================================================
// PUBLIC PAGES
// ============================================================

import Home from "../pages/Home/Home";
import Products from "../pages/Products/Products";
import ProductDetails from "../pages/ProductDetails/ProductDetails";
import Cart from "../pages/Cart/Cart";
import Checkout from "../pages/Checkout/Checkout";
import Login from "../pages/Login/Login";
import Register from "../pages/Register/Register";
import Orders from "../pages/Orders/Orders";
import Profile from "../pages/Profile/Profile";
import About from "../pages/About/About";
import Contact from "../pages/Contact/Contact";
import NotFound from "../pages/NotFound/NotFound";

// ============================================================
// CUSTOMER PAGES
// ============================================================

import CustomerDashboard from "../pages/Customer/CustomerDashboard";
import Wishlist from "../pages/Customer/Wishlist";
import Address from "../pages/Address/Address";
import AddAddress from "../pages/Address/AddAddress";
import EditAddress from "../pages/Address/EditAddress";
import PaymentSuccess from "../pages/Checkout/PaymentSuccess";
import PaymentFailed from "../pages/Checkout/PaymentFailed";
import PaymentCancelled from "../pages/Checkout/PaymentCancelled";

// ============================================================
// ADMIN DASHBOARD
// ============================================================

import Dashboard from "../pages/Admin/Dashboard/Dashboard";

// ============================================================
// ADMIN PRODUCT PAGES
// ============================================================

import AdminProducts from "../pages/Admin/Products/AdminProducts";
import AddProduct from "../pages/Admin/Products/AddProduct";
import EditProduct from "../pages/Admin/Products/EditProduct";

// ============================================================
// ADMIN CATEGORY PAGES
// ============================================================

import Categories from "../pages/Admin/Categories/Categories";
import AddCategory from "../pages/Admin/Categories/AddCategory";
import EditCategory from "../pages/Admin/Categories/EditCategory";

// ============================================================
// ADMIN INVENTORY PAGES
// ============================================================

import Inventory from "../pages/Admin/Inventory/Inventory";
import UpdateInventory from "../pages/Admin/Inventory/UpdateInventory";

// ============================================================
// ADMIN SUPPLIER PAGES
// ============================================================

import Suppliers from "../pages/Admin/Suppliers/Suppliers";
import AddSupplier from "../pages/Admin/Suppliers/AddSupplier";
import EditSupplier from "../pages/Admin/Suppliers/EditSupplier";

// ============================================================
// ADMIN ORDER PAGES
// ============================================================

import AdminOrders from "../pages/Admin/Orders/AdminOrders";
import UpdateOrder from "../pages/Admin/Orders/UpdateOrder";

// ============================================================
// ADMIN CUSTOMER PAGES
// ============================================================

import Customers from "../pages/Admin/Customers/Customers";

// ============================================================
// ADMIN OTHER PAGES
// ============================================================

import Reports from "../pages/Admin/Reports/Reports";
import AIPrediction from "../pages/Admin/AIPrediction/AIPrediction";
import Notifications from "../pages/Admin/Notifications/Notifications";

// ============================================================
// APP ROUTES
// ============================================================

const AppRoutes = () => {
    return (
        <BrowserRouter>
            <main>
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
                        CUSTOMER PROTECTED ROUTES
                    ================================================== */}

                    <Route
                        path="/cart"
                        element={
                            <ProtectedRoute>
                                <Cart />
                            </ProtectedRoute>
                        }
                    />

                    <Route
                        path="/checkout"
                        element={
                            <ProtectedRoute>
                                <Checkout />
                            </ProtectedRoute>
                        }
                    />

                    <Route
                        path="/orders"
                        element={
                            <ProtectedRoute>
                                <Orders />
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
    PAYMENT RESULT PAGES
================================================== */}

<Route
    path="/payment/success/"
    element={<PaymentSuccess />}
/>

<Route
    path="/payment/failed/"
    element={<PaymentFailed />}
/>

<Route
    path="/payment/cancelled/"
    element={<PaymentCancelled />}
/>

                    {/* ==================================================
                        CUSTOMER DASHBOARD
                    ================================================== */}

                    <Route
                        path="/customer/dashboard"
                        element={
                            <ProtectedRoute>
                                <CustomerDashboard />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/wishlist"
                        element={
                            <ProtectedRoute>
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
        <ProtectedRoute>
            <Address />
        </ProtectedRoute>
    }
/>

<Route
    path="/address/add"
    element={
        <ProtectedRoute>
            <AddAddress />
        </ProtectedRoute>
    }
/>

<Route
    path="/address/edit/:id"
    element={
        <ProtectedRoute>
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

                    {/* ==================================================
                        404
                    ================================================== */}

                    <Route
                        path="*"
                        element={<NotFound />}
                    />

                </Routes>
            </main>
        </BrowserRouter>
    );
};

export default AppRoutes;