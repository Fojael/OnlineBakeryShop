const About = () => {
    return (
        <div className="container py-5">

            {/* Page Title */}
            <div className="text-center mb-5">
                <h1>About Our Bakery</h1>
                <p className="lead">
                    Freshly baked happiness delivered to your doorstep.
                </p>
            </div>


            {/* About Section */}
            <div className="card shadow p-4 mb-4">
                <h3>Who We Are</h3>

                <p>
                    Welcome to BakeMaster AI Bakery Shop. We are
                    passionate about creating delicious and
                    high-quality bakery products for our customers.
                </p>

                <p>
                    Our bakery offers a wide range of cakes,
                    pastries, cupcakes, cookies, bread, and other
                    freshly baked items made with premium
                    ingredients.
                </p>
            </div>


            {/* Mission Section */}
            <div className="card shadow p-4 mb-4">
                <h3>Our Mission</h3>

                <p>
                    Our mission is to provide fresh, healthy,
                    and delicious bakery products while offering
                    a convenient online shopping experience for
                    customers.
                </p>
            </div>


            {/* Why Choose Us */}
            <div className="card shadow p-4 mb-4">
                <h3>Why Choose Us?</h3>

                <ul>
                    <li>Freshly baked products every day.</li>
                    <li>Premium quality ingredients.</li>
                    <li>Easy online ordering system.</li>
                    <li>Fast and reliable delivery service.</li>
                    <li>Secure online payment options.</li>
                    <li>AI-based product recommendations.</li>
                </ul>
            </div>


            {/* Products Section */}
            <div className="card shadow p-4 mb-4">
                <h3>Our Products</h3>

                <ul>
                    <li>Cakes</li>
                    <li>Cupcakes</li>
                    <li>Cookies</li>
                    <li>Pastries</li>
                    <li>Bread</li>
                    <li>Donuts</li>
                    <li>Custom Birthday Cakes</li>
                </ul>
            </div>


            {/* Services Section */}
            <div className="card shadow p-4 mb-4">
                <h3>Our Services</h3>

                <ul>
                    <li>Online Bakery Ordering</li>
                    <li>Home Delivery</li>
                    <li>Custom Cake Orders</li>
                    <li>Special Occasion Cakes</li>
                    <li>Secure Payment System</li>
                    <li>Order Tracking</li>
                </ul>
            </div>


            {/* Closing Section */}
            <div className="card shadow p-4">
                <h3>Thank You</h3>

                <p>
                    Thank you for choosing BakeMaster AI Bakery
                    Shop. We are committed to making every
                    celebration sweeter with our freshly baked
                    products and exceptional customer service.
                </p>
            </div>

        </div>
    );
};

export default About;