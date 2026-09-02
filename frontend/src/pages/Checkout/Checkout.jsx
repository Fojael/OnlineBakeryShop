import {
    useState,
} from "react";

import {
    useNavigate,
} from "react-router-dom";

import {
    toast,
} from "react-toastify";

import {
    createOrder,
} from "../../services/orderService";

import {
    createPayment,
} from "../../services/paymentService";

const initialAddress = {
    full_name: "",
    phone: "",
    email: "",
    division: "",
    district: "",
    city: "",
    area: "",
    street_address: "",
    postal_code: "",
    delivery_note: "",
};

const Checkout = () => {

    const navigate = useNavigate();

    // ========================================================
    // STATE
    // ========================================================

    const [
        shippingAddress,
        setShippingAddress,
    ] = useState("");

    const [
        addressForm,
        setAddressForm,
    ] = useState(initialAddress);

    const [
        paymentMethod,
        setPaymentMethod,
    ] = useState("Cash on Delivery");

    const [
        loading,
        setLoading,
    ] = useState(false);

    const handleAddressFieldChange = (event) => {
        const { name, value } = event.target;

        setAddressForm((previous) => ({
            ...previous,
            [name]: value,
        }));

        if (shippingAddress) {
            setShippingAddress("");
        }
    };

    const validateAddress = () => {
        const requiredFields = [
            "full_name",
            "phone",
            "email",
            "division",
            "district",
            "city",
            "area",
            "street_address",
            "postal_code",
        ];

        for (const field of requiredFields) {
            if (!String(addressForm[field] || "").trim()) {
                toast.error(
                    `Please enter your ${field.replace("_", " ")}.`
                );
                return false;
            }
        }

        if (!/^01[3-9]\d{8}$/.test(addressForm.phone.trim())) {
            toast.error("Please enter a valid Bangladeshi phone number.");
            return false;
        }

        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(addressForm.email.trim())) {
            toast.error("Please enter a valid email address.");
            return false;
        }

        return true;
    };

    // ========================================================
    // PLACE ORDER
    // ========================================================

    const handlePlaceOrder = async () => {

        const hasStructuredAddress = Object.values(addressForm).some(
            (value) => String(value || "").trim()
        );

        if (!hasStructuredAddress && !shippingAddress.trim()) {
            toast.error(
                "Please enter your shipping address details."
            );
            return;
        }

        if (hasStructuredAddress && !validateAddress()) {
            return;
        }

        if (loading) {
            return;
        }

        setLoading(true);

        try {

            const orderData = {
                payment_method: paymentMethod,
                ...(hasStructuredAddress
                    ? addressForm
                    : {
                        shipping_address: shippingAddress.trim(),
                    }),
            };

            console.log(
                "Sending order data:",
                orderData
            );

            // =================================================
            // CREATE ORDER
            // =================================================

            const response = await createOrder(
                orderData
            );

            console.log(
                "Complete order response:",
                response
            );

            console.log(
                "Order response data:",
                response.data
            );

            // =================================================
            // GET ORDER
            // =================================================

            const order =
                response.data?.order ||
                response.data;

            const orderId =
                order?.id ||
                response.data?.order_id ||
                response.data?.id;

            // =================================================
            // CHECK ORDER ID
            // =================================================

            if (!orderId) {

                console.error(
                    "Order ID missing. Backend returned:",
                    response.data
                );

                throw new Error(
                    "Order was created, but Order ID was not returned."
                );
            }

            console.log(
                "Created Order ID:",
                orderId
            );

            // =================================================
            // CASH ON DELIVERY
            // =================================================

            if (
                paymentMethod
                === "Cash on Delivery"
            ) {

                toast.success(
                    "Order placed successfully."
                );

                navigate(
                    `/orders/${orderId}`
                );

                return;
            }

            // =================================================
            // SSL COMMERZ
            // =================================================

            if (
                paymentMethod
                === "SSLCommerz"
            ) {

                console.log(
                    "Creating SSLCommerz payment for order:",
                    orderId
                );

                const paymentResponse =
                    await createPayment(
                        orderId
                    );

                console.log(
                    "Payment response:",
                    paymentResponse
                );

                // =================================================
                // GET GATEWAY URL
                // =================================================

                const gatewayUrl =
                    paymentResponse?.gateway_url ||
                    paymentResponse?.data?.gateway_url;

                if (!gatewayUrl) {

                    console.error(
                        "Gateway URL missing:",
                        paymentResponse
                    );

                    throw new Error(
                        "Payment gateway URL was not returned."
                    );
                }

                toast.info(
                    "Redirecting to SSLCommerz..."
                );

                // =================================================
                // REDIRECT TO SSL COMMERZ
                // =================================================

                window.location.href =
                    gatewayUrl;

                return;
            }

            // =================================================
            // UNSUPPORTED PAYMENT METHOD
            // =================================================

            throw new Error(
                "Unsupported payment method."
            );

        } catch (error) {

            console.error(
                "Checkout error:",
                error
            );

            console.error(
                "Backend error response:",
                error?.response?.data
            );

            const backendMessage =
                error?.response?.data?.detail ||
                error?.response?.data?.message ||
                error?.message ||
                "Could not place order.";

            toast.error(
                backendMessage
            );

        } finally {

            setLoading(false);
        }
    };


    // ========================================================
    // RENDER
    // ========================================================

    return (

        <div className="container py-5">

            <div className="row justify-content-center">

                <div className="col-lg-8">

                    <div className="card shadow-sm">

                        <div className="card-body p-4">

                            <h2 className="mb-4">
                                Checkout
                            </h2>

                            {/* ==================================
                                SHIPPING ADDRESS
                            ================================== */}

                            <div className="mb-4">

                                <div className="d-flex justify-content-between align-items-center mb-3">
                                    <h5 className="mb-0">Shipping Address</h5>
                                    <small className="text-muted">Required for delivery</small>
                                </div>

                                <div className="row g-3">
                                    <div className="col-md-6">
                                        <label className="form-label">Full Name</label>
                                        <input
                                            type="text"
                                            name="full_name"
                                            className="form-control"
                                            value={addressForm.full_name}
                                            onChange={handleAddressFieldChange}
                                            disabled={loading}
                                            placeholder="Enter full name"
                                        />
                                    </div>

                                    <div className="col-md-6">
                                        <label className="form-label">Phone</label>
                                        <input
                                            type="text"
                                            name="phone"
                                            className="form-control"
                                            value={addressForm.phone}
                                            onChange={handleAddressFieldChange}
                                            disabled={loading}
                                            placeholder="01XXXXXXXXX"
                                        />
                                    </div>

                                    <div className="col-md-6">
                                        <label className="form-label">Email</label>
                                        <input
                                            type="email"
                                            name="email"
                                            className="form-control"
                                            value={addressForm.email}
                                            onChange={handleAddressFieldChange}
                                            disabled={loading}
                                            placeholder="name@example.com"
                                        />
                                    </div>

                                    <div className="col-md-6">
                                        <label className="form-label">Division</label>
                                        <input
                                            type="text"
                                            name="division"
                                            className="form-control"
                                            value={addressForm.division}
                                            onChange={handleAddressFieldChange}
                                            disabled={loading}
                                            placeholder="Dhaka"
                                        />
                                    </div>

                                    <div className="col-md-6">
                                        <label className="form-label">District</label>
                                        <input
                                            type="text"
                                            name="district"
                                            className="form-control"
                                            value={addressForm.district}
                                            onChange={handleAddressFieldChange}
                                            disabled={loading}
                                            placeholder="Dhaka"
                                        />
                                    </div>

                                    <div className="col-md-6">
                                        <label className="form-label">City</label>
                                        <input
                                            type="text"
                                            name="city"
                                            className="form-control"
                                            value={addressForm.city}
                                            onChange={handleAddressFieldChange}
                                            disabled={loading}
                                            placeholder="Dhaka"
                                        />
                                    </div>

                                    <div className="col-md-6">
                                        <label className="form-label">Area</label>
                                        <input
                                            type="text"
                                            name="area"
                                            className="form-control"
                                            value={addressForm.area}
                                            onChange={handleAddressFieldChange}
                                            disabled={loading}
                                            placeholder="Dhanmondi"
                                        />
                                    </div>

                                    <div className="col-md-6">
                                        <label className="form-label">Postal Code</label>
                                        <input
                                            type="text"
                                            name="postal_code"
                                            className="form-control"
                                            value={addressForm.postal_code}
                                            onChange={handleAddressFieldChange}
                                            disabled={loading}
                                            placeholder="1205"
                                        />
                                    </div>

                                    <div className="col-12">
                                        <label className="form-label">Street Address</label>
                                        <textarea
                                            name="street_address"
                                            className="form-control"
                                            rows="3"
                                            value={addressForm.street_address}
                                            onChange={handleAddressFieldChange}
                                            disabled={loading}
                                            placeholder="House 12, Road 7"
                                        />
                                    </div>

                                    <div className="col-12">
                                        <label className="form-label">Delivery Note (Optional)</label>
                                        <textarea
                                            name="delivery_note"
                                            className="form-control"
                                            rows="2"
                                            value={addressForm.delivery_note}
                                            onChange={handleAddressFieldChange}
                                            disabled={loading}
                                            placeholder="Leave at gate / call before delivery"
                                        />
                                    </div>
                                </div>

                                <div className="mt-3">
                                    <label className="form-label">Legacy Address (Optional backup)</label>
                                    <textarea
                                        className="form-control"
                                        rows="3"
                                        value={shippingAddress}
                                        onChange={(event) => setShippingAddress(event.target.value)}
                                        placeholder="Optional complete shipping address if you prefer legacy text entry"
                                        disabled={loading}
                                    />
                                </div>

                            </div>


                            {/* ==================================
                                PAYMENT METHOD
                            ================================== */}

                            <div className="mb-4">

                                <label
                                    className="form-label"
                                >
                                    Payment Method
                                </label>

                                {/* ==============================
                                    COD
                                ============================== */}

                                <div className="form-check mb-2">

                                    <input
                                        className="form-check-input"
                                        type="radio"
                                        name="paymentMethod"
                                        id="cod"
                                        value="Cash on Delivery"
                                        checked={
                                            paymentMethod
                                            ===
                                            "Cash on Delivery"
                                        }
                                        onChange={(
                                            event
                                        ) =>
                                            setPaymentMethod(
                                                event.target.value
                                            )
                                        }
                                        disabled={loading}
                                    />

                                    <label
                                        className="form-check-label"
                                        htmlFor="cod"
                                    >
                                        Cash on Delivery
                                    </label>

                                </div>


                                {/* ==============================
                                    SSL COMMERZ
                                ============================== */}

                                <div className="form-check">

                                    <input
                                        className="form-check-input"
                                        type="radio"
                                        name="paymentMethod"
                                        id="sslcommerz"
                                        value="SSLCommerz"
                                        checked={
                                            paymentMethod
                                            ===
                                            "SSLCommerz"
                                        }
                                        onChange={(
                                            event
                                        ) =>
                                            setPaymentMethod(
                                                event.target.value
                                            )
                                        }
                                        disabled={loading}
                                    />

                                    <label
                                        className="form-check-label"
                                        htmlFor="sslcommerz"
                                    >
                                        SSLCommerz
                                    </label>

                                </div>

                            </div>


                            {/* ==================================
                                PLACE ORDER BUTTON
                            ================================== */}

                            <button
                                type="button"
                                className="btn btn-primary w-100"
                                onClick={
                                    handlePlaceOrder
                                }
                                disabled={loading}
                            >

                                {loading
                                    ? "Processing..."
                                    : "Place Order"
                                }

                            </button>

                        </div>

                    </div>

                </div>

            </div>

        </div>
    );
};


export default Checkout;