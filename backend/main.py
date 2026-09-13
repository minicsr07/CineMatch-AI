"""FastAPI entry point for the AI Movie Recommendation System."""

from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .recommender import MovieNotFoundError, MovieRecommender
from .tmdb import TMDBClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.recommender = MovieRecommender()
    app.state.tmdb = TMDBClient()
    yield


app = FastAPI(title="AI Movie Recommendation API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "https://frontend-one-rho-68.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/movies")
def movies(q: Annotated[str, Query(description="Case-insensitive title search")] = "", limit: Annotated[int, Query(ge=1, le=500)] = 100) -> dict[str, object]:
    titles = app.state.recommender.search(q, limit)
    return {"count": len(titles), "movies": titles}


@app.get("/recommendations/{movie_title}")
def recommendations(movie_title: str, limit: Annotated[int, Query(ge=1, le=20)] = 6) -> dict[str, object]:
    try:
        selected_title, results = app.state.recommender.recommendations(movie_title, limit)
    except MovieNotFoundError:
        raise HTTPException(status_code=404, detail=f"Movie '{movie_title}' was not found.") from None
    enriched_results = [app.state.tmdb.enrich(result) for result in results]
    return {"selected_movie": selected_title, "count": len(enriched_results), "recommendations": enriched_results}
