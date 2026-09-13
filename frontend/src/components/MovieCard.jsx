function releaseYear(releaseDate) {
  return releaseDate ? String(releaseDate).slice(0, 4) : null
}

export default function MovieCard({ movie }) {
  const matchScore = movie.match_score ?? movie.similarity ?? 0
  const genres = Array.isArray(movie.genres) ? movie.genres.join(' · ') : movie.genres
  const overview = movie.overview || 'Details for this recommendation are not currently available.'
  const year = releaseYear(movie.release_date)

  return <article className="movie-card"><div className="poster-wrap">{movie.poster_url ? <img className="movie-poster" src={movie.poster_url} alt={`${movie.title} poster`} loading="lazy" /> : <div className="poster-placeholder" role="img" aria-label={`No poster available for ${movie.title}`}><span>CM</span><small>No poster available</small></div>}<div className="score">{Math.round(matchScore * 100)}% match</div></div><div className="movie-copy"><h3>{movie.title}</h3>{genres && <p className="genres">{genres}</p>}<p className="movie-meta">{year && <span>{year}</span>}{year && movie.rating != null && <i>•</i>}{movie.rating != null && <span>★ {Number(movie.rating).toFixed(1)}</span>}</p><p className="overview">{overview}</p></div></article>
}
