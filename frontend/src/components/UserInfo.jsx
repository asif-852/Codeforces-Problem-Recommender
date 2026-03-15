function UserInfo({ userInfo }) {
  if (!userInfo) return null;

  return (
    <div className="user-info">
      <h2>User Info</h2>
      <p>
        <strong>Handle:</strong> {userInfo.handle}
      </p>
      <p>
        <strong>Rating:</strong> {userInfo.rating ?? "Unrated"}
      </p>
      <p>
        <strong>Rank:</strong> {userInfo.rank ?? "Unranked"}
      </p>
    </div>
  );
}

export default UserInfo;
