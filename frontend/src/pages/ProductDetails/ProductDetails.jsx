import { useState } from "react";

const ProductDetails = () => {
    const [quantity, setQuantity] = useState(1);

    const product = {
        id: 1,
        name: "Chocolate Cake",
        image: "https://via.placeholder.com/600x400",
        description:
            "Our delicious Chocolate Cake is freshly baked using premium cocoa and topped with rich chocolate frosting. Perfect for birthdays, celebrations, and everyday treats.",
        price: 15.99,
        stock: 25,
        category: "Cake",
        rating: 4.8,
    };

    const reviews = [
        {
            id: 1,
            name: "Sarah",
            rating: 5,
            comment: "Absolutely delicious! Highly recommended.",
        },
        {
            id: 2,
            name: "Ahmed",
            rating: 4,
            comment: "Fresh and tasty. Delivery was very fast.",
        },
        {
            id: 3,
            name: "John",
            rating: 5,
            comment: "One of the best chocolate cakes I've ever had.",
        },
    ];

    return (
        <div className="container py-5">
            <div className="row">

                {/* Product Image */}
                <div className="col-md-6 mb-4">
                    <img
                        src={product.image}
                        alt={product.name}
                        className="img-fluid rounded shadow"
                    />
                </div>

                {/* Product Information */}
                <div className="col-md-6">

                    <h1 className="mb-3">
                        {product.name}
                    </h1>

                    <p className="text-muted">
                        Category: {product.category}
                    </p>

                    <h3 className="text-success mb-3">
                        £{product.price}
                    </h3>

                    <p>
                        Rating: {product.rating} / 5
                    </p>

                    <p>
                        <strong>Stock:</strong>{" "}
                        {product.stock > 0
                            ? `${product.stock} Available`
                            : "Out of Stock"}
                    </p>

                    <hr />

                    <h5>Description</h5>

                    <p>
                        {product.description}
                    </p>

                    <hr />

                    {/* Quantity */}
                    <div className="mb-3">

                        <label className="form-label">
                            Quantity
                        </label>

                        <input
                            type="number"
                            min="1"
                            value={quantity}
                            onChange={(e) =>
                                setQuantity(e.target.value)
                            }
                            className="form-control"
                            style={{ width: "120px" }}
                        />

                    </div>

                    {/* Buttons */}
                    <button className="btn btn-primary me-3">
                        Add to Cart
                    </button>

                    <button className="btn btn-success">
                        Buy Now
                    </button>

                </div>
            </div>

            {/* Customer Reviews */}
            <div className="mt-5">

                <h2 className="mb-4">
                    Customer Reviews
                </h2>

                <div className="row">

                    {reviews.map((review) => (
                        <div
                            className="col-md-4 mb-4"
                            key={review.id}
                        >
                            <div className="card shadow h-100">

                                <div className="card-body">

                                    <h5>
                                        {review.name}
                                    </h5>

                                    <p>
                                        Rating: {review.rating} / 5
                                    </p>

                                    <p>
                                        {review.comment}
                                    </p>

                                </div>

                            </div>
                        </div>
                    ))}

                </div>
            </div>

            {/* Related Products */}
            <div className="mt-5">

                <h2 className="mb-4">
                    You May Also Like
                </h2>

                <div className="row">

                    <div className="col-md-4 mb-3">
                        <div className="card shadow">

                            <img
                                src="https://via.placeholder.com/300"
                                className="card-img-top"
                                alt="Cup Cake"
                            />

                            <div className="card-body text-center">
                                <h5>Cup Cake</h5>
                                <p>£4.99</p>
                            </div>

                        </div>
                    </div>

                    <div className="col-md-4 mb-3">
                        <div className="card shadow">

                            <img
                                src="https://via.placeholder.com/300"
                                className="card-img-top"
                                alt="Cookies"
                            />

                            <div className="card-body text-center">
                                <h5>Cookies</h5>
                                <p>£6.99</p>
                            </div>

                        </div>
                    </div>

                    <div className="col-md-4 mb-3">
                        <div className="card shadow">

                            <img
                                src="https://via.placeholder.com/300"
                                className="card-img-top"
                                alt="Brownie"
                            />

                            <div className="card-body text-center">
                                <h5>Brownie</h5>
                                <p>£5.99</p>
                            </div>

                        </div>
                    </div>

                </div>

            </div>
        </div>
    );
};

export default ProductDetails;