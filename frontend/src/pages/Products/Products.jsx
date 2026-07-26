import { useState } from "react";

const Products = () => {
    const [search, setSearch] = useState("");
    const [category, setCategory] = useState("All");
    const [sort, setSort] = useState("default");

    const products = [
        {
            id: 1,
            name: "Chocolate Cake",
            category: "Cake",
            price: 15.99,
            image: "https://via.placeholder.com/300",
            rating: 5,
            stock: "In Stock",
        },
        {
            id: 2,
            name: "Red Velvet Cake",
            category: "Cake",
            price: 18.99,
            image: "https://via.placeholder.com/300",
            rating: 5,
            stock: "In Stock",
        },
        {
            id: 3,
            name: "Cup Cake",
            category: "Cup Cake",
            price: 4.99,
            image: "https://via.placeholder.com/300",
            rating: 4,
            stock: "In Stock",
        },
        {
            id: 4,
            name: "Cookies",
            category: "Cookies",
            price: 6.99,
            image: "https://via.placeholder.com/300",
            rating: 4,
            stock: "In Stock",
        },
        {
            id: 5,
            name: "Donut",
            category: "Donut",
            price: 3.99,
            image: "https://via.placeholder.com/300",
            rating: 5,
            stock: "In Stock",
        },
        {
            id: 6,
            name: "Brownie",
            category: "Brownie",
            price: 5.99,
            image: "https://via.placeholder.com/300",
            rating: 5,
            stock: "In Stock",
        },
        {
            id: 7,
            name: "Croissant",
            category: "Pastry",
            price: 4.49,
            image: "https://via.placeholder.com/300",
            rating: 4,
            stock: "In Stock",
        },
        {
            id: 8,
            name: "Blueberry Muffin",
            category: "Muffin",
            price: 4.99,
            image: "https://via.placeholder.com/300",
            rating: 5,
            stock: "In Stock",
        },
    ];

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

    if (sort === "lowToHigh") {
        filteredProducts.sort((a, b) => a.price - b.price);
    }

    if (sort === "highToLow") {
        filteredProducts.sort((a, b) => b.price - a.price);
    }

    return (
        <div className="container py-5">
            {/* Page Title */}
            <h1 className="text-center mb-5">
                Bakery Products
            </h1>

            {/* Search and Filters */}
            <div className="row mb-4">

                {/* Search */}
                <div className="col-md-4 mb-3">
                    <input
                        type="text"
                        className="form-control"
                        placeholder="Search products..."
                        value={search}
                        onChange={(e) =>
                            setSearch(e.target.value)
                        }
                    />
                </div>

                {/* Category Filter */}
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
                            Cakes
                        </option>

                        <option value="Cup Cake">
                            Cup Cakes
                        </option>

                        <option value="Cookies">
                            Cookies
                        </option>

                        <option value="Donut">
                            Donuts
                        </option>

                        <option value="Brownie">
                            Brownies
                        </option>

                        <option value="Pastry">
                            Pastries
                        </option>

                        <option value="Muffin">
                            Muffins
                        </option>
                    </select>
                </div>

                {/* Sort */}
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

            {/* Products Grid */}
            <div className="row">

                {filteredProducts.length === 0 ? (
                    <div className="text-center">
                        <h4>No products found.</h4>
                    </div>
                ) : (
                    filteredProducts.map((product) => (
                        <div
                            className="col-md-3 mb-4"
                            key={product.id}
                        >
                            <div className="card shadow h-100">

                                <img
                                    src={product.image}
                                    alt={product.name}
                                    className="card-img-top"
                                />

                                <div className="card-body text-center">

                                    <h5>
                                        {product.name}
                                    </h5>

                                    <p>
                                        Category:
                                        {" "}
                                        {product.category}
                                    </p>

                                    <p>
                                        <strong>
                                            £
                                            {product.price}
                                        </strong>
                                    </p>

                                    <p>
                                        Rating:
                                        {" "}
                                        {product.rating}
                                        /5
                                    </p>

                                    <p>
                                        {product.stock}
                                    </p>

                                    <button className="btn btn-primary me-2">
                                        Add to Cart
                                    </button>

                                    <button className="btn btn-outline-dark">
                                        Details
                                    </button>

                                </div>

                            </div>
                        </div>
                    ))
                )}

            </div>

            {/* Pagination */}
            <div className="d-flex justify-content-center mt-4">

                <nav>
                    <ul className="pagination">

                        <li className="page-item">
                            <button className="page-link">
                                Previous
                            </button>
                        </li>

                        <li className="page-item active">
                            <button className="page-link">
                                1
                            </button>
                        </li>

                        <li className="page-item">
                            <button className="page-link">
                                2
                            </button>
                        </li>

                        <li className="page-item">
                            <button className="page-link">
                                3
                            </button>
                        </li>

                        <li className="page-item">
                            <button className="page-link">
                                Next
                            </button>
                        </li>

                    </ul>
                </nav>

            </div>
        </div>
    );
};

export default Products;