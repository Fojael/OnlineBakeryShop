import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getProduct } from "../../services/productService";

const ProductDetails = () => {
    const { id } = useParams();

    const [product, setProduct] = useState(null);
    const [loading, setLoading] = useState(true);
    const [quantity, setQuantity] = useState(1);
    const addToCart = async (productId, quantity) => {
    try {
        console.log("Product:", productId);
        console.log("Quantity:", quantity);

        // Later you will call the Cart API here

        alert("Product added to cart!");
    } catch (error) {
        console.log(error);
    }
};

    useEffect(() => {
        const loadProduct = async () => {
            try {
                const response = await getProduct(id);

                setProduct(response.data);
            } catch (error) {
                console.log(error);
            } finally {
                setLoading(false);
            }
        };

        loadProduct();
    }, [id]);
    
    // Loading State
    if (loading) {
        return (
            <div className="container py-5 text-center">
                <h3>Loading Product Details...</h3>
            </div>
        );
    }

    // Product Not Found
    if (!product) {
        return (
            <div className="container py-5 text-center">
                <h3>Product Not Found.</h3>
            </div>
        );
    }

    return (
        <div className="container py-5">

            <div className="row">

                {/* Product Image */}
                <div className="col-md-6">

                    <img
                        src={
                        product.image
                      ? product.image
                      : "https://placehold.co/300x300?text=No+Image"
                      }
                    alt={product.name}
                   />

                </div>

                {/* Product Information */}
                <div className="col-md-6">

                    {/* Product Name */}
                    <h1 className="mb-3">
                        {product.name}
                    </h1>

                    {/* Category */}
                    <h5 className="text-muted">
                       {product.category}
                    </h5>

                    {/* Price */}
                    <h3 className="text-danger my-3">
                        ৳ {Number(product.price).toFixed(2)}
                    </h3>

                    {/* Stock Status */}
                    <p>
                        <strong>Availability:</strong>{" "}
                       {product.stock_quantity > 0
                               ? `${product.stock_quantity} Available`
                               : "Out of Stock"}
                    </p>

                    {/* Stock Quantity */}
                    <p>
                        <strong>Stock:</strong>{" "}
                        {product.stock_quantity}
                    </p>

                    {/* Description */}
                    <h5 className="mt-4">
                        Product Description
                    </h5>

                    <p>
                        {product.description}
                    </p>

                    {/* Quantity */}
                    <div className="mb-4">

                        <label className="form-label">
                            Quantity
                        </label>

                        <input
                            type="number"
                            min="1"
                            value={quantity}
                            className="form-control"
                            style={{ width: "120px" }}
                            onChange={(e) =>
                                setQuantity(e.target.value)
                            }
                        />

                    </div>

                    {/* Buttons */}
                    <div className="d-flex gap-3">

                        <button
                        className="btn btn-primary"
                     disabled={!product.is_available}
                      onClick={() => addToCart(product.id, quantity)}
                      >
                        Add to Cart
                      </button>

                        <button
                            className="btn btn-success"
                            disabled={!product.is_available}
                        >
                            Buy Now
                        </button>

                    </div>

                </div>

            </div>

        </div>
    );
};

export default ProductDetails;