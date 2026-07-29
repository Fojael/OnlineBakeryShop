import { useEffect, useState } from "react";
import { getProducts } from "../../services/productService";

const Home = () => {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadProducts();
    }, []);

    const loadProducts = async () => {
        try {
            const response = await getProducts();

            // Display only the first 6 products
            setProducts(response.data.slice(0, 6));
        } catch (error) {
            console.log(error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="container py-5 text-center">
                <h3>Loading Featured Products...</h3>
            </div>
        );
    }

    return (
        <div className="container py-5">

            {/* Featured Products Section */}
            <h2 className="text-center mb-5">
                Featured Bakery Products
            </h2>

            <div className="row">

                {products.length > 0 ? (

                    products.map((product) => (

                        <div
                            className="col-lg-4 col-md-6 mb-4"
                            key={product.id}
                        >
                            <div className="card shadow h-100">

                                {/* Product Image */}
                                <img
                                    src={product.image}
                                    alt={product.name}
                                    className="card-img-top"
                                    style={{
                                        height: "250px",
                                        objectFit: "cover",
                                    }}
                                />

                                <div className="card-body">

                                    <h5 className="card-title">
                                        {product.name}
                                    </h5>

                                    <p className="text-muted">
                                        {product.category}
                                    </p>

                                    <p>
                                        {product.description}
                                    </p>

                                    <h5 className="text-danger">
                                        ৳ {product.price}
                                    </h5>

                                </div>

                                <div className="card-footer bg-white border-0">

                                    <button className="btn btn-primary w-100">
                                        Add to Cart
                                    </button>

                                </div>

                            </div>
                        </div>

                    ))

                ) : (

                    <div className="text-center">
                        <h4>No Featured Products Available.</h4>
                    </div>

                )}

            </div>

        </div>
    );
};

export default Home;