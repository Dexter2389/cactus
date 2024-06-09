import styles from './fileupload.module.css'
const Upload = () => {
    return(
        <>
            <label for="actual-btn" className={styles.upload}>
                <h3>Drop Video or click to browse files</h3>
            </label>
            <input type="file" id="actual-btn" hidden/>

        </>
    )
}
export default Upload
