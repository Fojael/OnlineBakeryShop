import PropTypes from "prop-types";


const SupplierStatCard = ({
    title,
    value,
    icon,
    description,
    iconClass = "text-primary",
}) => {

    return (

        <div className="card border-0 shadow-sm h-100">

            <div className="card-body">

                <div className="d-flex justify-content-between align-items-start">

                    <div>

                        <p className="text-muted mb-2">
                            {title}
                        </p>

                        <h3 className="fw-bold mb-2">
                            {value}
                        </h3>

                        {description && (

                            <small className="text-muted">
                                {description}
                            </small>

                        )}

                    </div>


                    <div
                        className={`fs-2 ${iconClass}`}
                    >
                        <i className={icon}></i>
                    </div>

                </div>

            </div>

        </div>

    );
};


SupplierStatCard.propTypes = {

    title: PropTypes.string.isRequired,

    value: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.number,
    ]).isRequired,

    icon: PropTypes.string.isRequired,

    description: PropTypes.string,

    iconClass: PropTypes.string,

};


export default SupplierStatCard;