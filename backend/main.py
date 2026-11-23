from fastapi import FastAPI, HTTPException, Query
from github_client import fetch_repos
import httpx
from typing import Literal
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import os

log_dir = Path(__file__).resolve().parent / "logs"
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    handlers=[
        logging.StreamHandler(),
        RotatingFileHandler(
            log_dir / "backend.log",
            maxBytes=5_000_000,
            backupCount=5,
            encoding="utf-8",
        ),
    ],
)

logger = logging.getLogger(__name__)

token = os.getenv("GITHUB_TOKEN", "").strip()
logger.info("GitHub token configured: %s", "true" if token else "false")

app = FastAPI(
    title="GitHub Repository Explorer",
    description="A simple API to explore GitHub repositories",
    version="0.2.1",
)


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/api/orgs/{org}/repos")
def get_repos(
    org: str,
    archived: bool | None = None,
    min_stars: int = Query(default=0, ge=0),
    language_list: list[str] | None = Query(default=None),
    sort_by: Literal["stars", "updated_at", "name"] = "name",
    order: Literal["asc", "desc"] = "asc",
    page_no: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    """
    Return one page of filtered and sorted repositories for an organisation.
    """
    try:
        repo_list = fetch_repos(
            org=org.lower(),
        )

    except httpx.HTTPStatusError as exc:
        response = exc.response
        status_code = response.status_code
        logger.warning("GitHub returned %s for org=%s", status_code, org)

        if status_code in (429, 403):
            raise HTTPException(
                status_code=status_code,
                detail="GitHub's request limit was reached. Please try again later.",
            ) from exc

        elif status_code == 404:
            raise HTTPException(
                status_code=404,
                detail="No GitHub organisation found with name '%s'." % org,
            ) from exc

        else:
            raise HTTPException(
                status_code=status_code, detail="GitHub could not complete the request."
            ) from exc

    except httpx.RequestError as exc:
        logger.warning("Could not reach GitHub for org=%s: %s", org, type(exc).__name__)
        raise HTTPException(status_code=502, detail="Could not reach GitHub.") from exc

    # Gather list of available languages
    available_languages = sorted(
        {repo["language"] for repo in repo_list if repo["language"]}, key=str.casefold
    )

    # Filter repos
    repo_list = filter_repos(
        repo_list,
        archived=archived,
        min_stars=min_stars,
        language_list=language_list,
    )

    # Sort repos
    repo_list = sort_repos(
        repo_list=repo_list,
        sort_by=sort_by,
        order=order,
    )

    start = (page_no - 1) * page_size

    return {
        "items": repo_list[start : start + page_size],
        "page": page_no,
        "page_size": page_size,
        "total": len(repo_list),
        "available_languages": available_languages,
    }


def filter_repos(
    repo_list: list[dict],
    archived: bool | None,
    min_stars: int,
    language_list: list[str] | None,
):
    """Return repositories that match all active filters."""
    language_list = [lang.strip().lower() for lang in language_list or []]

    return [
        repo
        for repo in repo_list
        if (archived is None or repo.get("archived") == archived)
        and repo.get("stars", 0) >= min_stars
        and (
            not language_list
            or (repo.get("language") or "none").lower() in language_list
        )
    ]


def sort_repos(
    repo_list: list[dict],
    sort_by: str,
    order: str,
):
    """
    Return a sorted copy without changing the cached repository list.
    """
    sort_keys = {
        "stars": lambda repo: repo["stars"],
        "updated_at": lambda repo: repo["updated_at"],
        "name": lambda repo: repo["name"].lower(),
    }
    return sorted(repo_list, key=sort_keys[sort_by], reverse=(order == "desc"))
