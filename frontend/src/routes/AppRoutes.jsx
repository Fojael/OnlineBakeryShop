import { BrowserRouter, Route, Routes } from "react-router-dom";

// Pages
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

import Dashboard from "../pages/Admin/Dashboard/Dashboard";
import AdminProducts from "../pages/Admin/Products/AdminProducts";
import Categories from "../pages/Admin/Categories/Categories";
import Inventory from "../pages/Admin/Inventory/Inventory";
import Suppliers from "../pages/Admin/Suppliers/Suppliers";
import AdminOrders from "../pages/Admin/Orders/AdminOrders";
import UpdateOrder from "../pages/Admin/Orders/UpdateOrder";
import Customers from "../pages/Admin/Customers/Customers";
import Reports from "../pages/Admin/Reports/Reports";
import AIPrediction from "../pages/Admin/AIPrediction/AIPrediction";
import Notifications from "../pages/Admin/Notifications/Notifications";

import ProtectedAdminRoute from "../components/Admin/ProtectedAdminRoute/ProtectedAdminRoute";

import AddProduct from "../pages/Products/AddProduct";
import EditProduct from "../pages/Products/EditProduct";

import AddCategory from "../pages/Admin/Categories/AddCategory";
import EditCategory from "../pages/Admin/Categories/EditCategory";

import UpdateInventory from "../pages/Admin/Inventory/UpdateInventory";

import AddSupplier from "../pages/Admin/Suppliers/AddSupplier";
import EditSupplier from "../pages/Admin/Suppliers/EditSupplier";

const AppRoutes = () => {
    return (
        <BrowserRouter>
            <main>
                <Routes>

                    {/* Public */}
                    <Route path="/" element={<Home />} />
                    <Route path="/products" element={<Products />} />
                    <Route path="/products/:id" element={<ProductDetails />} />
                    <Route path="/cart" element={<Cart />} />
                    <Route path="/checkout" element={<Checkout />} />
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Register />} />
                    <Route path="/orders" element={<Orders />} />
                    <Route path="/profile" element={<Profile />} />
                    <Route path="/about" element={<About />} />
                    <Route path="/contact" element={<Contact />} />

                    {/* Dashboard */}
                    <Route
                        path="/admin/dashboard"
                        element={
                            <ProtectedAdminRoute>
                                <Dashboard />
                            </ProtectedAdminRoute>
                        }
                    />

                    {/* Products */}
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

                    {/* Categories */}
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

                    {/* Inventory */}
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

                    {/* Suppliers */}
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

                    {/* Orders */}
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

                    {/* Other Admin Pages */}
                    <Route
                        path="/admin/customers"
                        element={
                            <ProtectedAdminRoute>
                                <Customers />
                            </ProtectedAdminRoute>
                        }
                    />

                    <Route
                        path="/admin/reports"
                        element={
                            <ProtectedAdminRoute>
                                <Reports />
                            </ProtectedAdminRoute>
                        }
                    />

                    <Route
                        path="/admin/ai-prediction"
                        element={
                            <ProtectedAdminRoute>
                                <AIPrediction />
                            </ProtectedAdminRoute>
                        }
                    />

                    <Route
                        path="/admin/notifications"
                        element={
                            <ProtectedAdminRoute>
                                <Notifications />
                            </ProtectedAdminRoute>
                        }
                    />

                    {/* 404 */}
                    <Route path="*" element={<NotFound />} />

                </Routes>
            </main>
        </BrowserRouter>
    );
};

export default AppRoutes;