"""Content-based movie recommender backed by the project's preserved movie data."""

from __future__ import annotations

import pickle
import re
import sys
import types
import zipfile
from io import BytesIO
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class MovieNotFoundError(LookupError):
    """Raised when a requested title is not in the catalogue."""


class MovieRecommender:
    """Load the legacy processed catalogue once and provide sparse TF-IDF matches."""

    def __init__(self) -> None:
        root = Path(__file__).resolve().parents[1]
        self._data_path = root / "models" / "ew.pickle"
        self._archive_path = root / "models" / "pickle.zip"
        self.movies = self._load_movies()
        self.vectorizer = TfidfVectorizer(stop_words="english", max_features=12_000)
        self.matrix = self.vectorizer.fit_transform(self.movies["features"])
        self._title_index = {self._normalise(title): index for index, title in enumerate(self.movies["title"])}

    @staticmethod
    def _normalise(title: str) -> str:
        return re.sub(r"\s+", " ", title.strip()).casefold()

    def _load_movies(self) -> pd.DataFrame:
        # Pandas 2 removed this module name used by the preserved pandas-1.x
        # dataframe pickle. Supplying the compatible Index aliases lets us read
        # the legacy data without modifying it on disk.
        legacy_indexes = types.ModuleType("pandas.core.indexes.numeric")
        legacy_indexes.Int64Index = pd.Index
        legacy_indexes.UInt64Index = pd.Index
        legacy_indexes.Float64Index = pd.Index
        sys.modules.setdefault("pandas.core.indexes.numeric", legacy_indexes)
        if self._data_path.exists():
            with self._data_path.open("rb") as source:
                raw = pickle.load(source)
        elif self._archive_path.exists():
            # The repository stores legacy artifacts in a zip to avoid loose,
            # duplicate large files. Read it in memory; never alter the archive.
            with zipfile.ZipFile(self._archive_path) as archive:
                raw = pickle.load(BytesIO(archive.read("ew.pickle")))
        else:
            raise FileNotFoundError(f"Movie catalogue was not found at {self._data_path} or {self._archive_path}.")
        if not isinstance(raw, pd.DataFrame) or "title" not in raw.columns:
            raise ValueError("models/ew.pickle does not contain a valid movie dataframe.")
        data = raw.copy()
        data["title"] = data["title"].fillna("").astype(str).str.strip()
        feature_column = "tags" if "tags" in data.columns else "overview"
        if feature_column not in data.columns:
            data[feature_column] = ""
        data["features"] = data[feature_column].fillna("").astype(str)
        data = data[data["title"].ne("")].drop_duplicates(subset="title", keep="first").reset_index(drop=True)
        if data.empty:
            raise ValueError("The movie catalogue has no usable titles.")
        return data

    def search(self, query: str = "", limit: int = 100) -> list[str]:
        query = self._normalise(query)
        titles = self.movies["title"].tolist()
        if query:
            titles = [title for title in titles if query in self._normalise(title)]
        return sorted(titles, key=str.casefold)[:max(1, min(limit, 500))]

    def recommendations(self, title: str, limit: int = 6) -> tuple[str, list[dict[str, object]]]:
        index = self._title_index.get(self._normalise(title))
        if index is None:
            raise MovieNotFoundError(title)
        scores = cosine_similarity(self.matrix[index], self.matrix).ravel()
        results = []
        for candidate in scores.argsort()[::-1]:
            if candidate == index:
                continue
            row = self.movies.iloc[int(candidate)]
            results.append(self._movie_payload(row, float(scores[candidate])))
            if len(results) == max(1, min(limit, 20)):
                break
        return str(self.movies.iloc[index]["title"]), results

    @staticmethod
    def _movie_payload(row: pd.Series, score: float) -> dict[str, object]:
        def optional_text(*columns: str) -> str | None:
            for column in columns:
                value = row.get(column)
                if pd.notna(value) and str(value).strip():
                    return str(value).strip()
            return None
        rating = row.get("vote_average")
        return {"title": str(row["title"]), "genres": optional_text("genres"),
                "overview": optional_text("overview"),
                "rating": float(rating) if pd.notna(rating) else None,
                "similarity": round(score, 3)}
