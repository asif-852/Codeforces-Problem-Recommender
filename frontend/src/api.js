const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api";

export async function fetchRecommendations(handle) {
  const response = await fetch(
    `${API_BASE}/recommend/${encodeURIComponent(handle)}/`
  );

  if (!response.ok) {
    // Try to extract error message from JSON response body
    let serverMessage = null;
    try {
      const body = await response.json();
      serverMessage = body.error;
    } catch {
      // Response wasn't JSON, fall through to default messages
    }

    if (serverMessage) {
      throw new Error(serverMessage);
    }

    if (response.status === 400) {
      throw new Error("Invalid handle. Please check your input.");
    } else if (response.status === 404) {
      throw new Error(
        "User not found. Please check the handle and try again."
      );
    } else if (response.status === 500) {
      throw new Error(
        "Server error: Unable to fetch recommendations. Please try again later."
      );
    } else {
      throw new Error(`Error ${response.status}: ${response.statusText}`);
    }
  }

  const contentType = response.headers.get("content-type");
  if (!contentType || !contentType.includes("application/json")) {
    throw new Error("Invalid response format: Expected JSON.");
  }

  const data = await response.json();

  if (data.error) {
    throw new Error(data.error);
  }

  return data;
}
