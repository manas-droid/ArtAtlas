import { type FormEvent, useState } from 'react'
import './App.css'
import { getQueryResponse } from './search.service'
import { FullResultsPanel } from './components/FullResultsPanel'
import { ExplanationPanel } from './components/ExplanationPanel'
import type { UIModel } from './transform.api.response'

function App() {
  const [query, setQuery] = useState('')
  const [uiModel, setUIModel] = useState<UIModel | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [hasSearched, setHasSearched] = useState(false)
  const [activeTab, setActiveTab] = useState<'full' | 'explanation'>('full')


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
      setUIModel(response)
    } catch (err) {
      console.error('Search failed', err)
      setError('Unable to fetch results right now. Please try again.')
      setUIModel(null)
    } finally {
      setLoading(false)
    }
  }

  const explanationBlocks = uiModel?.explanationModel?.explanationBlocks ?? []
  const explanationMeta = uiModel?.explanationModel?.metadata
  const fullResults = uiModel?.fullResultModel ?? { artwork: [], essay: [] }

  const hasExplanation = explanationBlocks.length > 0
  const hasFullResults = (fullResults.artwork?.length ?? 0) > 0 || (fullResults.essay?.length ?? 0) > 0
  const showTabs = hasExplanation && hasFullResults
  const currentTab = showTabs ? activeTab : hasFullResults ? 'full' : 'explanation'

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
        {showTabs && (
          <div className="tabs">
            <button
              className={currentTab === 'full' ? 'tab active' : 'tab'}
              type="button"
              onClick={() => setActiveTab('full')}
            >
              Full results
            </button>
            <button
              className={currentTab === 'explanation' ? 'tab active' : 'tab'}
              type="button"
              onClick={() => setActiveTab('explanation')}
            >
              Explanations
            </button>
          </div>
        )}

        {currentTab === 'full' && hasFullResults && <FullResultsPanel model={fullResults} />}

        {currentTab === 'explanation' && (
          <ExplanationPanel
            blocks={explanationBlocks}
            metadata={explanationMeta}
            showEmptyMessage={!loading && hasSearched}
          />
        )}

        {!showTabs && !hasFullResults && !hasExplanation && !loading && hasSearched && !error && (
          <div className="empty-state">
            <p>No results available yet. Try refining your search.</p>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
