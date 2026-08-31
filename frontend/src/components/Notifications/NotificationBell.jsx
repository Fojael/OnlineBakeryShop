import {
    useState,
} from "react";

import useNotification
    from "../../hooks/useNotification";

import NotificationDropdown
    from "./NotificationDropdown";


export default function NotificationBell() {

    const {
        unreadCount,
    } = useNotification();


    const [
        open,
        setOpen,
    ] = useState(false);


    return (

        <div
            className="
                position-relative
            "
        >

            <button
                type="button"
                className="
                    btn
                    btn-light
                    border
                    position-relative
                "
                onClick={() =>
                    setOpen(
                        (previous) =>
                            !previous
                    )
                }
                aria-label="Notifications"
            >

                <i
                    className="
                        bi
                        bi-bell-fill
                        fs-5
                    "
                />


                {unreadCount > 0 && (

                    <span
                        className="
                            position-absolute
                            top-0
                            start-100
                            translate-middle
                            badge
                            rounded-pill
                            bg-danger
                        "
                    >

                        {unreadCount}

                    </span>

                )}

            </button>


            {open && (

                <NotificationDropdown
                    closeDropdown={() =>
                        setOpen(false)
                    }
                />

            )}

        </div>

    );

}