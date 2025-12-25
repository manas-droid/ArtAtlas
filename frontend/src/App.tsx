import { type FormEvent, useState } from 'react'
import './App.css'
import { getQueryResponse } from './search/search.service'

function App() {
  const [query, setQuery] = useState('')

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!query.trim()) return
    // Replace this with real search logic when ready
    const result =  await getQueryResponse(query)
    
    console.log(result)
  }

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
          <button type="submit">Search</button>
        </form>
      </header>
    </div>
  )
}

export default App
