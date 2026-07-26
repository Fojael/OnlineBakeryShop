const Orders = () => {
    // Dummy data for now
    const currentOrders = [
        {
            id: 1,
            product: "Chocolate Cake",
            total: 25.99,
            status: "Preparing",
        },
        {
            id: 2,
            product: "Red Velvet Cake",
            total: 18.50,
            status: "Out for Delivery",
        },
    ];

    const previousOrders = [
        {
            id: 3,
            product: "Strawberry Cupcakes",
            total: 15.75,
            status: "Delivered",
        },
        {
            id: 4,
            product: "Blueberry Muffins",
            total: 12.99,
            status: "Delivered",
        },
    ];

    return (
        <div className="container py-5">

            <h1 className="text-center mb-5">
                My Orders
            </h1>

            {/* Current Orders */}
            <div className="card shadow mb-5">
                <div className="card-header">
                    <h3 className="mb-0">
                        Current Orders
                    </h3>
                </div>

                <div className="card-body">

                    {currentOrders.length === 0 ? (
                        <p>No current orders.</p>
                    ) : (
                        <div className="table-responsive">
                            <table className="table table-striped">
                                <thead>
                                    <tr>
                                        <th>Order ID</th>
                                        <th>Product</th>
                                        <th>Total Price</th>
                                        <th>Status</th>
                                    </tr>
                                </thead>

                                <tbody>
                                    {currentOrders.map((order) => (
                                        <tr key={order.id}>
                                            <td>#{order.id}</td>
                                            <td>{order.product}</td>
                                            <td>
                                                ${order.total}
                                            </td>
                                            <td>
                                                {order.status}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}

                </div>
            </div>


            {/* Previous Orders */}
            <div className="card shadow mb-5">
                <div className="card-header">
                    <h3 className="mb-0">
                        Previous Orders
                    </h3>
                </div>

                <div className="card-body">

                    {previousOrders.length === 0 ? (
                        <p>No previous orders.</p>
                    ) : (
                        <div className="table-responsive">
                            <table className="table table-striped">
                                <thead>
                                    <tr>
                                        <th>Order ID</th>
                                        <th>Product</th>
                                        <th>Total Price</th>
                                        <th>Status</th>
                                    </tr>
                                </thead>

                                <tbody>
                                    {previousOrders.map((order) => (
                                        <tr key={order.id}>
                                            <td>#{order.id}</td>
                                            <td>{order.product}</td>
                                            <td>
                                                ${order.total}
                                            </td>
                                            <td>
                                                {order.status}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}

                </div>
            </div>


            {/* Order Tracking */}
            <div className="card shadow">
                <div className="card-header">
                    <h3 className="mb-0">
                        Order Tracking
                    </h3>
                </div>

                <div className="card-body">

                    <p>
                        Track the status of your current
                        bakery orders.
                    </p>

                    <ul className="list-group">

                        <li className="list-group-item">
                            Order #1 - Preparing
                        </li>

                        <li className="list-group-item">
                            Order #2 - Out for Delivery
                        </li>

                    </ul>

                </div>
            </div>

        </div>
    );
};

export default Orders;