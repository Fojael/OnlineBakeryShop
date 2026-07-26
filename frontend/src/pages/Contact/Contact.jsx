import { useState } from "react";

const Contact = () => {
    const [contactData, setContactData] = useState({
        name: "",
        email: "",
        subject: "",
        message: "",
    });

    const handleChange = (e) => {
        setContactData({
            ...contactData,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = (e) => {
        e.preventDefault();

        // Later connect with Django API
        console.log(contactData);

        alert("Your message has been sent successfully!");

        setContactData({
            name: "",
            email: "",
            subject: "",
            message: "",
        });
    };

    return (
        <div className="container py-5">

            {/* Page Title */}
            <div className="text-center mb-5">
                <h1>Contact Us</h1>
                <p className="lead">
                    We'd love to hear from you.
                </p>
            </div>

            <div className="row">

                {/* Contact Form */}
                <div className="col-lg-7 mb-4">

                    <div className="card shadow p-4">

                        <h3 className="mb-4">
                            Send Us a Message
                        </h3>

                        <form onSubmit={handleSubmit}>

                            <div className="mb-3">
                                <label className="form-label">
                                    Full Name
                                </label>

                                <input
                                    type="text"
                                    className="form-control"
                                    name="name"
                                    value={contactData.name}
                                    onChange={handleChange}
                                    placeholder="Enter your name"
                                    required
                                />
                            </div>

                            <div className="mb-3">
                                <label className="form-label">
                                    Email Address
                                </label>

                                <input
                                    type="email"
                                    className="form-control"
                                    name="email"
                                    value={contactData.email}
                                    onChange={handleChange}
                                    placeholder="Enter your email"
                                    required
                                />
                            </div>

                            <div className="mb-3">
                                <label className="form-label">
                                    Subject
                                </label>

                                <input
                                    type="text"
                                    className="form-control"
                                    name="subject"
                                    value={contactData.subject}
                                    onChange={handleChange}
                                    placeholder="Enter the subject"
                                    required
                                />
                            </div>

                            <div className="mb-4">
                                <label className="form-label">
                                    Message
                                </label>

                                <textarea
                                    className="form-control"
                                    rows="5"
                                    name="message"
                                    value={contactData.message}
                                    onChange={handleChange}
                                    placeholder="Write your message"
                                    required
                                />
                            </div>

                            <button
                                type="submit"
                                className="btn btn-primary w-100"
                            >
                                Send Message
                            </button>

                        </form>

                    </div>

                </div>


                {/* Contact Information */}
                <div className="col-lg-5">

                    <div className="card shadow p-4 mb-4">

                        <h3 className="mb-4">
                            Contact Information
                        </h3>

                        <p>
                            <strong>Address:</strong><br />
                            House 12, Road 5,<br />
                            Dhaka, Bangladesh
                        </p>

                        <p>
                            <strong>Phone:</strong><br />
                            +880 1700-000000
                        </p>

                        <p>
                            <strong>Email:</strong><br />
                            info@bakemaster.com
                        </p>

                        <p>
                            <strong>Working Hours:</strong><br />
                            Saturday - Thursday<br />
                            9:00 AM - 9:00 PM
                        </p>

                    </div>


                    {/* Google Map */}
                    <div className="card shadow p-4">

                        <h3 className="mb-3">
                            Find Us
                        </h3>

                        <div className="ratio ratio-16x9">
                            <iframe
                                title="Google Map"
                                src="https://www.google.com/maps?q=Dhaka,Bangladesh&output=embed"
                                allowFullScreen=""
                                loading="lazy"
                            ></iframe>
                        </div>

                    </div>

                </div>

            </div>

        </div>
    );
};

export default Contact;