import heroImage from "../../assets/hero.png";

const Home = () => {
    return (
        <div>

            {/* Hero Section */}
            <section className="container py-5">
                <div className="row align-items-center">

                    <div className="col-md-6">
                        <h1 className="display-4 fw-bold">
                            Welcome to Online Bakery Shop
                        </h1>

                        <p className="lead">
                            Freshly baked cakes, cookies, pastries and
                            delicious treats delivered to your doorstep.
                        </p>

                        <button className="btn btn-primary me-3">
                            Shop Now
                        </button>

                        <button className="btn btn-outline-dark">
                            View Products
                        </button>
                    </div>

                    <div className="col-md-6 text-center">
                        <img
                            src={heroImage}
                            alt="Bakery"
                            className="img-fluid rounded shadow"
                        />
                    </div>

                </div>
            </section>


            {/* Featured Products */}
            <section className="container py-5">

                <h2 className="text-center mb-4">
                    Featured Products
                </h2>

                <div className="row">

                    <div className="col-md-3 mb-4">
                        <div className="card h-100 shadow">
                            <img
                                src="https://via.placeholder.com/300"
                                className="card-img-top"
                                alt="Chocolate Cake"
                            />
                            <div className="card-body text-center">
                                <h5>Chocolate Cake</h5>
                                <p>£15.99</p>
                                <button className="btn btn-primary">
                                    Add to Cart
                                </button>
                            </div>
                        </div>
                    </div>


                    <div className="col-md-3 mb-4">
                        <div className="card h-100 shadow">
                            <img
                                src="https://via.placeholder.com/300"
                                className="card-img-top"
                                alt="Cup Cake"
                            />
                            <div className="card-body text-center">
                                <h5>Cup Cake</h5>
                                <p>£5.99</p>
                                <button className="btn btn-primary">
                                    Add to Cart
                                </button>
                            </div>
                        </div>
                    </div>


                    <div className="col-md-3 mb-4">
                        <div className="card h-100 shadow">
                            <img
                                src="https://via.placeholder.com/300"
                                className="card-img-top"
                                alt="Cookies"
                            />
                            <div className="card-body text-center">
                                <h5>Cookies</h5>
                                <p>£7.99</p>
                                <button className="btn btn-primary">
                                    Add to Cart
                                </button>
                            </div>
                        </div>
                    </div>


                    <div className="col-md-3 mb-4">
                        <div className="card h-100 shadow">
                            <img
                                src="https://via.placeholder.com/300"
                                className="card-img-top"
                                alt="Pastry"
                            />
                            <div className="card-body text-center">
                                <h5>Pastry</h5>
                                <p>£6.99</p>
                                <button className="btn btn-primary">
                                    Add to Cart
                                </button>
                            </div>
                        </div>
                    </div>

                </div>
            </section>



            {/* Categories */}
            <section className="bg-light py-5">

                <div className="container">

                    <h2 className="text-center mb-4">
                        Product Categories
                    </h2>

                    <div className="row text-center">

                        <div className="col-md-3 mb-3">
                            <div className="card p-3 shadow">
                                Birthday Cakes
                            </div>
                        </div>

                        <div className="col-md-3 mb-3">
                            <div className="card p-3 shadow">
                                Cup Cakes
                            </div>
                        </div>

                        <div className="col-md-3 mb-3">
                            <div className="card p-3 shadow">
                                Cookies
                            </div>
                        </div>

                        <div className="col-md-3 mb-3">
                            <div className="card p-3 shadow">
                                Bread
                            </div>
                        </div>

                    </div>

                </div>

            </section>



            {/* Best Sellers */}
            <section className="container py-5">

                <h2 className="text-center mb-4">
                    Best Selling Products
                </h2>

                <div className="row text-center">

                    <div className="col-md-4">
                        <h5>Red Velvet Cake</h5>
                    </div>

                    <div className="col-md-4">
                        <h5>Chocolate Brownie</h5>
                    </div>

                    <div className="col-md-4">
                        <h5>Blueberry Muffin</h5>
                    </div>

                </div>

            </section>



            {/* AI Recommendation */}
            <section className="bg-warning-subtle py-5">

                <div className="container text-center">

                    <h2>AI Recommended Products</h2>

                    <p>
                        Our AI system recommends products based on
                        trending bakery items and customer preferences.
                    </p>

                    <h5>
                        Chocolate Muffins • Strawberry Cake • Donuts
                    </h5>

                </div>

            </section>



            {/* Promotional Banner */}
            <section className="container py-5">

                <div className="card bg-danger text-white text-center p-5 shadow">

                    <h2>Special Offer</h2>

                    <h3>20% OFF All Birthday Cakes</h3>

                    <p>Limited Time Offer!</p>

                    <button className="btn btn-light">
                        Order Now
                    </button>

                </div>

            </section>



            {/* Why Choose Us */}
            <section className="bg-light py-5">

                <div className="container">

                    <h2 className="text-center mb-4">
                        Why Choose Us?
                    </h2>

                    <div className="row text-center">

                        <div className="col-md-4">
                            <h5>Freshly Baked Daily</h5>
                        </div>

                        <div className="col-md-4">
                            <h5>Fast Delivery</h5>
                        </div>

                        <div className="col-md-4">
                            <h5>AI Product Recommendations</h5>
                        </div>

                    </div>

                </div>

            </section>



            {/* Customer Reviews */}
            <section className="container py-5">

                <h2 className="text-center mb-4">
                    Customer Reviews
                </h2>

                <div className="row">

                    <div className="col-md-4">
                        <div className="card p-3 shadow">
                            <p>
                                Excellent quality cakes and fast delivery.
                            </p>
                            <h6>- Sarah</h6>
                        </div>
                    </div>

                    <div className="col-md-4">
                        <div className="card p-3 shadow">
                            <p>
                                Best online bakery service I've used.
                            </p>
                            <h6>- Ahmed</h6>
                        </div>
                    </div>

                    <div className="col-md-4">
                        <div className="card p-3 shadow">
                            <p>
                                Delicious pastries and great customer support.
                            </p>
                            <h6>- John</h6>
                        </div>
                    </div>

                </div>

            </section>



            {/* Newsletter */}
            <section className="bg-primary text-white py-5">

                <div className="container text-center">

                    <h2>Subscribe to Our Newsletter</h2>

                    <p>
                        Receive updates on discounts, promotions and new products.
                    </p>

                    <input
                        type="email"
                        placeholder="Enter your email"
                        className="form-control mb-3"
                    />

                    <button className="btn btn-light">
                        Subscribe
                    </button>

                </div>

            </section>



            {/* Footer */}
            <footer className="bg-dark text-white py-4">

                <div className="container text-center">

                    <h5>Online Bakery Shop</h5>

                    <p>Email: support@onlinebakeryshop.com</p>

                    <p>Phone: +8801700000000</p>

                    <p>Dhaka, Bangladesh</p>

                    <p>
                        © 2026 Online Bakery Shop. All Rights Reserved.
                    </p>

                </div>

            </footer>

        </div>
    );
};

export default Home;