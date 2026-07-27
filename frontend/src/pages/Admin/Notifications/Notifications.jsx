import DashboardLayout from "../../../layouts/DashboardLayout";

const Notifications = () => {
    return (
        <DashboardLayout>

            <h2>Notifications</h2>

            <hr />

            <table className="table table-bordered table-striped">

                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Notification</th>
                        <th>Date</th>
                        <th>Status</th>
                    </tr>
                </thead>

                <tbody>

                    <tr>
                        <td>1</td>
                        <td>New customer order received.</td>
                        <td>24 July 2026</td>
                        <td>Unread</td>
                    </tr>

                    <tr>
                        <td>2</td>
                        <td>Chocolate Cake stock is low.</td>
                        <td>24 July 2026</td>
                        <td>Unread</td>
                    </tr>

                    <tr>
                        <td>3</td>
                        <td>Payment received for Order #1005.</td>
                        <td>24 July 2026</td>
                        <td>Read</td>
                    </tr>

                    <tr>
                        <td>4</td>
                        <td>AI recommends increasing Vanilla Cake stock.</td>
                        <td>24 July 2026</td>
                        <td>Read</td>
                    </tr>

                </tbody>

            </table>

        </DashboardLayout>
    );
};

export default Notifications;