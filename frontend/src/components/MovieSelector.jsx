import { useEffect, useState } from 'react'

export default function MovieSelector({ apiBaseUrl, selectedMovie, onSelect, onRecommend, loadingRecommendations }) {
  const [query, setQuery] = useState('')
  const [movies, setMovies] = useState([])
  const [open, setOpen] = useState(false)
  const [movieStatus, setMovieStatus] = useState('loading')

  useEffect(() => {
    const controller = new AbortController()
    const timer = setTimeout(async () => {
      setMovieStatus(query ? 'searching' : 'loading')
      try {
        const search = query ? `?q=${encodeURIComponent(query)}&limit=8` : '?limit=8'
        const response = await fetch(`${apiBaseUrl}/movies${search}`, { signal: controller.signal })
        if (!response.ok) throw new Error('Movie catalogue could not be loaded.')
        const body = await response.json()
        setMovies(Array.isArray(body.movies) ? body.movies : [])
        setMovieStatus('ready')
      } catch (error) {
        if (error.name !== 'AbortError') { setMovies([]); setMovieStatus('unavailable') }
      }
    }, query ? 180 : 0)
    return () => { controller.abort(); clearTimeout(timer) }
  }, [apiBaseUrl, query])

  function pick(title) { onSelect(title); setQuery(title); setOpen(false) }
  function changeQuery(event) { setQuery(event.target.value); onSelect(''); setOpen(true) }
  const dropdownMessage = movieStatus === 'loading' ? 'Loading movies…' : movieStatus === 'searching' ? 'Searching movies…' : movieStatus === 'unavailable' ? 'Movie catalogue is unavailable.' : movies.length === 0 ? 'No matching movies.' : null

  return <div className="selector"><label htmlFor="movie-search">Choose a movie</label><div className="search-row"><div className="search-box"><input id="movie-search" value={query} placeholder="Try “The Dark Knight”" onChange={changeQuery} onFocus={() => setOpen(true)} onKeyDown={event => event.key === 'Enter' && selectedMovie && onRecommend()} />{open && <div className="suggestions">{dropdownMessage ? <p className="suggestion-status">{dropdownMessage}</p> : <ul>{movies.map(movie => <li key={movie}><button type="button" onMouseDown={() => pick(movie)}>{movie}</button></li>)}</ul>}</div>}</div><button type="button" className="recommend-button" disabled={!selectedMovie || loadingRecommendations} onClick={onRecommend}>{loadingRecommendations ? 'Finding…' : 'Recommend movies'}</button></div>{selectedMovie ? <p className="selection">Selected: <strong>{selectedMovie}</strong></p> : <p className="selection">Select a title from the matching movies to continue.</p>}</div>
}
