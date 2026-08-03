import { useEffect, useState } from "react";
import { getProducts } from "../../services/productService";
import { Link } from "react-router-dom";

const Products = () => {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);

    const [search, setSearch] = useState("");
    const [category, setCategory] = useState("All");
    const [sort, setSort] = useState("default");
    const addToCart = async (productId, quantity) => {
    try {
        console.log("Product:", productId);
        console.log("Quantity:", quantity);

        // Later call Cart API

        alert("Product added to cart!");
    } catch (error) {
        console.log(error);
    }
};

    useEffect(() => {
        const fetchProducts = async () => {
            try {
                const response = await getProducts();
                setProducts(response.data);
            } catch (error) {
                console.log(error);
            } finally {
                setLoading(false);
            }
        };

        fetchProducts();
    }, []);

    // Search + Category Filter
    let filteredProducts = products.filter((product) => {
        const matchesSearch = product.name
            .toLowerCase()
            .includes(search.toLowerCase());

        const matchesCategory =
            category === "All"
                ? true
                : product.category.toLowerCase() === category.toLowerCase()

        return matchesSearch && matchesCategory;
    });

    // Sort Products
    if (sort === "lowToHigh") {
        filteredProducts.sort(
            (a, b) => Number(a.price) - Number(b.price)
        );
    }

    if (sort === "highToLow") {
        filteredProducts.sort(
            (a, b) => Number(b.price) - Number(a.price)
        );
    }

    // Loading State
    if (loading) {
        return (
            <div className="container py-5 text-center">
                <h3>Loading Products...</h3>
            </div>
        );
    }

    return (
        <div className="container py-5">

            {/* Page Title */}
            <h1 className="text-center mb-5">
                Our Fresh Bakery Collection
            </h1>

            {/* Search + Filter Section */}
            <div className="row mb-4">

                {/* Search */}
                <div className="col-md-4 mb-3">
                    <input
                        type="text"
                        className="form-control"
                        placeholder="Search Bakery Products..."
                        value={search}
                        onChange={(e) =>
                            setSearch(e.target.value)
                        }
                    />
                </div>

                {/* Category */}
                <div className="col-md-4 mb-3">
                    <select
                        className="form-select"
                        value={category}
                        onChange={(e) =>
                            setCategory(e.target.value)
                        }
                    >
                        <option value="All">
                            All Categories
                        </option>

                        <option value="Cake">
                            Cake
                        </option>

                        <option value="Pastry">
                            Pastry
                        </option>

                        <option value="Cookies">
                            Cookies
                        </option>

                        <option value="Bread">
                            Bread
                        </option>

                        <option value="Donut">
                            Donut
                        </option>

                        <option value="Muffin">
                            Muffin
                        </option>

                        <option value="Cup Cake">
                            Cup Cake
                        </option>

                    </select>
                </div>

                {/* Sorting */}
                <div className="col-md-4 mb-3">
                    <select
                        className="form-select"
                        value={sort}
                        onChange={(e) =>
                            setSort(e.target.value)
                        }
                    >
                        <option value="default">
                            Sort Products
                        </option>

                        <option value="lowToHigh">
                            Price: Low to High
                        </option>

                        <option value="highToLow">
                            Price: High to Low
                        </option>
                    </select>
                </div>

            </div>

            {/* Product Cards */}
            <div className="row">

                {filteredProducts.length > 0 ? (

                    filteredProducts.map((product) => (

                        <div
                            className="col-lg-3 col-md-4 col-sm-6 mb-4"
                            key={product.id}
                        >
                            <div className="card shadow h-100">

                                {/* Product Image */}
                                <img
                                   src={
                                        product.image
                                       ? product.image
                                       : "https://placehold.co/300x300?text=No+Image"
                                         }
                                      alt={product.name}
                                />

                                <div className="card-body d-flex flex-column">

                                    {/* Product Name */}
                                    <h5 className="card-title">
                                        {product.name}
                                    </h5>

                                    {/* Category */}
                                    <p className="text-muted mb-1">
                                        {product.category}
                                    </p>

                                    {/* Description */}
                                    <p
                                        className="card-text"
                                        style={{
                                            minHeight: "50px",
                                        }}
                                    >
                                        {product.description}
                                    </p>

                                    {/* Price */}
                                    <h5 className="text-danger mb-2">
                                       ৳ {Number(product.price).toFixed(2)}
                                    </h5>

                                    {/* Stock */}
                                    <p
    className={
        product.stock_quantity > 0
            ? "text-success"
            : "text-danger"
    }
>
    {product.stock_quantity > 0
        ? `${product.stock_quantity} Available`
        : "Out of Stock"}
</p>

                                    {/* Rating */}
                                    <p>
                                        ⭐ {product.rating || 5}/5
                                    </p>

                                    {/* Buttons */}
                                   <div className="mt-auto">

                                  <button
                                         className="btn btn-primary w-100 mb-2"
                                           onClick={() => addToCart(product.id, 1)}
                                    >
                                               Add to Cart
                                   </button>

                                   <Link
                                      to={`/products/${product.id}`}
                                       className="btn btn-outline-dark w-100"
                                        >
                                          View Details
                                   </Link>

                                             </div>

                                </div>
                            </div>
                        </div>

                    ))

                ) : (

                    <div className="text-center">
                        <h4>No Products Found.</h4>
                    </div>

                )}

            </div>

        </div>
    );
};

export default Products;