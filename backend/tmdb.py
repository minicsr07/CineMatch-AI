"""Optional TMDB v3 metadata enrichment for recommendation results."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen


TMDB_API_URL = "https://api.themoviedb.org/3"
POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"


def _load_local_env() -> None:
    """Read backend/.env without adding a dependency or overriding real env vars."""
    env_file = Path(__file__).resolve().parent / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


class TMDBClient:
    """Small fault-tolerant client; no key means enrichment is simply skipped."""

    def __init__(self) -> None:
        _load_local_env()
        self.api_key = os.getenv("TMDB_API_KEY", "").strip()

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def _get(self, path: str, **params: str | int) -> dict[str, object] | None:
        if not self.enabled:
            return None
        query = urlencode({"api_key": self.api_key, **params})
        try:
            with urlopen(f"{TMDB_API_URL}{path}?{query}", timeout=2.5) as response:
                return json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, OSError):
            return None

    @lru_cache(maxsize=1024)
    def movie_metadata(self, title: str) -> dict[str, object]:
        """Return normalized metadata for TMDB's best title match, or an empty dict."""
        search = self._get("/search/movie", query=title, include_adult="false")
        if not search or not isinstance(search.get("results"), list) or not search["results"]:
            return {}
        match = search["results"][0]
        if not isinstance(match, dict):
            return {}
        movie_id = match.get("id")
        details = self._get(f"/movie/{movie_id}") if movie_id else None
        source = details if isinstance(details, dict) else match
        poster_path = source.get("poster_path") or match.get("poster_path")
        genres = source.get("genres", [])
        genre_names = [genre.get("name") for genre in genres if isinstance(genre, dict) and genre.get("name")]
        return {
            "title": source.get("title") or match.get("title") or title,
            "poster_url": f"{POSTER_BASE_URL}{poster_path}" if poster_path else None,
            "overview": source.get("overview") or match.get("overview") or None,
            "release_date": source.get("release_date") or match.get("release_date") or None,
            "rating": source.get("vote_average", match.get("vote_average")),
            "genres": genre_names or None,
            "tmdb_id": source.get("id") or match.get("id"),
        }

    def enrich(self, recommendation: dict[str, object]) -> dict[str, object]:
        """Merge optional remote data without ever replacing a usable local value."""
        enriched = {**recommendation, "match_score": recommendation.get("similarity"), "poster_url": None, "release_date": None, "tmdb_id": None}
        metadata = self.movie_metadata(str(recommendation["title"]))
        if not metadata:
            return enriched
        for key, value in metadata.items():
            if value is not None:
                enriched[key] = value
        return enriched
