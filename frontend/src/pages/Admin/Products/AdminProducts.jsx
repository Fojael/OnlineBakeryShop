import {
    useCallback,
    useEffect,
    useMemo,
    useState,
} from "react";

import {
    Link,
} from "react-router-dom";

import {
    toast,
} from "react-toastify";

import DashboardLayout from "../../../layouts/DashboardLayout";

import {
    getProducts,
    deleteProduct,
} from "../../../services/productService";


const AdminProducts = () => {

    // =========================================================
    // STATE
    // =========================================================

    const [products, setProducts] = useState([]);

    const [loading, setLoading] = useState(true);

    const [search, setSearch] = useState("");


    // =========================================================
    // FETCH PRODUCTS
    // =========================================================

    const fetchProducts = useCallback(async () => {

        try {

            setLoading(true);

            const response = await getProducts();

            const data = response.data;

            /*
             * Django REST Framework normally returns
             * an array when pagination is disabled.
             *
             * If pagination is enabled, products may be
             * inside data.results.
             */

            if (Array.isArray(data)) {

                setProducts(data);

            } else if (
                data &&
                Array.isArray(data.results)
            ) {

                setProducts(data.results);

            } else {

                setProducts([]);

            }

        } catch (error) {

            console.error(
                "Failed to load products:",
                error
            );

            toast.error(
                error?.response?.data?.detail ||
                "Unable to load products."
            );

            setProducts([]);

        } finally {

            setLoading(false);

        }

    }, []);


    // =========================================================
    // LOAD PRODUCTS
    // =========================================================

    useEffect(() => {

        const timer = window.setTimeout(() => {

            void fetchProducts();

        }, 0);

        return () => {

            window.clearTimeout(timer);

        };

    }, [fetchProducts]);


    // =========================================================
    // DELETE PRODUCT
    // =========================================================

    const handleDelete = async (id) => {

        const confirmed = window.confirm(
            "Are you sure you want to delete this product?"
        );

        if (!confirmed) {
            return;
        }

        try {

            await deleteProduct(id);

            toast.success(
                "Product deleted successfully."
            );

            await fetchProducts();

        } catch (error) {

            console.error(
                "Failed to delete product:",
                error
            );

            toast.error(
                error?.response?.data?.detail ||
                "Failed to delete product."
            );

        }

    };


    // =========================================================
    // SEARCH PRODUCTS
    // =========================================================

    const filteredProducts = useMemo(() => {

        const keyword = search
            .trim()
            .toLowerCase();

        if (!keyword) {

            return products;

        }

        return products.filter((product) => {

            const name = String(
                product.name || ""
            ).toLowerCase();

            const category = String(
                product.category_name ||
                product.category?.name ||
                ""
            ).toLowerCase();

            const price = String(
                product.price || ""
            ).toLowerCase();

            const description = String(
                product.description || ""
            ).toLowerCase();

            return (
                name.includes(keyword) ||
                category.includes(keyword) ||
                price.includes(keyword) ||
                description.includes(keyword)
            );

        });

    }, [
        products,
        search,
    ]);


    // =========================================================
    // PRODUCT IMAGE
    // =========================================================

    const getProductImage = (product) => {

        if (!product.image) {

            return null;

        }

        if (
            String(product.image).startsWith("http")
        ) {

            return product.image;

        }

        return `http://127.0.0.1:8000${product.image}`;

    };


    // =========================================================
    // FORMAT PRICE
    // =========================================================

    const formatPrice = (price) => {

        const value = Number(price);

        if (Number.isNaN(value)) {

            return "0.00";

        }

        return value.toFixed(2);

    };


    // =========================================================
    // LOADING
    // =========================================================

    if (loading) {

        return (

            <DashboardLayout>

                <div className="container-fluid py-5 text-center">

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

            </DashboardLayout>

        );

    }


    // =========================================================
    // PAGE
    // =========================================================

    return (

        <DashboardLayout>

            <div className="container-fluid py-4">

                {/* =================================================
                    HEADER
                ================================================= */}

                <div
                    className="
                        d-flex
                        flex-column
                        flex-md-row
                        justify-content-between
                        align-items-md-center
                        gap-3
                        mb-4
                    "
                >

                    <div>

                        <h2 className="mb-1">
                            Product Management
                        </h2>

                        <p className="text-muted mb-0">
                            Manage all bakery products.
                        </p>

                    </div>


                    <div className="d-flex gap-2">

                        <button
                            type="button"
                            className="btn btn-primary"
                            onClick={fetchProducts}
                        >
                            Refresh Products
                        </button>


                        <Link
                            to="/admin/products/add"
                            className="btn btn-success"
                        >
                            Add Product
                        </Link>

                    </div>

                </div>


                {/* =================================================
                    SEARCH
                ================================================= */}

                <div className="card shadow-sm mb-4">

                    <div className="card-body">

                        <div className="row align-items-end">

                            <div className="col-md-6">

                                <label
                                    htmlFor="productSearch"
                                    className="form-label fw-semibold"
                                >
                                    Search Products
                                </label>

                                <input
                                    id="productSearch"
                                    type="text"
                                    className="form-control"
                                    placeholder="
                                        Search by product name,
                                        category or price...
                                    "
                                    value={search}
                                    onChange={(event) =>
                                        setSearch(
                                            event.target.value
                                        )
                                    }
                                />

                            </div>


                            <div className="col-md-6 mt-3 mt-md-0">

                                <div className="text-md-end">

                                    <span className="text-muted">
                                        Total Products:{" "}
                                    </span>

                                    <strong>
                                        {
                                            filteredProducts.length
                                        }
                                    </strong>

                                </div>

                            </div>

                        </div>

                    </div>

                </div>


                {/* =================================================
                    PRODUCTS TABLE
                ================================================= */}

                <div className="card shadow">

                    <div className="card-header bg-primary text-white">

                        <h4 className="mb-0">
                            All Products
                        </h4>

                    </div>


                    <div className="card-body p-0">

                        <div className="table-responsive">

                            <table
                                className="
                                    table
                                    table-bordered
                                    table-hover
                                    align-middle
                                    mb-0
                                "
                            >

                                <thead className="table-dark">

                                    <tr>

                                        <th>
                                            Image
                                        </th>

                                        <th>
                                            Product
                                        </th>

                                        <th>
                                            Category
                                        </th>

                                        <th>
                                            Price
                                        </th>

                                        <th>
                                            Stock
                                        </th>

                                        <th>
                                            Status
                                        </th>

                                        <th>
                                            Actions
                                        </th>

                                    </tr>

                                </thead>


                                <tbody>

                                    {filteredProducts.length > 0 ? (

                                        filteredProducts.map(
                                            (product) => {

                                                const image =
                                                    getProductImage(
                                                        product
                                                    );

                                                return (

                                                    <tr
                                                        key={
                                                            product.id
                                                        }
                                                    >

                                                        {/* IMAGE */}

                                                        <td
                                                            style={{
                                                                width: "100px",
                                                            }}
                                                        >

                                                            {image ? (

                                                                <img
                                                                    src={
                                                                        image
                                                                    }
                                                                    alt={
                                                                        product.name ||
                                                                        "Product"
                                                                    }
                                                                    style={{
                                                                        width: "70px",
                                                                        height: "70px",
                                                                        objectFit:
                                                                            "cover",
                                                                        borderRadius:
                                                                            "8px",
                                                                    }}
                                                                    onError={(
                                                                        event
                                                                    ) => {

                                                                        event.currentTarget.style.display =
                                                                            "none";

                                                                    }}
                                                                />

                                                            ) : (

                                                                <div
                                                                    className="
                                                                        bg-light
                                                                        text-muted
                                                                        d-flex
                                                                        align-items-center
                                                                        justify-content-center
                                                                    "
                                                                    style={{
                                                                        width: "70px",
                                                                        height: "70px",
                                                                        borderRadius:
                                                                            "8px",
                                                                    }}
                                                                >
                                                                    No Image
                                                                </div>

                                                            )}

                                                        </td>


                                                        {/* PRODUCT */}

                                                        <td>

                                                            <strong>
                                                                {
                                                                    product.name ||
                                                                    "Unnamed Product"
                                                                }
                                                            </strong>


                                                            {product.description && (

                                                                <div
                                                                    className="
                                                                        text-muted
                                                                        small
                                                                    "
                                                                >
                                                                    {
                                                                        product.description
                                                                    }
                                                                </div>

                                                            )}

                                                        </td>


                                                        {/* CATEGORY */}

                                                        <td>

                                                            {
                                                                product.category_name ||
                                                                product.category?.name ||
                                                                "N/A"
                                                            }

                                                        </td>


                                                        {/* PRICE */}

                                                        <td>

                                                            <strong>
                                                                ৳
                                                                {formatPrice(
                                                                    product.price
                                                                )}
                                                            </strong>

                                                        </td>


                                                        {/* STOCK */}

                                                        <td>

                                                            {
                                                                product.stock ??
                                                                product.quantity ??
                                                                0
                                                            }

                                                        </td>


                                                        {/* STATUS */}

                                                        <td>

                                                            {product.is_available !==
                                                            false ? (

                                                                <span className="badge bg-success">
                                                                    Available
                                                                </span>

                                                            ) : (

                                                                <span className="badge bg-danger">
                                                                    Unavailable
                                                                </span>

                                                            )}

                                                        </td>


                                                        {/* ACTIONS */}

                                                        <td>

                                                            <div className="d-flex gap-2">

                                                                <Link
                                                                    to={`/admin/products/edit/${product.id}`}
                                                                    className="btn btn-warning btn-sm"
                                                                >
                                                                    Edit
                                                                </Link>


                                                                <button
                                                                    type="button"
                                                                    className="btn btn-danger btn-sm"
                                                                    onClick={() =>
                                                                        handleDelete(
                                                                            product.id
                                                                        )
                                                                    }
                                                                >
                                                                    Delete
                                                                </button>

                                                            </div>

                                                        </td>

                                                    </tr>

                                                );

                                            }
                                        )

                                    ) : (

                                        <tr>

                                            <td
                                                colSpan="7"
                                                className="text-center py-5"
                                            >

                                                <h5>
                                                    No Products Found
                                                </h5>

                                                <p className="text-muted mb-0">

                                                    {search
                                                        ? "No products match your search."
                                                        : "There are no products yet."}

                                                </p>

                                                {!search && (

                                                    <Link
                                                        to="/admin/products/add"
                                                        className="btn btn-primary mt-3"
                                                    >
                                                        Add Your First Product
                                                    </Link>

                                                )}

                                            </td>

                                        </tr>

                                    )}

                                </tbody>

                            </table>

                        </div>

                    </div>

                </div>

            </div>

        </DashboardLayout>

    );

};


export default AdminProducts;