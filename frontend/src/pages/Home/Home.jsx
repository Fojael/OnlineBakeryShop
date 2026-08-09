import {
    useEffect,
    useState,
} from "react";

import {
    Link,
} from "react-router-dom";

import {
    toast,
} from "react-toastify";

import {
    getProducts,
} from "../../services/productService";


const Home = () => {

    const [products, setProducts] = useState([]);

    const [loading, setLoading] = useState(true);


    // =========================================================
    // LOAD PRODUCTS
    // =========================================================

    useEffect(() => {

        const loadProducts = async () => {

            try {

                const response =
                    await getProducts();

                console.log(
                    "Products API response:",
                    response.data
                );


                // -------------------------------------------------
                // Make sure response is an array
                // -------------------------------------------------

                if (Array.isArray(response.data)) {

                    setProducts(
                        response.data
                            .filter(
                                (product) =>
                                    product.is_available !== false
                            )
                            .slice(0, 6)
                    );

                } else {

                    console.error(
                        "Unexpected products response:",
                        response.data
                    );

                    setProducts([]);

                    toast.error(
                        "Invalid product data received."
                    );
                }

            } catch (error) {

                console.error(
                    "Failed to load products:",
                    error
                );

                console.error(
                    "API URL:",
                    error.config?.url
                );

                console.error(
                    "API response:",
                    error.response?.data
                );

                toast.error(
                    "Unable to load products."
                );

                setProducts([]);

            } finally {

                setLoading(false);

            }
        };


        loadProducts();

    }, []);


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

                <h5 className="mt-3">
                    Loading Products...
                </h5>

            </div>
        );
    }


    // =========================================================
    // HOME PAGE
    // =========================================================

    return (

        <div>


            {/* =================================================
                HERO SECTION
            ================================================= */}

            <section className="bg-light py-5">

                <div className="container">

                    <div className="row align-items-center">

                        {/* LEFT */}

                        <div className="col-lg-6">

                            <h1 className="display-3 fw-bold">

                                Fresh Bakery
                                <br />

                                Products
                                <br />

                                Delivered to Your Door

                            </h1>


                            <p className="lead mt-4">

                                Discover fresh cakes,
                                breads, pastries,
                                cookies and other
                                delicious bakery products.

                            </p>


                            <div className="d-flex gap-2 mt-4">

                                <Link
                                    to="/products"
                                    className="btn btn-primary btn-lg"
                                >
                                    Explore Products
                                </Link>


                                <Link
                                    to="/register"
                                    className="btn btn-outline-primary btn-lg"
                                >
                                    Create Account
                                </Link>


                                <Link
                                    to="/login"
                                    className="btn btn-outline-dark btn-lg"
                                >
                                    Login
                                </Link>

                            </div>

                        </div>


                        {/* RIGHT */}

                        <div className="col-lg-6 mt-4 mt-lg-0">

                            <div className="card shadow border-0">

                                <div className="card-body text-center py-5">

                                    <h2 className="fw-bold">
                                        BakeMaster AI
                                    </h2>

                                    <p className="lead text-muted">
                                        Smart Bakery Management
                                        & Online Ordering
                                    </p>

                                </div>

                            </div>

                        </div>

                    </div>

                </div>

            </section>


            {/* =================================================
                FEATURED PRODUCTS
            ================================================= */}

            <section className="py-5">

                <div className="container">

                    <div className="text-center mb-5">

                        <h2 className="fw-bold">
                            Featured Bakery Products
                        </h2>

                        <p className="text-muted">
                            Discover some of our available
                            bakery products.
                        </p>

                    </div>


                    {/* =================================================
                        PRODUCTS EXIST
                    ================================================= */}

                    {products.length > 0 ? (

                        <div className="row">

                            {products.map(
                                (product) => (

                                    <div
                                        className="col-lg-4 col-md-6 mb-4"
                                        key={product.id}
                                    >

                                        <div className="card shadow-sm h-100">


                                            {/* IMAGE */}

                                            <img
                                                src={
                                                    product.image ||
                                                    "https://placehold.co/600x400?text=Bakery+Product"
                                                }
                                                className="card-img-top"
                                                alt={product.name}
                                                style={{
                                                    height: "250px",
                                                    objectFit: "cover",
                                                }}
                                            />


                                            {/* BODY */}

                                            <div className="card-body">

                                                <h5 className="card-title fw-bold">
                                                    {product.name}
                                                </h5>


                                                <span className="badge bg-secondary mb-2">
                                                    {product.category}
                                                </span>


                                                <p className="text-muted">

                                                    {product.description}

                                                </p>


                                                <h5 className="text-primary fw-bold">

                                                    ৳{" "}
                                                    {Number(
                                                        product.price
                                                    ).toFixed(2)}

                                                </h5>

                                            </div>


                                            {/* FOOTER */}

                                            <div className="card-footer bg-white border-0 pb-3">

                                                <Link
                                                    to={`/products/${product.id}`}
                                                    className="btn btn-primary w-100"
                                                >
                                                    View Product
                                                </Link>

                                            </div>

                                        </div>

                                    </div>

                                )
                            )}

                        </div>

                    ) : (

                        /* =================================================
                           NO PRODUCTS
                        ================================================= */

                        <div className="text-center py-5">

                            <h4>
                                No Featured Products Available
                            </h4>

                            <p className="text-muted">
                                Please check back later.
                            </p>


                            <Link
                                to="/products"
                                className="btn btn-primary"
                            >
                                Browse Products
                            </Link>

                        </div>

                    )}

                </div>

            </section>

        </div>
    );
};


export default Home;