import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { Provider } from "react-redux";

import App from "./App";
import { store } from "./redux/store";

import NotificationProvider
    from "./providers/NotificationProvider";

import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap/dist/js/bootstrap.bundle.min.js";
import "bootstrap-icons/font/bootstrap-icons.css";

ReactDOM.createRoot(
    document.getElementById("root")
).render(
    <React.StrictMode>

        <Provider store={store}>

            <BrowserRouter>

                <NotificationProvider>

                    <App />

                </NotificationProvider>

            </BrowserRouter>

        </Provider>

    </React.StrictMode>
);