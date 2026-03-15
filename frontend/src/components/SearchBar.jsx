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
        <input
          type="text"
          value={handle}
          onChange={handleChange}
          placeholder="Enter Codeforces handle"
          disabled={loading}
          maxLength={HANDLE_MAX_LENGTH}
          aria-invalid={!!validationError}
        />
        {validationError && (
          <span className="validation-error">{validationError}</span>
        )}
      </div>
      <button type="submit" disabled={loading || !handle.trim()}>
        {loading ? "Loading..." : "Get Recommendations"}
      </button>
    </form>
  );
}

export default SearchBar;
