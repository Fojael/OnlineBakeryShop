import useNotification
    from "../../hooks/useNotification";

import "../../styles/Notification.css";


const NotificationsPage = () => {

    const {

        notifications,

        unreadCount,

        loading,

        markNotificationRead,

        markAllRead,

        deleteNotification,

        deleteAllNotifications,

    } = useNotification();


    return (

        <div className="container py-4">

            <div className="notification-header">

                <div>

                    <h2 className="mb-1">
                        Notifications
                    </h2>

                    <p className="text-muted mb-0">

                        Total: {notifications.length}

                        {" | "}

                        Unread: {unreadCount}

                    </p>

                </div>


                <div
                    className="
                        notification-actions
                    "
                >

                    <button
                        type="button"
                        className="
                            btn
                            btn-primary
                        "
                        onClick={markAllRead}
                        disabled={
                            unreadCount === 0
                        }
                    >
                        Mark All Read
                    </button>


                    <button
                        type="button"
                        className="
                            btn
                            btn-danger
                        "
                        onClick={
                            deleteAllNotifications
                        }
                        disabled={
                            notifications.length === 0
                        }
                    >
                        Delete All
                    </button>

                </div>

            </div>


            <hr />


            {loading && (

                <div
                    className="
                        text-center
                        py-5
                    "
                >

                    <div
                        className="
                            spinner-border
                        "
                        role="status"
                    >

                        <span className="visually-hidden">
                            Loading...
                        </span>

                    </div>

                </div>

            )}


            {!loading &&
                notifications.length === 0 && (

                    <div
                        className="
                            empty-notification
                        "
                    >

                        <h4>
                            🎉 You're all caught up!
                        </h4>

                        <p>
                            No notifications found.
                        </p>

                    </div>

                )}


            {!loading &&
                notifications.map(
                    (notification) => (

                        <div
                            key={
                                notification.id
                            }
                            className={`
                                notification-card
                                ${
                                    notification.is_read
                                        ? ""
                                        : "notification-unread"
                                }
                            `}
                        >

                            <div
                                className="
                                    notification-content
                                "
                            >

                                <h5>
                                    {
                                        notification.title
                                    }
                                </h5>


                                <p>
                                    {
                                        notification.message
                                    }
                                </p>


                                <small
                                    className="
                                        text-muted
                                    "
                                >

                                    {new Date(
                                        notification.created_at
                                    ).toLocaleString()}

                                </small>

                            </div>


                            <div
                                className="
                                    notification-buttons
                                "
                            >

                                {!notification.is_read && (

                                    <button
                                        type="button"
                                        className="
                                            btn
                                            btn-success
                                            btn-sm
                                        "
                                        onClick={() =>
                                            markNotificationRead(
                                                notification.id
                                            )
                                        }
                                    >
                                        Mark Read
                                    </button>

                                )}


                                <button
                                    type="button"
                                    className="
                                        btn
                                        btn-outline-danger
                                        btn-sm
                                    "
                                    onClick={() =>
                                        deleteNotification(
                                            notification.id
                                        )
                                    }
                                >
                                    Delete
                                </button>

                            </div>

                        </div>

                    )
                )}

        </div>

    );

};


export default NotificationsPage;