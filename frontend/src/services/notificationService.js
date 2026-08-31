import api from "./api";


// ==========================================================
// GET ALL NOTIFICATIONS
// ==========================================================

export const getNotifications = async () => {

    const response =
        await api.get(
            "/notifications/"
        );

    return response.data;

};


// ==========================================================
// GET UNREAD NOTIFICATIONS
// ==========================================================

export const getUnreadNotifications =
    async () => {

        const response =
            await api.get(
                "/notifications/unread/"
            );

        return response.data;

    };


// ==========================================================
// MARK ONE AS READ
// ==========================================================

export const markNotificationRead =
    async (id) => {

        const response =
            await api.patch(
                `/notifications/${id}/read/`
            );

        return response.data;

    };


// ==========================================================
// MARK ALL AS READ
// ==========================================================

export const markAllNotificationsRead =
    async () => {

        const response =
            await api.patch(
                "/notifications/read-all/"
            );

        return response.data;

    };


// ==========================================================
// DELETE ONE
// ==========================================================

export const deleteNotification =
    async (id) => {

        const response =
            await api.delete(
                `/notifications/${id}/`
            );

        return response.data;

    };


// ==========================================================
// DELETE ALL
// ==========================================================

export const deleteAllNotifications =
    async () => {

        const response =
            await api.delete(
                "/notifications/delete-all/"
            );

        return response.data;

    };