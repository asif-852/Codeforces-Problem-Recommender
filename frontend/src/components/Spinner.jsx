function Spinner({ message = "Fetching recommendations…" }) {
  return (
    <div className="spinner-container" role="status" aria-live="polite">
      <div className="spinner" />
      <p className="spinner-message">{message}</p>
    </div>
  );
}

export default Spinner;
