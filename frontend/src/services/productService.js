import api from "./api";

const fallbackProducts = [
    {
        id: 1,
        name: "Classic Vanilla Cake",
        category: "Cake",
        description: "Soft vanilla sponge layered with creamy frosting.",
        price: 1200,
        stock_quantity: 12,
        rating: 5,
        image: "https://placehold.co/300x300?text=Classic+Vanilla+Cake",
    },
    {
        id: 2,
        name: "Chocolate Donut",
        category: "Donut",
        description: "Warm chocolate donut with a glossy finish.",
        price: 180,
        stock_quantity: 25,
        rating: 4,
        image: "https://placehold.co/300x300?text=Chocolate+Donut",
    },
    {
        id: 3,
        name: "Butter Croissant",
        category: "Pastry",
        description: "Flaky golden croissant baked fresh every morning.",
        price: 220,
        stock_quantity: 18,
        rating: 5,
        image: "https://placehold.co/300x300?text=Butter+Croissant",
    },
    {
        id: 4,
        name: "Honey Bread",
        category: "Bread",
        description: "Soft bread with a sweet honey glaze.",
        price: 260,
        stock_quantity: 20,
        rating: 4,
        image: "https://placehold.co/300x300?text=Honey+Bread",
    },
];

const handleApiFallback = (error, fallbackValue) => {
    console.warn("API unavailable, using local fallback data.", error.message);
    return { data: fallbackValue };
};

// Get all products
export const getProducts = async () => {
    try {
        return await api.get("products/");
    } catch (error) {
        return handleApiFallback(error, fallbackProducts);
    }
};

// Get one product
export const getProduct = async (id) => {
    try {
        return await api.get(`products/${id}/`);
    } catch (error) {
        const product = fallbackProducts.find((item) => item.id === Number(id));
        return handleApiFallback(error, product || fallbackProducts[0]);
    }
};

// Create product with image
export const createProduct = (formData) => {
    return api.post("products/", formData, {
        headers: {
            "Content-Type": "multipart/form-data",
        },
    });
};

// Update product with image
export const updateProduct = (id, formData) => {
    return api.put(`products/${id}/`, formData, {
        headers: {
            "Content-Type": "multipart/form-data",
        },
    });
};

// Delete product
export const deleteProduct = (id) => {
    return api.delete(`products/${id}/`);
};
