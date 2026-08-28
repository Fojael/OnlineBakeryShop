import {
    BrowserRouter,
    Routes,
    Route,
} from "react-router-dom";

import PaymentSuccess from "./pages/PaymentSuccess";
import PaymentFailed from "./pages/PaymentFailed";
import PaymentCancelled from "./pages/PaymentCancelled";


function App() {

    return (

        <BrowserRouter>

            <Routes>

                {/* Other routes */}

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

            </Routes>

        </BrowserRouter>
    );
}


export default App;