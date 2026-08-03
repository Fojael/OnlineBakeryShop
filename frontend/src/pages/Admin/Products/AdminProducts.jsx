import { useEffect, useState, useMemo } from "react";
import { Link } from "react-router-dom";
import { toast } from "react-toastify";
import {
    getProducts,
    deleteProduct,
} from "../../../services/productService";

const AdminProducts = () => {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState("");

    const fetchProducts = async () => {
        try {
            setLoading(true);

            const response = await getProducts();

            setProducts(response.data);
            
        } catch (error) {
            console.error(error);
           toast.error("Failed to load products.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        (async () => {
            await fetchProducts();
        })();
    }, []);

    const filteredProducts = useMemo(() => {
        return products.filter((product) =>
            product.name.toLowerCase().includes(search.toLowerCase())
        );
    }, [products, search]);

    const handleDelete = async (id) => {
        const confirmDelete = window.confirm(
            "Are you sure you want to delete this product?"
        );

        if (!confirmDelete) return;

        try {
            await deleteProduct(id);

          toast.success("Product deleted successfully.");

            fetchProducts();
        } catch (error) {
            console.error(error);
            toast.error("Failed to delete product.");
        }
    };

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
                    Loading Products...
                </h4>

            </div>
        );
    }

    return (
        <div className="container py-4">

            {/* Header */}
            <div className="d-flex justify-content-between align-items-center mb-4">

                <div>
                    <h2 className="fw-bold">
                        Product Management
                    </h2>

                    <p className="text-muted">
                        Total Products:
                        <strong>
                            {" "}
                            {filteredProducts.length}
                        </strong>
                    </p>
                </div>

                <Link
                    to="/admin/products/add"
                    className="btn btn-success"
                >
                    + Add Product
                </Link>

            </div>

            {/* Search */}

            <div className="row mb-3">

                <div className="col-md-4">

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

            </div>

            {/* Table */}

            <div className="table-responsive shadow-sm">

                <table className="table table-striped table-hover align-middle">

                    <thead className="table-dark">

                        <tr>
                            <th>ID</th>
                            <th>Image</th>
                            <th>Name</th>
                            <th>Category</th>
                            <th>Price</th>
                            <th>Stock</th>
                            <th>Status</th>
                            <th width="170">
                                Actions
                            </th>
                        </tr>

                    </thead>

                    <tbody>

                        {filteredProducts.length > 0 ? (

                            filteredProducts.map((product) => (

                                <tr key={product.id}>

                                    <td>{product.id}</td>

                                    <td>

                                      <img
                                          src={
                                               product.image
                                              ? product.image
                                            : "https://placehold.co/300x300?text=No+Image"
                                                }
                                              alt={product.name}
                                        />

                                    </td>

                                    <td className="fw-semibold">
                                        {product.name}
                                    </td>

                                    <td>
                                        {product.category}
                                    </td>

                                    <td>
                                        ৳
                                        {Number(
                                            product.price
                                        ).toFixed(2)}
                                    </td>

                                    <td>
                                        {product.stock_quantity}
                                    </td>

                                    <td>

                                        {product.is_available ? (

                                            <span className="badge bg-success">
                                                In Stock
                                            </span>

                                        ) : (

                                            <span className="badge bg-danger">
                                                Out of Stock
                                            </span>

                                        )}

                                    </td>

                                    <td>

                                        <Link
                                            to={`/admin/products/edit/${product.id}`}
                                            className="btn btn-warning btn-sm me-2"
                                        >
                                            Edit
                                        </Link>

                                        <button
                                            className="btn btn-danger btn-sm"
                                            onClick={() =>
                                                handleDelete(
                                                    product.id
                                                )
                                            }
                                        >
                                            Delete
                                        </button>

                                    </td>

                                </tr>

                            ))

                        ) : (

                            <tr>

                                <td
                                    colSpan="8"
                                    className="text-center py-5"
                                >

                                    <h5>
                                        No products found
                                    </h5>

                                </td>

                            </tr>

                        )}

                    </tbody>

                </table>

            </div>

        </div>
    );
};

export default AdminProducts;