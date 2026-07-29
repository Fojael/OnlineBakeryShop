import { BrowserRouter, Routes, Route } from "react-router-dom";

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
import Customers from "../pages/Admin/Customers/Customers";
import Reports from "../pages/Admin/Reports/Reports";
import AIPrediction from "../pages/Admin/AIPrediction/AIPrediction";
import Notifications from "../pages/Admin/Notifications/Notifications";
import ProtectedAdminRoute from "../components/Admin/ProtectedAdminRoute/ProtectedAdminRoute";


// Components
//import Navbar from "../components/Navbar/Navbar";
//import Footer from "../components/Footer/Footer";

const AppRoutes = () => {
    return (
        <BrowserRouter>
            

            <main>
                <Routes>
                    <Route path="/" element={<Home />} />

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
                        element={<Cart />}
                    />

                    <Route
                        path="/checkout"
                        element={<Checkout />}
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
                        element={<Orders />}
                    />

                    <Route
                        path="/profile"
                        element={<Profile />}
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
    path="/admin/dashboard"
    element={
        <ProtectedAdminRoute>
            <Dashboard />
        </ProtectedAdminRoute>
    }
/>

<Route
    path="/admin/products"
    element={
        <ProtectedAdminRoute>
            <AdminProducts />
        </ProtectedAdminRoute>
    }
/>
<Route
    path="/admin/categories"
    element={
        <ProtectedAdminRoute>
            <Categories />
        </ProtectedAdminRoute>
    }
/>

<Route
    path="/admin/inventory"
    element={
        <ProtectedAdminRoute>
            <Inventory />
        </ProtectedAdminRoute>
    }
/>

<Route
    path="/admin/suppliers"
    element={
        <ProtectedAdminRoute>
            <Suppliers />
        </ProtectedAdminRoute>
    }
/>

<Route
    path="/admin/orders"
    element={
        <ProtectedAdminRoute>
            <AdminOrders />
        </ProtectedAdminRoute>
    }
/>

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