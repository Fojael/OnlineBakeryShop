import Navbar from "../components/Navbar/Navbar";
import Footer from "../components/Footer/Footer";

const MainLayout = ({ children }) => {
    return (
        <>
            <Navbar />

            <main>
                {children}
            </main>

            <Footer />
        </>
    );
};

export default MainLayout;