import { useEffect, useState } from "react";
import { getProducts } from "../../services/productService";

const Products = () => {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);

    const [search, setSearch] = useState("");
    const [category, setCategory] = useState("All");
    const [sort, setSort] = useState("default");

    useEffect(() => {
        fetchProducts();
    }, []);

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

    // Search + Category Filter
    let filteredProducts = products.filter((product) => {
        const matchesSearch = product.name
            .toLowerCase()
            .includes(search.toLowerCase());

        const matchesCategory =
            category === "All"
                ? true
                : product.category === category;

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
                                    src={product.image}
                                    alt={product.name}
                                    className="card-img-top"
                                    style={{
                                        height: "230px",
                                        objectFit: "cover",
                                    }}
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
                                        ৳ {product.price}
                                    </h5>

                                    {/* Stock */}
                                    <p className="text-success">
                                        {product.stock
                                            ? product.stock
                                            : "Available"}
                                    </p>

                                    {/* Rating */}
                                    <p>
                                        ⭐ {product.rating || 5}/5
                                    </p>

                                    {/* Buttons */}
                                    <div className="mt-auto">

                                        <button className="btn btn-primary w-100 mb-2">
                                            Add to Cart
                                        </button>

                                        <button className="btn btn-outline-dark w-100">
                                            View Details
                                        </button>

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