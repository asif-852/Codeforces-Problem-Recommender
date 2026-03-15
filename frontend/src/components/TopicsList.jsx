function TopicsList({ title, topics }) {
  if (!topics || topics.length === 0) return null;

  return (
    <div className="topics-list">
      <h2>{title}</h2>
      <ul>
        {topics.map((topic) => (
          <li key={topic}>{topic}</li>
        ))}
      </ul>
    </div>
  );
}

export default TopicsList;
