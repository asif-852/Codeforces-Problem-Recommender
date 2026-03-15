# Codeforces Problem Recommender — Frontend

This is the React + Vite frontend for the Codeforces Problem Recommender. It communicates with the Django REST backend to display personalized problem recommendations.

## Tech Stack

- **React 19** — UI library
- **Vite 8** — Build tool and development server (with HMR)
- **ESLint** — Code linting

## Development

### Prerequisites

- Node.js 18+
- npm

### Setup

```bash
# From the frontend/ directory
npm install
npm run dev
```

The dev server starts on **http://localhost:3000** and proxies all `/api/*` requests to the Django backend at `http://127.0.0.1:8000`.

### Available Scripts

| Script | Description |
|--------|-------------|
| `npm run dev` | Start development server with HMR |
| `npm run build` | Build for production (outputs to `dist/`) |
| `npm run preview` | Preview the production build locally |
| `npm run lint` | Run ESLint |

## Components

| Component | Description |
|-----------|-------------|
| `App.jsx` | Root component; manages global state and orchestrates API calls |
| `SearchBar.jsx` | Handles input with client-side validation |
| `UserInfo.jsx` | Displays user profile (handle, rating, rank, skill group) |
| `ProblemList.jsx` | Renders the list of 6 recommended problems with links |
| `TopicsList.jsx` | Shows important topics for the user's skill group |
| `ErrorMessage.jsx` | Displays API or validation errors |
| `Spinner.jsx` | Loading indicator shown during API requests |
