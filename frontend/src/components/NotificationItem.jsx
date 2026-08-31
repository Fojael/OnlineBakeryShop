import useNotification from "../../hooks/useNotification";

export default function NotificationItem({

    notification,

}) {

    const {

        markNotificationRead,

        deleteNotification,

    } = useNotification();

    return (

        <div
            className={`
                list-group-item
                ${notification.is_read
                    ? ""
                    : "list-group-item-warning"}
            `}
        >

            <div
                className="
                    d-flex
                    justify-content-between
                "
            >

                <div>

                    <h6
                        className="mb-1"
                    >

                        {notification.title}

                    </h6>

                    <small>

                        {notification.message}

                    </small>

                    <br />

                    <small
                        className="text-muted"
                    >

                        {
                            new Date(
                                notification.created_at
                            ).toLocaleString()
                        }

                    </small>

                </div>

                <div
                    className="
                        d-flex
                        flex-column
                        gap-2
                    "
                >

                    {
                        !notification.is_read && (

                            <button
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

                                Read

                            </button>

                        )
                    }

                    <button
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

        </div>

    );

}