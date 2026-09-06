import api from "./api";

export const getInventoryItems = (response) => {
    const data = response?.data;
    return Array.isArray(data) ? data : data?.results || [];
};

// Get All Inventory
export const getInventory = () => {
    return api.get("inventory/");
};

// Get Single Inventory Item
export const getInventoryItem = (id) => {
    return api.get(`inventory/${id}/`);
};

// Update Inventory
export const updateInventory = (id, data) => {
    return api.put(
        `inventory/${id}/`,
        data,
        {
            headers: {
                "Content-Type": "application/json",
            },
        }
    );
};