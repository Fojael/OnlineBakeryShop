import {
    useState,
    useEffect,
    useCallback,
} from "react";

import NotificationContext from "../context/NotificationContext";

import { useAuth } from "../context/AuthContext";

import {
    getNotifications,
    markNotificationRead as markReadApi,
    markAllNotificationsRead as markAllApi,
    deleteNotification as deleteApi,
    deleteAllNotifications as deleteAllApi,
} from "../services/notificationService";

export default function NotificationProvider({
    children,
}) {

    const { isAuthenticated } = useAuth();

    const [notifications, setNotifications] = useState([]);

    const [unreadCount, setUnreadCount] = useState(0);

    const [loading, setLoading] = useState(false);

    // =============================================
    // FETCH NOTIFICATIONS
    // =============================================

    const fetchNotifications = useCallback(async () => {

        if (!isAuthenticated) {

            return {
                notifications: [],
                unread_count: 0,
            };

        }

        return await getNotifications();

    }, [isAuthenticated]);

    // =============================================
    // LOAD AFTER LOGIN
    // =============================================

    useEffect(() => {

        let cancelled = false;

        async function load() {

            try {

                setLoading(true);

                const data = await fetchNotifications();

                if (cancelled) return;

                setNotifications(
                    data.notifications || []
                );

                setUnreadCount(
                    data.unread_count || 0
                );

            } catch (error) {

                console.error(error);

            } finally {

                if (!cancelled) {

                    setLoading(false);

                }

            }

        }

        load();

        return () => {

            cancelled = true;

        };

    }, [fetchNotifications]);

    // =============================================
    // AUTO REFRESH
    // =============================================

    useEffect(() => {

        if (!isAuthenticated) {

            return;

        }

        const interval = setInterval(async () => {

            try {

                const data =
                    await fetchNotifications();

                setNotifications(
                    data.notifications || []
                );

                setUnreadCount(
                    data.unread_count || 0
                );

            } catch (error) {

                console.error(error);

            }

        }, 30000);

        return () => clearInterval(interval);

    }, [
        isAuthenticated,
        fetchNotifications,
    ]);

    // =============================================
    // MANUAL RELOAD
    // =============================================

    const loadNotifications = useCallback(async () => {

        try {

            const data =
                await fetchNotifications();

            setNotifications(
                data.notifications || []
            );

            setUnreadCount(
                data.unread_count || 0
            );

        } catch (error) {

            console.error(error);

        }

    }, [fetchNotifications]);

    // =============================================
    // MARK ONE
    // =============================================

    const markNotificationRead = async (id) => {

        try {

            await markReadApi(id);

            setNotifications((prev) =>
                prev.map((item) =>
                    item.id === id
                        ? {
                              ...item,
                              is_read: true,
                          }
                        : item
                )
            );

            setUnreadCount((prev) =>
                Math.max(prev - 1, 0)
            );

        } catch (error) {

            console.error(error);

        }

    };

    // =============================================
    // MARK ALL
    // =============================================

    const markAllRead = async () => {

        try {

            await markAllApi();

            setNotifications((prev) =>
                prev.map((item) => ({
                    ...item,
                    is_read: true,
                }))
            );

            setUnreadCount(0);

        } catch (error) {

            console.error(error);

        }

    };

    // =============================================
    // DELETE ONE
    // =============================================

    const deleteNotification = async (id) => {

        try {

            const target =
                notifications.find(
                    (item) => item.id === id
                );

            await deleteApi(id);

            setNotifications((prev) =>
                prev.filter(
                    (item) => item.id !== id
                )
            );

            if (
                target &&
                !target.is_read
            ) {

                setUnreadCount((prev) =>
                    Math.max(prev - 1, 0)
                );

            }

        } catch (error) {

            console.error(error);

        }

    };

    // =============================================
    // DELETE ALL
    // =============================================

    const deleteAllNotifications = async () => {

        try {

            await deleteAllApi();

            setNotifications([]);

            setUnreadCount(0);

        } catch (error) {

            console.error(error);

        }

    };

    // =============================================
    // CONTEXT
    // =============================================

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

    return (

        <NotificationContext.Provider
            value={value}
        >

            {children}

        </NotificationContext.Provider>

    );

}