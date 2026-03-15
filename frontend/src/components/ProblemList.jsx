function ProblemList({ problems }) {
  if (!problems || problems.length === 0) return null;

  return (
    <div className="problem-list">
      <h2>Recommended Problems</h2>
      <ul>
        {problems.map((problem) => (
          <li key={`${problem.contestId}-${problem.index}`}>
            <a
              href={`https://codeforces.com/problemset/problem/${problem.contestId}/${problem.index}`}
              target="_blank"
              rel="noopener noreferrer"
            >
              {problem.name} (Rating: {problem.rating})
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default ProblemList;
