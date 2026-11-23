# GitHub Repository Explorer

A React and FastAPI app for exploring a GitHub organisation’s public 
repositories.

Search by organisation to return a table of all repositories for an 
organisation. Filter repositories by language, archive status or minimum stars. 
Sort the results by name, star count or last update.

## Run locally

### Prerequisites

- Python 3.12+
- Node.js and npm

The commands below use Bash and were tested on Ubuntu under WSL.

Open two terminals at the repository root, one for the backend and one for the 
frontend.


### Optional GitHub token

The app works with and without a token. Set environment variable `GITHUB_TOKEN`
to make authenticated requests to GitHub and use a higher API rate limit. Token 
should be a fine-grained personal access token with read-only access to public 
repositories.

In the WSL/Bash terminal where you’ll start the backend, run:

```bash
read -rsp "GitHub token: " GITHUB_TOKEN
```
Enter your Github token, then run:
```
echo
export GITHUB_TOKEN
```

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Open http://127.0.0.1:8000/health to check the backend is running.
Interactive API documentation is available at http://127.0.0.1:8000/docs.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite.

Enter a GitHub organisation such as `github` and click **Search**. Once the 
results load, choose your filters and click **Search** again to apply them.

## How it works

1. React sends a request to `GET /api/orgs/{org}/repos`. Vite forwards `/api` 
    requests to FastAPI.
2. The backend retrieves the organisation’s public repositories from GitHub,
   following GitHub’s pagination to collect the full list.
3. FastAPI builds the list of available languages, then applies any requested
   filters, sorts the matching repositories and returns one page of results.
4. React displays the repositories and uses the total number of matches to
   calculate how many pages are available.
5. The backend caches up to 16 organisations' repository lists in memory for up 
   to 20 minutes. Changing filters, sorting, or changing page reuses that list 
   while it is cached. This reduces GitHub API requests, but recent changes on 
   GitHub can take up to 20 minutes to appear.

E.g. The request below returns the first page of repositories with at least 10 
stars, where primary language is Python ordered from most to fewest stars:

```text
/api/orgs/github/repos?language_list=Python&min_stars=10&sort_by=stars&order=desc&page_no=1
```

## Decisions and trade-offs

#### Filter and sort before paginating.
This makes the ordering and total count accurate across the whole organisation. 
The trade-off is that the first search for a large organisation can require 
several GitHub requests so may take longer initially.

#### Build language options from the full repository list.
Selecting a language keeps the other languages available, so users can broaden 
their search without clearing the filter first.

#### Apply filters on Search.
Users can change several options in one go. Changing a checkbox takes effect 
when they submit the form.

## Run the backend tests

With the backend virtual environment active, from `backend/`, run:

```bash
python -m pytest -q
```

Tests cover sorting, language filtering, pagination, and GitHub connection 
failures. Endpoint tests replace the GitHub client function with sample data or 
simulated error, to run offline.

## Future improvements

- Expand test coverage. E.g. Add backend tests for GitHub pagination and 
  rate-limit responses and a frontend test that checks whether selected
  languages are sent to the API correctly.
- UI improvements. E.g. Replace the language checkbox list with a searchable 
  multi-select dropdown so users can find and select languages without 
  scrolling through a long list.
- Show when repository data was last fetched and let users refresh it before
  20-minute cache expires.
- Link repository names to GitHub so users can open a project directly from
  the results table.