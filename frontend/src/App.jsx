import { useState, useCallback } from "react";
import SearchBar from "./components/SearchBar";
import UserInfo from "./components/UserInfo";
import ProblemList from "./components/ProblemList";
import TopicsList from "./components/TopicsList";
import Spinner from "./components/Spinner";
import ErrorMessage from "./components/ErrorMessage";
import InfoBanner from "./components/InfoBanner";
import { fetchRecommendations } from "./api";
import "./App.css";

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastHandle, setLastHandle] = useState(null);

  const handleSearch = useCallback(async (handle) => {
    setLoading(true);
    setError(null);
    setData(null);
    setLastHandle(handle);

    try {
      const result = await fetchRecommendations(handle);
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  // Re-fetch with the same handle to get a new set of problems (#22)
  const handleRefresh = useCallback(() => {
    if (lastHandle) {
      handleSearch(lastHandle);
    }
  }, [lastHandle, handleSearch]);

  const handleRetry = useCallback(() => {
    if (lastHandle) {
      handleSearch(lastHandle);
    }
  }, [lastHandle, handleSearch]);

  return (
    <div className="app-wrapper">
      <div className="container">
        {/* Header */}
        <header className="header-card">
          <h1>
            <span className="logo-icon">&lt;/&gt;</span>
            Codeforces Problem Recommender
          </h1>
          <p>Get personalized problem recommendations based on your Codeforces profile</p>
        </header>

        {/* Info banner — always visible */}
        <InfoBanner />

        {/* Search */}
        <div className="search-card">
          <SearchBar onSearch={handleSearch} loading={loading} />
        </div>

        {/* Results area */}
        <div id="result">
          {loading && <Spinner />}

          {error && <ErrorMessage message={error} onRetry={handleRetry} />}

          {data && (
            <>
              <UserInfo userInfo={data.user_info} />
              <ProblemList
                problems={data.recommended_problems}
                onRefresh={handleRefresh}
              />
              <TopicsList
                title="Important Topics"
                topics={data.important_topics}
              />
              {data.struggle_topics && data.struggle_topics.length > 0 && (
                <TopicsList
                  title="Topics to Focus On"
                  topics={data.struggle_topics}
                />
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
