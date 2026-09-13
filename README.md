# CineMatch AI — Movie Recommendation System

CineMatch AI is a modern full-stack content-based movie recommender. A FastAPI service turns the project's preserved TMDB-derived movie catalogue into TF-IDF vectors, compares them with cosine similarity, and serves recommendations to a responsive React/Vite interface.

## Problem statement

Large movie catalogues make finding a relevant next film difficult. This project recommends movies with similar textual attributes—plot, genres, keywords, cast, and crew—after a viewer chooses a title.

## Features

- Searchable title selector with debounced API search
- Six nearest recommendations, always excluding the selected movie
- Case-insensitive lookup, URL-safe titles, helpful 404 responses
- Robust catalogue cleaning: missing titles/features and duplicate titles are handled before training
- Startup-only TF-IDF build; requests compare only the chosen sparse vector
- FastAPI health and catalogue endpoints, CORS for local Vite development
- Responsive React UI with loading, empty, and error states

## ML approach

The retained `models/ew.pickle` dataframe is a processed artifact from the original TMDB workflow. Its `tags` column combines overview, genre, keyword, cast, and director tokens. The API cleans this data and uses **TF-IDF** (term frequency weighted by how rare a word is across the catalogue) to convert each movie's text into a sparse numerical vector. **Cosine similarity** measures the angle between the selected movie vector and each other vector; a higher score means more similar content, regardless of text length.

The original raw TMDB CSV is not included in this repository, so it is not downloaded or substituted. The original processed dataframe and legacy Django/notebook assets are preserved.

## Architecture

```
React + Vite  →  FastAPI endpoints  →  TF-IDF sparse matrix  →  TMDB-derived artifact
```

`backend/recommender.py` resolves artifact paths relative to its own file, so it works from any terminal directory. The Django application remains as preserved legacy code; the modern app uses FastAPI and React.

## Project structure

```
backend/                 FastAPI API and recommendation engine
frontend/                Vite React single-page application
models/ew.pickle         preserved processed movie catalogue
notebooks/               presentation-ready ML walkthrough
ipynb/                   original project notebook (preserved)
MovieRecommendation/, predict/  legacy Django application (preserved)
```

## Installation and running

Prerequisites: Python 3.10+ and Node.js 18+.

Start the backend from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
uvicorn backend.main:app --reload
```

Start the frontend in a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the address printed by Vite (normally `http://localhost:5173`). Set `VITE_API_URL` in `frontend/.env` only when the API is hosted somewhere other than `http://127.0.0.1:8000`.

## API endpoints

| Endpoint | Purpose |
| --- | --- |
| `GET /health` | Returns API health status. |
| `GET /movies?q=dark&limit=8` | Searches available movie titles. |
| `GET /recommendations/The%20Dark%20Knight?limit=6` | Returns similar movies and available metadata. |

Example:

```powershell
Invoke-RestMethod 'http://127.0.0.1:8000/recommendations/Avatar'
```

## Notebook

Open `notebooks/movie_recommendation.ipynb` for a presentation-friendly walkthrough: loading, inspection, missing/duplicate analysis, cleaning, feature engineering, TF-IDF, cosine similarity, examples, and lightweight validation.

## Future improvements

- Restore raw TMDB CSVs to surface rich overview, rating, and genre metadata directly.
- Add posters, user accounts, favourites, and feedback-based ranking.
- Persist vectorizer artifacts or use approximate nearest-neighbour search for much larger catalogues.
- Combine content similarity with collaborative filtering.
