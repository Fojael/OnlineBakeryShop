import DashboardLayout from "../../../layouts/DashboardLayout";

const AIPrediction = () => {
    return (
        <DashboardLayout>

            <h2>AI Sales Prediction & Inventory Recommendation</h2>

            <hr />

            <table className="table table-bordered table-striped">

                <thead>
                    <tr>
                        <th>Product Name</th>
                        <th>Predicted Demand</th>
                        <th>Recommended Action</th>
                    </tr>
                </thead>

                <tbody>

                    <tr>
                        <td>Chocolate Cake</td>
                        <td>High</td>
                        <td>Increase Stock</td>
                    </tr>

                    <tr>
                        <td>Vanilla Cake</td>
                        <td>Medium</td>
                        <td>Maintain Stock</td>
                    </tr>

                    <tr>
                        <td>Cup Cake</td>
                        <td>Low</td>
                        <td>Reduce Stock</td>
                    </tr>

                </tbody>

            </table>

        </DashboardLayout>
    );
};

export default AIPrediction;