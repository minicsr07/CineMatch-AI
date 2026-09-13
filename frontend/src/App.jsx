import { useState } from 'react'
import MovieSelector from './components/MovieSelector'
import Recommendations from './components/Recommendations'
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
export default function App() {
  const [selectedMovie, setSelectedMovie] = useState(''), [results, setResults] = useState(null), [loadingRecommendations, setLoadingRecommendations] = useState(false), [recommendationError, setRecommendationError] = useState('')
  async function recommend() { if (!selectedMovie) return; setLoadingRecommendations(true); setRecommendationError(''); setResults(null); try { const response = await fetch(`${API_BASE_URL}/recommendations/${encodeURIComponent(selectedMovie)}`); const body = await response.json(); if (!response.ok) throw new Error(body.detail || 'Recommendations could not be loaded.'); setResults(body) } catch (error) { setRecommendationError(error.message || 'The recommendation API is unavailable.') } finally { setLoadingRecommendations(false) } }
  return <main className="page"><section className="hero"><p className="eyebrow">CONTENT-BASED DISCOVERY</p><h1>Find your next <em>great</em> movie.</h1><p className="intro">CineMatch AI reads movie descriptions, genres, cast, crew and keywords to uncover films with a similar feel.</p><MovieSelector apiBaseUrl={API_BASE_URL} selectedMovie={selectedMovie} onSelect={setSelectedMovie} onRecommend={recommend} loadingRecommendations={loadingRecommendations} /></section><Recommendations results={results} loading={loadingRecommendations} error={recommendationError} selectedMovie={selectedMovie} /></main>
}
