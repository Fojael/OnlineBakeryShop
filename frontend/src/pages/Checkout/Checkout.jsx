
import { useEffect, useState } from "react";
import {
    useLocation,
    useNavigate,
} from "react-router-dom";
import { toast } from "react-toastify";

import { createOrder } from "../../services/orderService";
import { createPayment } from "../../services/paymentService";
import { getAddresses } from "../../services/addressService";
import { getCart } from "../../services/cartService";

// ============================================================
// INITIAL ADDRESS
// ============================================================

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


// ============================================================
// CHECKOUT
// ============================================================

const Checkout = () => {

    const navigate = useNavigate();

    const location = useLocation();

    const buyNow = location.state?.buyNow;

    const buyNowProductId = Number(
        buyNow?.productId
    );

    const buyNowQuantity = Number(
        buyNow?.quantity
    );

    const isBuyNow =
        Number.isInteger(buyNowProductId) &&
        buyNowProductId > 0 &&
        Number.isInteger(buyNowQuantity) &&
        buyNowQuantity > 0;

    // ========================================================
    // STATE
    // ========================================================

    const [shippingAddress, setShippingAddress] = useState("");

    const [addressForm, setAddressForm] = useState(
        initialAddress
    );
    const [savedAddresses, setSavedAddresses] = useState([]);
    const [selectedAddressId, setSelectedAddressId] = useState("");

    // IMPORTANT:
    // Backend values are:
    // COD
    // SSLCommerz
    const [paymentMethod, setPaymentMethod] = useState("COD");

    const [loading, setLoading] = useState(false);
    const [cartSnapshot, setCartSnapshot] = useState(null);
    const [cartSnapshotError, setCartSnapshotError] = useState("");

    useEffect(() => {
        let mounted = true;
        getAddresses()
            .then((response) => {
                if (mounted) setSavedAddresses(response.data || []);
            })
            .catch(() => {
                if (mounted) setSavedAddresses([]);
            });
        return () => {
            mounted = false;
        };
    }, []);

    useEffect(() => {
        if (isBuyNow) return undefined;
        let mounted = true;
        getCart()
            .then((response) => {
                if (mounted) setCartSnapshot(response.data);
            })
            .catch((error) => {
                if (mounted) {
                    setCartSnapshotError(
                        error.response?.data?.detail ||
                        "Unable to refresh your cart."
                    );
                }
            });
        return () => {
            mounted = false;
        };
    }, [isBuyNow]);

    const selectSavedAddress = (event) => {
        const addressId = event.target.value;
        setSelectedAddressId(addressId);
        const address = savedAddresses.find(
            (item) => String(item.id) === addressId
        );
        if (!address) return;
        setAddressForm({
            full_name: address.full_name || "",
            phone: address.phone || "",
            email: addressForm.email,
            division: address.division || "",
            district: address.district || "",
            city: address.upazila || "",
            area: address.upazila || "",
            street_address: address.address_line || "",
            postal_code: address.postal_code || "",
            delivery_note: "",
        });
        setShippingAddress("");
    };


    // ========================================================
    // ADDRESS FIELD CHANGE
    // ========================================================

    const handleAddressFieldChange = (event) => {

        const {
            name,
            value,
        } = event.target;

        setAddressForm((previous) => ({
            ...previous,
            [name]: value,
        }));

        // Clear legacy address when structured address
        // is being used.
        if (shippingAddress) {
            setShippingAddress("");
        }
    };


    // ========================================================
    // VALIDATE ADDRESS
    // ========================================================

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

            if (
                !String(
                    addressForm[field] || ""
                ).trim()
            ) {

                const fieldName = field
                    .replace(/_/g, " ");

                toast.error(
                    `Please enter your ${fieldName}.`
                );

                return false;
            }
        }


        // ====================================================
        // BANGLADESHI PHONE VALIDATION
        // ====================================================

        if (
            !/^01[3-9]\d{8}$/.test(
                addressForm.phone.trim()
            )
        ) {

            toast.error(
                "Please enter a valid Bangladeshi phone number."
            );

            return false;
        }


        // ====================================================
        // EMAIL VALIDATION
        // ====================================================

        if (
            !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(
                addressForm.email.trim()
            )
        ) {

            toast.error(
                "Please enter a valid email address."
            );

            return false;
        }


        return true;
    };


    // ========================================================
    // BUILD SHIPPING ADDRESS
    // ========================================================

    const buildShippingAddress = () => {

        const addressParts = [
            `Name: ${addressForm.full_name.trim()}`,
            `Phone: ${addressForm.phone.trim()}`,
            `Email: ${addressForm.email.trim()}`,
            `Division: ${addressForm.division.trim()}`,
            `District: ${addressForm.district.trim()}`,
            `City: ${addressForm.city.trim()}`,
            `Area: ${addressForm.area.trim()}`,
            `Street Address: ${addressForm.street_address.trim()}`,
            `Postal Code: ${addressForm.postal_code.trim()}`,
        ];


        if (
            addressForm.delivery_note.trim()
        ) {

            addressParts.push(
                `Delivery Note: ${addressForm.delivery_note.trim()}`
            );
        }


        return addressParts.join(", ");
    };


    // ========================================================
    // PLACE ORDER
    // ========================================================

    const handlePlaceOrder = async () => {

        if (loading) {
            return;
        }


        // ====================================================
        // DETERMINE ADDRESS TYPE
        // ====================================================

        const hasStructuredAddress =
            Object.values(addressForm).some(
                (value) =>
                    String(value || "").trim()
            );


        // ====================================================
        // NO ADDRESS
        // ====================================================

        if (
            !hasStructuredAddress &&
            !shippingAddress.trim()
        ) {

            toast.error(
                "Please enter your shipping address details."
            );

            return;
        }


        // ====================================================
        // VALIDATE STRUCTURED ADDRESS
        // ====================================================

        if (
            hasStructuredAddress &&
            !validateAddress()
        ) {

            return;
        }


        setLoading(true);


        try {

            // =================================================
            // BUILD SHIPPING ADDRESS
            // =================================================

            const finalShippingAddress =
                hasStructuredAddress
                    ? buildShippingAddress()
                    : shippingAddress.trim();


            // =================================================
            // CREATE ORDER PAYLOAD
            // =================================================

            const orderData = {
                shipping_address:
                    finalShippingAddress,

                payment_method:
                    paymentMethod,

                ...(isBuyNow
                    ? {
                        buy_now_product:
                            buyNowProductId,
                        buy_now_quantity:
                            buyNowQuantity,
                    }
                    : {}),
            };


            console.log(
                "Sending order data:",
                orderData
            );


            // =================================================
            // CREATE ORDER
            // =================================================

            const response =
                await createOrder(orderData);


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
                paymentMethod === "COD"
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
                paymentMethod === "SSLCommerz"
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


            const backendError =
                error?.response?.data;


            let backendMessage =
                backendError?.detail ||
                backendError?.message ||
                error?.message ||
                "Could not place order.";


            // =================================================
            // HANDLE FIELD VALIDATION ERRORS
            // =================================================

            if (
                backendError &&
                typeof backendError === "object"
            ) {

                const validationMessages = [];

                Object.entries(
                    backendError
                ).forEach(
                    ([field, messages]) => {

                        if (Array.isArray(messages)) {

                            messages.forEach(
                                (message) => {

                                    validationMessages.push(
                                        `${field}: ${message}`
                                    );
                                }
                            );

                        } else if (
                            typeof messages === "string"
                        ) {

                            validationMessages.push(
                                `${field}: ${messages}`
                            );
                        }
                    }
                );


                if (
                    validationMessages.length > 0
                ) {

                    backendMessage =
                        validationMessages.join(" ");
                }
            }


            toast.error(
                backendMessage.includes("stock") || backendMessage.includes("available")
                    ? `${backendMessage} Please return to your cart and review the updated stock.`
                    : backendMessage
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

                            {cartSnapshotError && (
                                <div className="alert alert-warning">{cartSnapshotError}</div>
                            )}
                            {!isBuyNow && cartSnapshot && (
                                <div className="alert alert-light border mb-4">
                                    <div className="d-flex justify-content-between">
                                        <span>Current cart subtotal</span>
                                        <strong>৳{Number(cartSnapshot.total_amount || 0).toFixed(2)}</strong>
                                    </div>
                                    <small className="text-muted">
                                        Final price, stock, delivery charge, and total are calculated by the server when you place the order.
                                    </small>
                                </div>
                            )}


                            {/* ==================================================
                                SHIPPING ADDRESS
                            ================================================== */}

                            <div className="mb-4">

                                <div className="d-flex justify-content-between align-items-center mb-3">

                                    <h5 className="mb-0">
                                        Shipping Address
                                    </h5>

                                    <small className="text-muted">
                                        Required for delivery
                                    </small>

                                </div>

                                {savedAddresses.length > 0 && (
                                    <div className="mb-3">
                                        <label className="form-label" htmlFor="saved-address">
                                            Use a saved address
                                        </label>
                                        <select
                                            id="saved-address"
                                            className="form-select"
                                            value={selectedAddressId}
                                            onChange={selectSavedAddress}
                                            disabled={loading}
                                        >
                                            <option value="">Enter a new address</option>
                                            {savedAddresses.map((address) => (
                                                <option key={address.id} value={address.id}>
                                                    {address.full_name} - {address.address_line}
                                                    {address.is_default ? " (Default)" : ""}
                                                </option>
                                            ))}
                                        </select>
                                    </div>
                                )}


                                <div className="row g-3">


                                    {/* FULL NAME */}

                                    <div className="col-md-6">

                                        <label className="form-label">
                                            Full Name
                                        </label>

                                        <input
                                            type="text"
                                            name="full_name"
                                            className="form-control"
                                            value={
                                                addressForm.full_name
                                            }
                                            onChange={
                                                handleAddressFieldChange
                                            }
                                            disabled={loading}
                                            placeholder="Enter full name"
                                        />

                                    </div>


                                    {/* PHONE */}

                                    <div className="col-md-6">

                                        <label className="form-label">
                                            Phone
                                        </label>

                                        <input
                                            type="text"
                                            name="phone"
                                            className="form-control"
                                            value={
                                                addressForm.phone
                                            }
                                            onChange={
                                                handleAddressFieldChange
                                            }
                                            disabled={loading}
                                            placeholder="01XXXXXXXXX"
                                        />

                                    </div>


                                    {/* EMAIL */}

                                    <div className="col-md-6">

                                        <label className="form-label">
                                            Email
                                        </label>

                                        <input
                                            type="email"
                                            name="email"
                                            className="form-control"
                                            value={
                                                addressForm.email
                                            }
                                            onChange={
                                                handleAddressFieldChange
                                            }
                                            disabled={loading}
                                            placeholder="name@example.com"
                                        />

                                    </div>


                                    {/* DIVISION */}

                                    <div className="col-md-6">

                                        <label className="form-label">
                                            Division
                                        </label>

                                        <input
                                            type="text"
                                            name="division"
                                            className="form-control"
                                            value={
                                                addressForm.division
                                            }
                                            onChange={
                                                handleAddressFieldChange
                                            }
                                            disabled={loading}
                                            placeholder="Dhaka"
                                        />

                                    </div>


                                    {/* DISTRICT */}

                                    <div className="col-md-6">

                                        <label className="form-label">
                                            District
                                        </label>

                                        <input
                                            type="text"
                                            name="district"
                                            className="form-control"
                                            value={
                                                addressForm.district
                                            }
                                            onChange={
                                                handleAddressFieldChange
                                            }
                                            disabled={loading}
                                            placeholder="Dhaka"
                                        />

                                    </div>


                                    {/* CITY */}

                                    <div className="col-md-6">

                                        <label className="form-label">
                                            City
                                        </label>

                                        <input
                                            type="text"
                                            name="city"
                                            className="form-control"
                                            value={
                                                addressForm.city
                                            }
                                            onChange={
                                                handleAddressFieldChange
                                            }
                                            disabled={loading}
                                            placeholder="Dhaka"
                                        />

                                    </div>


                                    {/* AREA */}

                                    <div className="col-md-6">

                                        <label className="form-label">
                                            Area
                                        </label>

                                        <input
                                            type="text"
                                            name="area"
                                            className="form-control"
                                            value={
                                                addressForm.area
                                            }
                                            onChange={
                                                handleAddressFieldChange
                                            }
                                            disabled={loading}
                                            placeholder="Dhanmondi"
                                        />

                                    </div>


                                    {/* POSTAL CODE */}

                                    <div className="col-md-6">

                                        <label className="form-label">
                                            Postal Code
                                        </label>

                                        <input
                                            type="text"
                                            name="postal_code"
                                            className="form-control"
                                            value={
                                                addressForm.postal_code
                                            }
                                            onChange={
                                                handleAddressFieldChange
                                            }
                                            disabled={loading}
                                            placeholder="1205"
                                        />

                                    </div>


                                    {/* STREET ADDRESS */}

                                    <div className="col-12">

                                        <label className="form-label">
                                            Street Address
                                        </label>

                                        <textarea
                                            name="street_address"
                                            className="form-control"
                                            rows="3"
                                            value={
                                                addressForm.street_address
                                            }
                                            onChange={
                                                handleAddressFieldChange
                                            }
                                            disabled={loading}
                                            placeholder="House 12, Road 7"
                                        />

                                    </div>


                                    {/* DELIVERY NOTE */}

                                    <div className="col-12">

                                        <label className="form-label">
                                            Delivery Note (Optional)
                                        </label>

                                        <textarea
                                            name="delivery_note"
                                            className="form-control"
                                            rows="2"
                                            value={
                                                addressForm.delivery_note
                                            }
                                            onChange={
                                                handleAddressFieldChange
                                            }
                                            disabled={loading}
                                            placeholder="Leave at gate / call before delivery"
                                        />

                                    </div>

                                </div>


                                {/* ==================================================
                                    LEGACY ADDRESS
                                ================================================== */}

                                <div className="mt-3">

                                    <label className="form-label">
                                        Legacy Address (Optional Backup)
                                    </label>

                                    <textarea
                                        className="form-control"
                                        rows="3"
                                        value={
                                            shippingAddress
                                        }
                                        onChange={(event) =>
                                            setShippingAddress(
                                                event.target.value
                                            )
                                        }
                                        placeholder="Optional complete shipping address"
                                        disabled={loading}
                                    />

                                </div>

                            </div>


                            {/* ==================================================
                                PAYMENT METHOD
                            ================================================== */}

                            <div className="mb-4">

                                <label className="form-label">
                                    Payment Method
                                </label>


                                {/* ==================================================
                                    CASH ON DELIVERY
                                ================================================== */}

                                <div className="form-check mb-2">

                                    <input
                                        className="form-check-input"
                                        type="radio"
                                        name="paymentMethod"
                                        id="cod"
                                        value="COD"
                                        checked={
                                            paymentMethod === "COD"
                                        }
                                        onChange={(event) =>
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


                                {/* ==================================================
                                    SSLCOMMERZ
                                ================================================== */}

                                <div className="form-check">

                                    <input
                                        className="form-check-input"
                                        type="radio"
                                        name="paymentMethod"
                                        id="sslcommerz"
                                        value="SSLCommerz"
                                        checked={
                                            paymentMethod ===
                                            "SSLCommerz"
                                        }
                                        onChange={(event) =>
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


                            {/* ==================================================
                                PLACE ORDER
                            ================================================== */}

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
