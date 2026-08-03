import api from "./api";

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