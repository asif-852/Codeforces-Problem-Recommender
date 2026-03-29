import { useState } from "react";

const HANDLE_MAX_LENGTH = 24;
const HANDLE_REGEX = /^[a-zA-Z0-9_-]+$/;

function validateHandle(handle) {
  if (!handle || !handle.trim()) {
    return "Handle cannot be empty.";
  }
  if (handle.length > HANDLE_MAX_LENGTH) {
    return `Handle must be at most ${HANDLE_MAX_LENGTH} characters.`;
  }
  if (!HANDLE_REGEX.test(handle)) {
    return "Handle can only contain letters, digits, underscores, and hyphens.";
  }
  return null;
}

// Inline SVG search icon — no extra dependency needed
function SearchIcon() {
  return (
    <svg
      className="search-icon"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <circle cx="11" cy="11" r="8" />
      <line x1="21" y1="21" x2="16.65" y2="16.65" />
    </svg>
  );
}

function SearchBar({ onSearch, loading }) {
  const [handle, setHandle] = useState("");
  const [validationError, setValidationError] = useState(null);

  const handleChange = (e) => {
    const value = e.target.value;
    setHandle(value);
    if (validationError) {
      setValidationError(validateHandle(value.trim()));
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = handle.trim();
    const error = validateHandle(trimmed);
    if (error) {
      setValidationError(error);
      return;
    }
    setValidationError(null);
    onSearch(trimmed);
  };

  return (
    <form className="search-bar" onSubmit={handleSubmit}>
      <div className="search-input-wrapper">
        <div className="input-icon-wrapper">
          <SearchIcon />
          <input
            type="text"
            value={handle}
            onChange={handleChange}
            placeholder="Enter Codeforces handle"
            disabled={loading}
            maxLength={HANDLE_MAX_LENGTH}
            aria-invalid={!!validationError}
            aria-label="Codeforces handle"
          />
        </div>
        {validationError && (
          <span className="validation-error" role="alert">
            {validationError}
          </span>
        )}
      </div>

      <button type="submit" disabled={loading || !handle.trim()}>
        {loading ? "Loading…" : "Get Recommendations →"}
      </button>
    </form>
  );
}

export default SearchBar;
