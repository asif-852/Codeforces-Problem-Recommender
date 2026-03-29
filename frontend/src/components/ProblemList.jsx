// Refresh icon SVG — no extra dependency needed
function RefreshIcon() {
  return (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <polyline points="23 4 23 10 17 10" />
      <polyline points="1 20 1 14 7 14" />
      <path d="M3.51 9a9 9 0 0114.36-3.36L23 10M1 14l5.13 4.36A9 9 0 0020.49 15" />
    </svg>
  );
}

/**
 * ProblemList — displays recommended problems in a 2-column card grid.
 *
 * Props:
 *   problems  — array of problem objects from the API
 *   onRefresh — callback to fetch a new set of problems (#22)
 */
function ProblemList({ problems, onRefresh }) {
  if (!problems || problems.length === 0) return null;

  return (
    <div className="card">
      <h2 className="section-heading">Recommended Problems</h2>

      {/* 2-col grid; drops to 1-col on mobile via CSS */}
      <div className="problem-grid">
        {problems.map((problem, index) => {
          const problemUrl = `https://codeforces.com/problemset/problem/${problem.contestId}/${problem.index}`;
          const problemId  = `${problem.contestId}${problem.index}`;
          const tags       = problem.tags ?? [];

          return (
            <div
              key={`${problem.contestId}-${problem.index}`}
              className="problem-card"
            >
              {/* Numbered badge */}
              <div className="problem-badge" aria-label={`Problem ${index + 1}`}>
                {index + 1}
              </div>

              <div className="problem-body">
                {/* Problem name as a link */}
                <a
                  href={problemUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="problem-name"
                >
                  {problem.name}
                </a>

                {/* Contest ID + rating */}
                <div className="problem-meta">
                  <span className="problem-id">{problemId}</span>
                  {problem.rating && (
                    <span className="problem-rating">{problem.rating}</span>
                  )}
                </div>

                {/* Tags (#23) — only shown when present */}
                {tags.length > 0 && (
                  <div className="problem-tags" aria-label="Problem tags">
                    {tags.map((tag) => (
                      <span key={tag} className="tag-pill">{tag}</span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Refresh / New Problems button (#22) */}
      {onRefresh && (
        <div className="refresh-row">
          <button
            className="refresh-btn"
            onClick={onRefresh}
            type="button"
            aria-label="Get a new set of recommended problems"
          >
            <RefreshIcon />
            Get New Problems
          </button>
        </div>
      )}
    </div>
  );
}

export default ProblemList;
