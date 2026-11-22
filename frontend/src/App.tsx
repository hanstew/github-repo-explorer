import { useState, type FormEvent } from "react"

type Repo = {
  name: string
  description: string | null
  language: string | null
  stars: number
  updated_at: string
  archived: boolean
}

type RepoPage = {
  items: Repo[]
  page: number
  page_size: number
  total: number
  available_languages: string[]
}

type Search = {
  org: string
  params: URLSearchParams
}

export default function App() {
  const [org, setOrg] = useState("")
  const [result, setResult] = useState<RepoPage | null>(null)
  const [lastSearch, setLastSearch] = useState<Search | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  async function loadPage(search: Search, page: number) {
    setLoading(true)
    setError("")

    try {
      const params = new URLSearchParams(search.params)
      params.set("page_no", String(page))

      const url = `/api/orgs/${encodeURIComponent(search.org)}/repos?${params}`
      const response = await fetch(url)
      if (!response.ok) {
        const body = await response.json().catch(() => null)
        throw new Error(
          typeof body?.detail === "string"
            ? body.detail
            : `Could not load repositories (${response.status})`
        )
      }
      
      const data: RepoPage = await response.json()
      setResult(data)
      setLastSearch(search)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load repositories")
    } finally {
      setLoading(false)
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const orgName = org.trim().toLowerCase()
    if (!orgName) return

    const form = new FormData(event.currentTarget)
    const params = new URLSearchParams()

    for (const [key, value] of form.entries()) {
      if (typeof value === "string" && value !== "") {
        params.append(key, value)
      }
    }

    // A new search always starts at page 1.
    void loadPage({ org: orgName, params }, 1)
  }

  const sameOrg = org.trim().toLowerCase() === lastSearch?.org
  const totalPages = result ? Math.ceil(result.total / result.page_size) : 0

  return (
    <main>
      <h1>GitHub Repository Explorer</h1>

      <form onSubmit={handleSubmit}>
        <fieldset className="search-options" disabled={loading}>
          <legend>Search Options</legend>

          <label className="org-field">
            Organisation{" "}
            <input
              value={org}
              onChange={(event) => setOrg(event.target.value)}
              placeholder="e.g. google"
              required
            />
          </label>

          {sameOrg && result && (
            <>
            <label>
              Minimum stars{" "}
              <input type="number" name="min_stars" min="0" defaultValue="0" />
            </label>

            <label>
              Archive status{" "}
              <select name="archived" defaultValue="">
                <option value="">All repositories</option>
                <option value="false">Not archived</option>
                <option value="true">Archived only</option>
              </select>
            </label>

            <label>
              Sort by{" "}
              <select name="sort_by" defaultValue="name">
                <option value="stars">Stars</option>
                <option value="updated_at">Last updated</option>
                <option value="name">Name</option>
              </select>
            </label>

            <label>
              Order{" "}
              <select name="order" defaultValue="asc">
                <option value="desc">Descending</option>
                <option value="asc">Ascending</option>
              </select>
            </label>

            <fieldset>
              <legend>Languages (leave unchecked for all)</legend>
              {result.available_languages.map((lang) => (
                <label key={lang}>
                  <input type="checkbox" name="language_list" value={lang} /> {lang}{" "}
                </label>
              ))}
              <label>
                <input type="checkbox" name="language_list" value="none" /> No language
              </label>
            </fieldset>
          </>
          )}

          <button type="submit" disabled={!org.trim()}>Search</button>
        </fieldset>
      </form>

      {loading && <p role="status">Loading repositories…</p>}
      {error && <p role="alert">{error}</p>}

      {!loading && !error && result && lastSearch && (
        <section>
          <h2>Results for {lastSearch.org}</h2>

          {result.items.length === 0 ? (
            <p>No repositories match these filters.</p>
          ) : (
            <>
              <p>{result.total} matching repositories</p>
              <div className="table-scroll">
                <table>
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Description</th>
                      <th>Language</th>
                      <th>Stars</th>
                      <th>Last updated</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.items.map((repo) => (
                      <tr key={repo.name}>
                        <td>{repo.name}</td>
                        <td>{repo.description || "—"}</td>
                        <td>{repo.language || "No language"}</td>
                        <td>{repo.stars}</td>
                        <td>{new Date(repo.updated_at).toLocaleDateString("en-GB")}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <nav aria-label="Results pages">
                <button
                  disabled={result.page <= 1}
                  onClick={() => void loadPage(lastSearch, result.page - 1)}
                >
                  Previous
                </button>
                {" "}Page {result.page} of {totalPages}{" "}
                <button
                  disabled={result.page >= totalPages}
                  onClick={() => void loadPage(lastSearch, result.page + 1)}
                >
                  Next
                </button>
              </nav>
            </>
          )}
        </section>
      )}
    </main>
  )
}