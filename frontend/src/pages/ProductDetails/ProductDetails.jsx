import {
    useEffect,
    useState,
} from "react";

import {
    Link,
    useParams,
} from "react-router-dom";

import {
    toast,
} from "react-toastify";

import {
    getProduct,
} from "../../services/productService";


const API_BASE_URL = "http://127.0.0.1:8000";


const ProductDetails = () => {

    const { id } = useParams();


    const [product, setProduct] = useState(null);

    const [loading, setLoading] = useState(true);

    const [quantity, setQuantity] = useState(1);


    // =========================================================
    // PRODUCT IMAGE
    // =========================================================

    const getProductImage = (productData) => {

        if (!productData?.image) {

            return "https://placehold.co/600x500?text=No+Image";

        }


        const image = String(productData.image);


        if (
            image.startsWith("http://") ||
            image.startsWith("https://")
        ) {

            return image;

        }


        return `${API_BASE_URL}${image}`;
    };


    // =========================================================
    // LOAD PRODUCT
    // =========================================================

    useEffect(() => {

        const loadProduct = async () => {

            try {

                setLoading(true);


                const response =
                    await getProduct(id);


                console.log(
                    "Product details:",
                    response.data
                );


                setProduct(response.data);


            } catch (error) {

                console.error(
                    "Failed to load product:",
                    error
                );

                console.error(
                    "Response:",
                    error?.response?.data
                );


                toast.error(
                    error?.response?.data?.detail ||
                    "Unable to load product."
                );


                setProduct(null);


            } finally {

                setLoading(false);

            }
        };


        if (id) {

            loadProduct();

        }

    }, [id]);


    // =========================================================
    // ADD TO CART
    // =========================================================

    const addToCart = async () => {

        try {

            console.log(
                "Product ID:",
                product.id
            );

            console.log(
                "Quantity:",
                quantity
            );


            /*
             * Cart API will be connected here.
             *
             * Example later:
             *
             * await addCartItem({
             *     product: product.id,
             *     quantity: quantity
             * });
             */


            toast.success(
                `${product.name} added to cart.`
            );


        } catch (error) {

            console.error(
                "Failed to add product to cart:",
                error
            );

            toast.error(
                "Unable to add product to cart."
            );

        }
    };


    // =========================================================
    // QUANTITY
    // =========================================================

    const handleQuantityChange = (event) => {

        const value = Number(
            event.target.value
        );


        if (
            Number.isNaN(value) ||
            value < 1
        ) {

            setQuantity(1);

            return;

        }


        if (
            product &&
            product.stock_quantity &&
            value > product.stock_quantity
        ) {

            setQuantity(
                product.stock_quantity
            );

            return;

        }


        setQuantity(value);

    };


    // =========================================================
    // LOADING
    // =========================================================

    if (loading) {

        return (

            <div className="container py-5 text-center">

                <div
                    className="spinner-border text-primary"
                    role="status"
                >
                    <span className="visually-hidden">
                        Loading...
                    </span>
                </div>

                <h4 className="mt-3">
                    Loading Product Details...
                </h4>

            </div>

        );

    }


    // =========================================================
    // PRODUCT NOT FOUND
    // =========================================================

    if (!product) {

        return (

            <div className="container py-5 text-center">

                <h3>
                    Product Not Found
                </h3>

                <p className="text-muted">
                    The requested product could not be found.
                </p>

                <Link
                    to="/products"
                    className="btn btn-primary"
                >
                    Browse Products
                </Link>

            </div>

        );

    }


    const stockQuantity =
        Number(product.stock_quantity || 0);


    const isAvailable =
        product.is_available !== false &&
        stockQuantity > 0;


    // =========================================================
    // PAGE
    // =========================================================

    return (

        <div className="container py-5">

            <div className="row g-5">

                {/* =================================================
                    IMAGE
                ================================================= */}

                <div className="col-md-6">

                    <div className="card shadow-sm border-0">

                        <img
                            src={getProductImage(product)}
                            className="card-img-top"
                            alt={product.name}
                            style={{
                                width: "100%",
                                height: "500px",
                                objectFit: "cover",
                            }}
                            onError={(event) => {
                                event.currentTarget.src =
                                    "https://placehold.co/600x500?text=No+Image";
                            }}
                        />

                    </div>

                </div>


                {/* =================================================
                    PRODUCT INFORMATION
                ================================================= */}

                <div className="col-md-6">

                    <span className="badge bg-secondary mb-3">
                        {product.category || "Bakery"}
                    </span>


                    <h1 className="fw-bold mb-3">
                        {product.name}
                    </h1>


                    <h2 className="text-primary fw-bold mb-4">

                        ৳{" "}

                        {Number(
                            product.price || 0
                        ).toFixed(2)}

                    </h2>


                    {/* DESCRIPTION */}

                    <div className="mb-4">

                        <h5 className="fw-bold">
                            Product Description
                        </h5>

                        <p className="text-muted">
                            {product.description ||
                                "No description available."}
                        </p>

                    </div>


                    {/* STOCK */}

                    <div className="mb-4">

                        <h6 className="fw-bold">
                            Availability
                        </h6>


                        {isAvailable ? (

                            <span className="badge bg-success">
                                In Stock
                            </span>

                        ) : (

                            <span className="badge bg-danger">
                                Out of Stock
                            </span>

                        )}


                        <p className="mt-2 text-muted">

                            Available quantity:{" "}

                            <strong>
                                {stockQuantity}
                            </strong>

                        </p>

                    </div>


                    {/* QUANTITY */}

                    <div className="mb-4">

                        <label
                            htmlFor="quantity"
                            className="form-label fw-semibold"
                        >
                            Quantity
                        </label>


                        <input
                            id="quantity"
                            type="number"
                            className="form-control"
                            style={{
                                width: "130px",
                            }}
                            min="1"
                            max={
                                stockQuantity > 0
                                    ? stockQuantity
                                    : 1
                            }
                            value={quantity}
                            disabled={!isAvailable}
                            onChange={
                                handleQuantityChange
                            }
                        />

                    </div>


                    {/* BUTTONS */}

                    <div className="d-flex flex-wrap gap-2">

                        <button
                            type="button"
                            className="btn btn-primary btn-lg"
                            disabled={!isAvailable}
                            onClick={addToCart}
                        >
                            Add to Cart
                        </button>


                        <button
                            type="button"
                            className="btn btn-success btn-lg"
                            disabled={!isAvailable}
                            onClick={() => {
                                toast.info(
                                    "Buy Now will be connected to the checkout system."
                                );
                            }}
                        >
                            Buy Now
                        </button>


                        <Link
                            to="/products"
                            className="btn btn-outline-secondary btn-lg"
                        >
                            Back to Products
                        </Link>

                    </div>

                </div>

            </div>

        </div>

    );
};


export default ProductDetails;