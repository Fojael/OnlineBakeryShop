import React from "react";
import ReactDOM from "react-dom/client";

import App from "./App";

import { Provider } from "react-redux";
import { store } from "./redux/store";

import { AuthProvider } from "./context/AuthContext";
import NotificationProvider from "./providers/NotificationProvider";

import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap/dist/js/bootstrap.bundle.min.js";
import "bootstrap-icons/font/bootstrap-icons.css";

ReactDOM.createRoot(
    document.getElementById("root")
).render(
    <React.StrictMode>

        <Provider store={store}>

            <AuthProvider>

                <NotificationProvider>

                    <App />

                </NotificationProvider>

            </AuthProvider>

        </Provider>

    </React.StrictMode>
);