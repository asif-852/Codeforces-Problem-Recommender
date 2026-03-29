/**
 * TopicsList — renders a list of topics as pill badges instead of a <ul>.
 *
 * Props:
 *   title  — section heading text
 *   topics — array of topic strings
 */
function TopicsList({ title, topics }) {
  if (!topics || topics.length === 0) return null;

  return (
    <div className="card">
      <h2 className="section-heading">{title}</h2>
      <div className="topics-pills">
        {topics.map((topic) => (
          <span key={topic} className="tag-pill">{topic}</span>
        ))}
      </div>
    </div>
  );
}

export default TopicsList;
