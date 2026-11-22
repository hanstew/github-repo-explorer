import httpx
from cachetools.func import ttl_cache
import os


@ttl_cache(maxsize=16, ttl=1200)
def fetch_repos(
    org: str,
) -> list[dict]:
    """
    Fetch all public repositories for an organisation.

    Follow GitHub pagination and cache successful results for 20 minutes
    so changing filters or pages can reuse the same data.

    Each repository is returned as a dictionary.
    """
    next_url = f"https://api.github.com/orgs/{org}/repos?type=public&per_page=100"
    all_repos = []
    headers = {"Accept": "application/vnd.github+json"}
    token = os.getenv("GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    while next_url:
        response = httpx.get(next_url, headers=headers, timeout=10)
        response.raise_for_status()
        repo_list = [
            {
                "name": repo.get("name"),
                "description": repo.get("description"),
                "language": repo.get("language"),
                "stars": repo.get("stargazers_count"),
                "updated_at": repo.get("updated_at"),
                "archived": repo.get("archived"),
            }
            for repo in response.json()
        ]
        all_repos.extend(repo_list)

        # Handle pagination - check if there is a next url to query next
        next_url = response.links.get("next", {}).get("url")
        print(next_url)

    return all_repos
