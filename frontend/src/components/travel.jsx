import styles from './travel.module.css'
const Travel = ({ data }) => {
    return (
        <div className={styles.travel}>
            <h2>{data.title}</h2>
            <h3>Itinerary</h3>
            <ul className="itinerary">
                {data.itinerary.map((city, index) => (
                    <li key={index}>{city}</li>
                ))}
            </ul>
            <h3>Hashtags</h3>
            <ul className="hashtags">
                {data.hashtags.map((hash, index) => (
                    <li key={index}>{hash}</li>
                ))}
            </ul>
            <video width="320" height="240" controls>
                <source src={data.reel_file} type="video/mp4" />
                Your browser does not support the video tag.
            </video>
        </div>
    );
};

export default Travel;
