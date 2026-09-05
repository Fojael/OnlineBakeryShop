import {
    useEffect,
    useMemo,
    useState,
} from "react";

import { toast } from "react-toastify";

import {
    getSupplierProducts,
    updateSupplierProduct,
} from "../../../services/supplierService";


const getStatus = (product) => {
    const currentStock = Number(
        product.stock_quantity ?? 0
    );

    const minimumStock = Number(
        product.minimum_stock ?? 0
    );

    if (currentStock === 0) {
        return "Out of Stock";
    }

    if (currentStock <= minimumStock) {
        return "Low Stock";
    }

    return "In Stock";
};


const getStatusClass = (status) => {
    switch (status) {
        case "In Stock":
            return "bg-success";

        case "Low Stock":
            return "bg-warning text-dark";

        case "Out of Stock":
            return "bg-danger";

        default:
            return "bg-secondary";
    }
};


const formatDate = (value) => {
    if (!value) {
        return "Not available";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return "Not available";
    }

    return date.toLocaleString("en-BD", {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    });
};


const SupplierInventory = () => {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [updatingId, setUpdatingId] = useState(null);


    // ==========================================================
    // LOAD PRODUCTS
    // ==========================================================

    useEffect(() => {
        let isMounted = true;

        const loadProducts = async () => {
            try {
                const response =
                    await getSupplierProducts();

                const data = Array.isArray(response)
                    ? response
                    : response?.results || [];

                if (isMounted) {
                    setProducts(data);
                }
            } catch (error) {
                console.error(
                    "Failed to load supplier inventory:",
                    error
                );

                if (isMounted) {
                    toast.error(
                        error?.response?.data?.detail ||
                            "Failed to load inventory."
                    );

                    setProducts([]);
                }
            } finally {
                if (isMounted) {
                    setLoading(false);
                }
            }
        };

        void loadProducts();

        return () => {
            isMounted = false;
        };
    }, []);


    // ==========================================================
    // SUMMARY
    // ==========================================================

    const summary = useMemo(() => {
        const totalProducts = products.length;

        const totalStock = products.reduce(
            (sum, product) =>
                sum +
                Number(
                    product.stock_quantity ?? 0
                ),
            0
        );

        const lowStock = products.filter(
            (product) =>
                getStatus(product) === "Low Stock"
        ).length;

        const outOfStock = products.filter(
            (product) =>
                getStatus(product) === "Out of Stock"
        ).length;

        return {
            totalProducts,
            totalStock,
            lowStock,
            outOfStock,
        };
    }, [products]);


    // ==========================================================
    // STOCK HISTORY
    // ==========================================================

    const stockHistory = useMemo(
        () =>
            [...products]
                .sort(
                    (a, b) =>
                        new Date(
                            b.updated_at ||
                                b.created_at
                        ) -
                        new Date(
                            a.updated_at ||
                                a.created_at
                        )
                )
                .slice(0, 6)
                .map((product) => ({
                    id: product.id,
                    name: product.name,
                    stock: Number(
                        product.stock_quantity ?? 0
                    ),
                    date:
                        product.updated_at ||
                        product.created_at,
                })),
        [products]
    );


    // ==========================================================
    // UPDATE STOCK
    // ==========================================================

    const handleUpdateStock = async (product) => {
        const currentStock = Number(
            product.stock_quantity ?? 0
        );

        const value = window.prompt(
            `Update stock for ${product.name} (current: ${currentStock})`,
            String(currentStock)
        );

        if (value === null) {
            return;
        }

        const nextValue = Number(value);

        if (
            !Number.isFinite(nextValue) ||
            nextValue < 0
        ) {
            toast.warning(
                "Stock must be a valid non-negative number."
            );
            return;
        }

        try {
            setUpdatingId(product.id);

            await updateSupplierProduct(
                product.id,
                {
                    stock_quantity: nextValue,
                }
            );

            setProducts((previous) =>
                previous.map((item) =>
                    item.id === product.id
                        ? {
                              ...item,
                              stock_quantity:
                                  nextValue,
                              updated_at:
                                  new Date().toISOString(),
                          }
                        : item
                )
            );

            toast.success(
                `Stock updated for ${product.name}.`
            );
        } catch (error) {
            console.error(
                "Failed to update stock:",
                error
            );

            toast.error(
                error?.response?.data?.detail ||
                    "Failed to update stock."
            );
        } finally {
            setUpdatingId(null);
        }
    };


    // ==========================================================
    // LOADING
    // ==========================================================

    if (loading) {
        return (
            <div className="container py-4">
                <div className="text-center py-5">

                    <div
                        className="spinner-border"
                        role="status"
                    />

                    <p className="mt-3 mb-0">
                        Loading supplier inventory...
                    </p>

                </div>
            </div>
        );
    }


    return (
        <div className="container py-4">

            <div className="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-3">

                <div>
                    <h2 className="fw-bold mb-1">
                        Supplier Inventory
                    </h2>

                    <p className="text-muted mb-0">
                        Track stock levels and update
                        inventory safely.
                    </p>
                </div>

            </div>


            {/* SUMMARY */}

            <div className="row g-3 mb-4">

                <div className="col-md-3">
                    <div className="card border-0 shadow-sm h-100">
                        <div className="card-body">
                            <small className="text-muted">
                                Total Products
                            </small>

                            <h3 className="mt-2 mb-0 fw-bold">
                                {summary.totalProducts}
                            </h3>
                        </div>
                    </div>
                </div>


                <div className="col-md-3">
                    <div className="card border-0 shadow-sm h-100">
                        <div className="card-body">
                            <small className="text-muted">
                                Total Stock
                            </small>

                            <h3 className="mt-2 mb-0 fw-bold">
                                {summary.totalStock}
                            </h3>
                        </div>
                    </div>
                </div>


                <div className="col-md-3">
                    <div className="card border-0 shadow-sm h-100">
                        <div className="card-body">
                            <small className="text-muted">
                                Low Stock
                            </small>

                            <h3 className="mt-2 mb-0 fw-bold text-warning">
                                {summary.lowStock}
                            </h3>
                        </div>
                    </div>
                </div>


                <div className="col-md-3">
                    <div className="card border-0 shadow-sm h-100">
                        <div className="card-body">
                            <small className="text-muted">
                                Out of Stock
                            </small>

                            <h3 className="mt-2 mb-0 fw-bold text-danger">
                                {summary.outOfStock}
                            </h3>
                        </div>
                    </div>
                </div>

            </div>


            {/* INVENTORY TABLE */}

            <div className="card shadow-sm border-0">

                <div className="card-body p-0">

                    <div className="table-responsive">

                        <table className="table align-middle mb-0">

                            <thead className="table-light">
                                <tr>
                                    <th>Product</th>
                                    <th>Current Stock</th>
                                    <th>Minimum Stock</th>
                                    <th>Status</th>
                                    <th>Last Updated</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>

                            <tbody>

                                {products.length === 0 ? (
                                    <tr>
                                        <td
                                            colSpan="6"
                                            className="text-center text-muted py-4"
                                        >
                                            No inventory records
                                            found.
                                        </td>
                                    </tr>
                                ) : (
                                    products.map(
                                        (product) => {
                                            const status =
                                                getStatus(
                                                    product
                                                );

                                            const minimumStock =
                                                Number(
                                                    product.minimum_stock ??
                                                        0
                                                );

                                            return (
                                                <tr
                                                    key={
                                                        product.id
                                                    }
                                                >

                                                    <td>
                                                        <div className="fw-semibold">
                                                            {
                                                                product.name
                                                            }
                                                        </div>

                                                        <small className="text-muted">
                                                            {
                                                                product.category
                                                            }
                                                        </small>
                                                    </td>

                                                    <td>
                                                        {Number(
                                                            product.stock_quantity ??
                                                                0
                                                        )}
                                                    </td>

                                                    <td>
                                                        {
                                                            minimumStock
                                                        }
                                                    </td>

                                                    <td>
                                                        <span
                                                            className={`badge ${getStatusClass(
                                                                status
                                                            )}`}
                                                        >
                                                            {
                                                                status
                                                            }
                                                        </span>
                                                    </td>

                                                    <td>
                                                        {formatDate(
                                                            product.updated_at ||
                                                                product.created_at
                                                        )}
                                                    </td>

                                                    <td>
                                                        <button
                                                            type="button"
                                                            className="btn btn-sm btn-outline-primary"
                                                            onClick={() =>
                                                                handleUpdateStock(
                                                                    product
                                                                )
                                                            }
                                                            disabled={
                                                                updatingId ===
                                                                product.id
                                                            }
                                                        >
                                                            {updatingId ===
                                                            product.id
                                                                ? "Updating..."
                                                                : "Update Stock"}
                                                        </button>
                                                    </td>

                                                </tr>
                                            );
                                        }
                                    )
                                )}

                            </tbody>

                        </table>

                    </div>

                </div>

            </div>


            {/* HISTORY */}

            <div className="row mt-4 g-3">

                <div className="col-lg-7">

                    <div className="card shadow-sm border-0 h-100">

                        <div className="card-body">

                            <h5 className="fw-bold mb-3">
                                Stock History
                            </h5>

                            {stockHistory.length === 0 ? (
                                <p className="text-muted mb-0">
                                    No stock history
                                    available yet.
                                </p>
                            ) : (
                                <div className="list-group list-group-flush">

                                    {stockHistory.map(
                                        (entry) => (
                                            <div
                                                key={entry.id}
                                                className="list-group-item px-0"
                                            >

                                                <div className="d-flex justify-content-between align-items-center gap-3">

                                                    <div>

                                                        <div className="fw-semibold">
                                                            {
                                                                entry.name
                                                            }
                                                        </div>

                                                        <small className="text-muted">
                                                            {formatDate(
                                                                entry.date
                                                            )}
                                                        </small>

                                                    </div>

                                                    <span className="badge bg-light text-dark border">
                                                        {
                                                            entry.stock
                                                        }{" "}
                                                        units
                                                    </span>

                                                </div>

                                            </div>
                                        )
                                    )}

                                </div>
                            )}

                        </div>
                    </div>

                </div>


                <div className="col-lg-5">

                    <div className="card shadow-sm border-0 h-100">

                        <div className="card-body">

                            <h5 className="fw-bold mb-3">
                                Last Restock Date
                            </h5>

                            {products.length === 0 ? (
                                <p className="text-muted mb-0">
                                    No product restock
                                    activity yet.
                                </p>
                            ) : (
                                <div className="list-group list-group-flush">

                                    {[...products]
                                        .sort(
                                            (a, b) =>
                                                new Date(
                                                    b.updated_at ||
                                                        b.created_at
                                                ) -
                                                new Date(
                                                    a.updated_at ||
                                                        a.created_at
                                                )
                                        )
                                        .map(
                                            (
                                                product
                                            ) => (
                                                <div
                                                    key={
                                                        product.id
                                                    }
                                                    className="list-group-item px-0"
                                                >

                                                    <div className="d-flex justify-content-between gap-3 align-items-center">

                                                        <span className="fw-medium">
                                                            {
                                                                product.name
                                                            }
                                                        </span>

                                                        <small className="text-muted">
                                                            {formatDate(
                                                                product.updated_at ||
                                                                    product.created_at
                                                            )}
                                                        </small>

                                                    </div>

                                                </div>
                                            )
                                        )}

                                </div>
                            )}

                        </div>
                    </div>

                </div>

            </div>

        </div>
    );
};


export default SupplierInventory;