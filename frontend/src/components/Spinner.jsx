function Spinner({ message = "Fetching recommendations..." }) {
  return (
    <div className="spinner-container">
      <div className="spinner" />
      <p className="spinner-message">{message}</p>
    </div>
  );
}

export default Spinner;
