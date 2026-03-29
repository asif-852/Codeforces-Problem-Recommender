function UserInfo({ userInfo }) {
  if (!userInfo) return null;

  const rating = userInfo.rating;
  const rank   = userInfo.rank;

  return (
    <div className="card">
      <h2 className="section-heading">User Info</h2>

      <div className="user-stats-grid">
        <div className="stat-cell">
          <span className="stat-label">Handle</span>
          <span className="stat-value">{userInfo.handle}</span>
        </div>

        <div className="stat-cell">
          <span className="stat-label">Rating</span>
          <span
            className={`stat-value ${
              rating ? "stat-value--rating" : "stat-value--unrated"
            }`}
          >
            {rating ?? "Unrated"}
          </span>
        </div>

        <div className="stat-cell">
          <span className="stat-label">Rank</span>
          <span
            className={`stat-value ${
              rank ? "stat-value--rank" : "stat-value--unrated"
            }`}
          >
            {rank ?? "Unranked"}
          </span>
        </div>
      </div>
    </div>
  );
}

export default UserInfo;
