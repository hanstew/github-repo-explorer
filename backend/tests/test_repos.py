from fastapi.testclient import TestClient
import main
from main import filter_repos, sort_repos
import httpx

client = TestClient(main.app)


def test_sort_by_stars_returns_highest_first():
    repos = [
        {"name": "small", "stars": 2},
        {"name": "large", "stars": 50},
    ]
    result = sort_repos(repos, sort_by="stars", order="desc")
    assert [repo["name"] for repo in result] == ["large", "small"]


def test_language_filter_matches_regardless_of_case():
    repos = [
        {"name": "api", "language": "Python"},
        {"name": "website", "language": "TypeScript"},
        {"name": "notes", "language": None},
    ]
    result = filter_repos(
        repos,
        archived=None,
        min_stars=0,
        language_list=["python"],
    )
    assert [repo["name"] for repo in result] == ["api"]

def test_get_repos_filters_before_paginating(monkeypatch):
    repos = [
        {"name": "a", "language": "Rust"},
        {"name": "b", "language": "Python"},
        {"name": "c", "language": "TypeScript"},
    ]
    monkeypatch.setattr(main, "fetch_repos", lambda org: repos)

    response = client.get(
        "/api/orgs/example/repos",
        params=[
            ("language_list", "Python"),
            ("language_list", "TypeScript"),
            ("page_no", "2"),
            ("page_size", "1"),
        ],
    )

    assert response.status_code == 200
    data = response.json()
    assert [repo["name"] for repo in data["items"]] == ["c"]
    assert data["page"] == 2
    assert data["total"] == 2
    assert data["available_languages"] == ["Python", "Rust", "TypeScript"]

def test_get_repos_returns_502_when_github_is_unreachable(monkeypatch):
    def unreachable(org):
        raise httpx.ConnectError("Connection refused")

    monkeypatch.setattr(main, "fetch_repos", unreachable)
    response = client.get("/api/orgs/example/repos")
    assert response.status_code == 502
    assert response.json()["detail"] == "Could not reach GitHub."