import { useContext } from "react";

import NotificationContext
    from "../context/NotificationContext";

export default function useNotification() {

    return useContext(NotificationContext);

}