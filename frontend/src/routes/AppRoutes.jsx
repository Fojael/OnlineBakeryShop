import { BrowserRouter, Route, Routes } from "react-router-dom";
import ProtectedRoute from "../components/ProtectedRoute/ProtectedRoute";

// ============================================================
// Public Pages
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
// Admin Pages
// ============================================================

import Dashboard from "../pages/Admin/Dashboard/Dashboard";
import AdminProducts from "../pages/Admin/Products/AdminProducts";

import Categories from "../pages/Admin/Categories/Categories";
import AddCategory from "../pages/Admin/Categories/AddCategory";
import EditCategory from "../pages/Admin/Categories/EditCategory";

import Inventory from "../pages/Admin/Inventory/Inventory";
import UpdateInventory from "../pages/Admin/Inventory/UpdateInventory";

import Suppliers from "../pages/Admin/Suppliers/Suppliers";
import AddSupplier from "../pages/Admin/Suppliers/AddSupplier";
import EditSupplier from "../pages/Admin/Suppliers/EditSupplier";

import AdminOrders from "../pages/Admin/Orders/AdminOrders";
import UpdateOrder from "../pages/Admin/Orders/UpdateOrder";

import Customers from "../pages/Admin/Customers/Customers";
import Reports from "../pages/Admin/Reports/Reports";
import AIPrediction from "../pages/Admin/AIPrediction/AIPrediction";
import Notifications from "../pages/Admin/Notifications/Notifications";
import CustomerDashboard from "../pages/customer/CustomerDashboard";

// ============================================================
// Product Pages
// ============================================================

import AddProduct from "../pages/Products/AddProduct";
import EditProduct from "../pages/Products/EditProduct";

// ============================================================
// Protected Route
// ============================================================

import ProtectedAdminRoute from "../components/Admin/ProtectedAdminRoute/ProtectedAdminRoute";

// ============================================================
// App Routes
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
                        path="/login"
                        element={<Login />}
                    />

                    <Route
                        path="/register"
                        element={<Register />}
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

                    <Route
                        path="/about"
                        element={<About />}
                    />

                    <Route
                        path="/contact"
                        element={<Contact />}
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
                    <Route
    path="/customer/dashboard"
    element={
        <ProtectedRoute>
            <CustomerDashboard />
        </ProtectedRoute>
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