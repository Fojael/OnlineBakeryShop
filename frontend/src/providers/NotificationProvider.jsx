import {
    useState,
    useEffect,
    useCallback,
} from "react";

import NotificationContext
    from "../context/NotificationContext";

import {
    getNotifications,
    markNotificationRead as markReadApi,
    markAllNotificationsRead as markAllApi,
    deleteNotification as deleteApi,
    deleteAllNotifications as deleteAllApi,
} from "../services/notificationService";


// ==========================================================
// NOTIFICATION PROVIDER
// ==========================================================

export default function NotificationProvider({
    children,
}) {

    // ==========================================================
    // STATE
    // ==========================================================

    const [
        notifications,
        setNotifications,
    ] = useState([]);

    const [
        unreadCount,
        setUnreadCount,
    ] = useState(0);

    const [
        loading,
        setLoading,
    ] = useState(false);


    // ==========================================================
    // FETCH NOTIFICATIONS FROM API
    // ==========================================================

    const fetchNotifications = useCallback(
        async () => {

            const accessToken =
                localStorage.getItem("access")
                ||
                sessionStorage.getItem("access");

            if (!accessToken) {

                return {
                    notifications: [],
                    unread_count: 0,
                };

            }

            return await getNotifications();

        },
        []
    );


    // ==========================================================
    // LOAD NOTIFICATIONS
    // ==========================================================

    const loadNotifications = useCallback(
        async () => {

            const accessToken =
                localStorage.getItem("access")
                ||
                sessionStorage.getItem("access");

            if (!accessToken) {

                setNotifications([]);
                setUnreadCount(0);

                return;

            }

            try {

                setLoading(true);

                const data =
                    await fetchNotifications();


                setNotifications(
                    data?.notifications || []
                );

                setUnreadCount(
                    data?.unread_count || 0
                );

            } catch (error) {

                console.error(
                    "Failed to load notifications:",
                    error
                );

            } finally {

                setLoading(false);

            }

        },
        [fetchNotifications]
    );


    // ==========================================================
    // INITIAL LOAD + AUTH CHANGE LISTENER
    // ==========================================================

    useEffect(() => {

        const handleAuthChange = () => {

            loadNotifications();

        };


        window.addEventListener(
            "auth-changed",
            handleAuthChange
        );


        // Delay initial loading so the effect itself
        // does not synchronously trigger state updates.

        const timer = setTimeout(() => {

            handleAuthChange();

        }, 0);


        return () => {

            window.removeEventListener(
                "auth-changed",
                handleAuthChange
            );

            clearTimeout(timer);

        };

    }, [loadNotifications]);


    // ==========================================================
    // AUTO REFRESH EVERY 30 SECONDS
    // ==========================================================

    useEffect(() => {

        const interval =
            setInterval(async () => {

                const accessToken =
                    localStorage.getItem("access")
                    ||
                    sessionStorage.getItem("access");


                if (!accessToken) {

                    setNotifications([]);
                    setUnreadCount(0);

                    return;

                }


                try {

                    const data =
                        await fetchNotifications();


                    setNotifications(
                        data?.notifications || []
                    );

                    setUnreadCount(
                        data?.unread_count || 0
                    );

                } catch (error) {

                    console.error(
                        "Notification refresh failed:",
                        error
                    );

                }

            }, 30000);


        return () => {

            clearInterval(interval);

        };

    }, [fetchNotifications]);


    // ==========================================================
    // MARK ONE NOTIFICATION AS READ
    // ==========================================================

    const markNotificationRead =
        async (id) => {

            try {

                await markReadApi(id);


                setNotifications((previous) =>
                    previous.map((item) =>
                        item.id === id
                            ? {
                                ...item,
                                is_read: true,
                            }
                            : item
                    )
                );


                setUnreadCount((previous) =>
                    Math.max(
                        previous - 1,
                        0
                    )
                );

            } catch (error) {

                console.error(
                    "Failed to mark notification as read:",
                    error
                );

            }

        };


    // ==========================================================
    // MARK ALL NOTIFICATIONS AS READ
    // ==========================================================

    const markAllRead =
        async () => {

            try {

                await markAllApi();


                setNotifications((previous) =>
                    previous.map((item) => ({
                        ...item,
                        is_read: true,
                    }))
                );


                setUnreadCount(0);

            } catch (error) {

                console.error(
                    "Failed to mark all notifications as read:",
                    error
                );

            }

        };


    // ==========================================================
    // DELETE ONE NOTIFICATION
    // ==========================================================

    const deleteNotification =
        async (id) => {

            try {

                const target =
                    notifications.find(
                        (item) =>
                            item.id === id
                    );


                await deleteApi(id);


                setNotifications((previous) =>
                    previous.filter(
                        (item) =>
                            item.id !== id
                    )
                );


                if (
                    target &&
                    !target.is_read
                ) {

                    setUnreadCount((previous) =>
                        Math.max(
                            previous - 1,
                            0
                        )
                    );

                }

            } catch (error) {

                console.error(
                    "Failed to delete notification:",
                    error
                );

            }

        };


    // ==========================================================
    // DELETE ALL NOTIFICATIONS
    // ==========================================================

    const deleteAllNotifications =
        async () => {

            try {

                await deleteAllApi();


                setNotifications([]);

                setUnreadCount(0);

            } catch (error) {

                console.error(
                    "Failed to delete all notifications:",
                    error
                );

            }

        };


    // ==========================================================
    // CONTEXT VALUE
    // ==========================================================

    const value = {

        notifications,

        unreadCount,

        loading,

        loadNotifications,

        markNotificationRead,

        markAllRead,

        deleteNotification,

        deleteAllNotifications,

    };


    // ==========================================================
    // PROVIDER
    // ==========================================================

    return (

        <NotificationContext.Provider
            value={value}
        >

            {children}

        </NotificationContext.Provider>

    );

}