import { useState, useCallback } from "react";
import SearchBar from "./components/SearchBar";
import UserInfo from "./components/UserInfo";
import ProblemList from "./components/ProblemList";
import TopicsList from "./components/TopicsList";
import Spinner from "./components/Spinner";
import ErrorMessage from "./components/ErrorMessage";
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

  const handleRetry = useCallback(() => {
    if (lastHandle) {
      handleSearch(lastHandle);
    }
  }, [lastHandle, handleSearch]);

  return (
    <div className="container">
      <h1>Codeforces Problem Recommender</h1>
      <SearchBar onSearch={handleSearch} loading={loading} />

      <div id="result">
        {loading && <Spinner />}

        {error && <ErrorMessage message={error} onRetry={handleRetry} />}

        {data && (
          <>
            <UserInfo userInfo={data.user_info} />
            <ProblemList problems={data.recommended_problems} />
            <TopicsList
              title="Important Topics"
              topics={data.important_topics}
            />
            <TopicsList
              title="Topics to Focus On"
              topics={data.struggle_topics}
            />
          </>
        )}
      </div>
    </div>
  );
}

export default App;
