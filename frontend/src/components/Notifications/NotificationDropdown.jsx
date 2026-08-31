import useNotification
    from "../../hooks/useNotification";

import NotificationItem
    from "./NotificationItem";


export default function NotificationDropdown({
    closeDropdown,
}) {

    const {
        notifications,
        markAllRead,
        deleteAllNotifications,
    } = useNotification();


    return (

        <div
            className="
                card
                shadow
                position-absolute
                end-0
                mt-2
            "
            style={{
                width: "380px",
                maxWidth: "90vw",
                zIndex: 9999,
            }}
        >

            {/* HEADER */}

            <div
                className="
                    card-header
                    d-flex
                    justify-content-between
                    align-items-center
                "
            >

                <strong>
                    Notifications
                </strong>


                <div
                    className="
                        d-flex
                        align-items-center
                        gap-2
                    "
                >

                    <button
                        type="button"
                        className="
                            btn
                            btn-sm
                            btn-outline-primary
                        "
                        onClick={markAllRead}
                    >

                        Mark All

                    </button>


                    <button
                        type="button"
                        className="
                            btn
                            btn-sm
                            btn-outline-secondary
                        "
                        onClick={closeDropdown}
                        aria-label="Close notifications"
                    >

                        <i
                            className="
                                bi
                                bi-x-lg
                            "
                        />

                    </button>

                </div>

            </div>


            {/* LIST */}

            <div
                className="list-group"
                style={{
                    maxHeight: "400px",
                    overflowY: "auto",
                }}
            >

                {notifications.length === 0 ? (

                    <div
                        className="
                            p-3
                            text-center
                            text-muted
                        "
                    >

                        No Notifications

                    </div>

                ) : (

                    notifications.map(
                        (notification) => (

                            <NotificationItem
                                key={
                                    notification.id
                                }
                                notification={
                                    notification
                                }
                            />

                        )
                    )

                )}

            </div>


            {/* FOOTER */}

            <div
                className="card-footer"
            >

                <button
                    type="button"
                    className="
                        btn
                        btn-danger
                        btn-sm
                        w-100
                    "
                    onClick={
                        deleteAllNotifications
                    }
                >

                    Delete All

                </button>

            </div>

        </div>

    );

}