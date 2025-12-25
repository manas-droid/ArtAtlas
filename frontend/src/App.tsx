import { type FormEvent,  useState } from 'react'
import './App.css'
import { getQueryResponse } from './search/search.service'
import type { Artwork, ExplanationBlock, SearchModel } from './search/search.model'

function conceptReason(label: string) {
  return `Your query relates to ${label}${label ? '' : ' this idea'}.`
}

function App() {
  const [query, setQuery] = useState('')
  const [searchModel, setSearchModel] = useState<SearchModel | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [hasSearched, setHasSearched] = useState(false)


  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const trimmedQuery = query.trim()
    if (!trimmedQuery) {
      setError('Enter a search term to begin.')
      return
    }

    setError(null)
    setLoading(true)
    setHasSearched(true)

    try {
      const response = await getQueryResponse(trimmedQuery)
      setSearchModel(response)
    } catch (err) {
      console.error('Search failed', err)
      setError('Unable to fetch results right now. Please try again.')
      setSearchModel(null)
    } finally {
      setLoading(false)
    }
  }

  const explanationBlocks = searchModel?.explanationBlocks ?? []

  return (
    <div className="app">
      <header className="search-header">
        <form className="search-form" onSubmit={handleSubmit}>
          <label className="sr-only" htmlFor="search">
            Search
          </label>
          <input
            id="search"
            type="text"
            placeholder="Search..."
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Searching...' : 'Search'}
          </button>
        </form>
        {error && <p className="error">{error}</p>}
      </header>

      {hasSearched && (
        <section className="query-intro">
          <p className="subtle">
            We identified key artistic ideas related to your query and found visual evidence supporting them.
          </p>
        </section>
      )}

      <main>
        {explanationBlocks.length > 0 && (
          <section className="concepts">
            <h2>Key ideas related to your search</h2>
            <div className="concept-grid">
              {explanationBlocks.map((block) => (
                <ConceptCard key={block.concept.id} block={block} />
              ))}
            </div>
          </section>
        )}

        {!loading && hasSearched && explanationBlocks.length === 0 && !error && (
          <div className="empty-state">
            <p>No explainable ideas found yet. Try refining your search.</p>
          </div>
        )}

        {searchModel?.metadata?.unexplainedResultsHidden && (
          <footer className="footer-note">
            Some retrieved artworks are not shown because they could not be confidently explained using visual evidence.
          </footer>
        )}
      </main>
    </div>
  )
}

type ConceptCardProps = {
  block: ExplanationBlock
}

function ConceptCard({ block }: ConceptCardProps) {
  const { concept, evidence } = block
  return (
    <article className="concept-card">
      <div className="card-section">
        <p className="eyebrow">Why this idea appears</p>
        <p className="lead">{conceptReason(concept.label)}</p>
        {concept.confidenceLabel && <span className="pill">{concept.confidenceLabel} confidence</span>}
      </div>

      <div className="card-section">
        <p className="eyebrow">Visual examples supporting this idea</p>
        <p className="body">Overall strength: {evidence.overallStrengthLabel}</p>
        <div className="artworks">
          {evidence.artworks.map((artwork) => (
            <ArtworkCard key={artwork.artworkId} artwork={artwork} conceptLabel={concept.label} />
          ))}
        </div>
      </div>
    </article>
  )
}

type ArtworkCardProps = {
  artwork: Artwork
  conceptLabel: string
}

function ArtworkCard({ artwork, conceptLabel }: ArtworkCardProps) {
  const hasImage = Boolean(artwork.imageUrl)
  return (
    <div className="artwork-card">
      <div className="artwork-thumb" aria-hidden="true">
        {hasImage ? (
          <img src={artwork.imageUrl} alt={artwork.title || conceptLabel} loading="lazy" />
        ) : (
          <span>{artwork.title || conceptLabel}</span>
        )}
      </div>
      <div className="artwork-copy">
        <p className="eyebrow">{artwork.supportStrengthLabel} support</p>
        <p className="lead">{artwork.title || 'Untitled artwork'}</p>
        <p className="body">{artwork.whyThisArtwork}</p>
      </div>
    </div>
  )
}

export default App
