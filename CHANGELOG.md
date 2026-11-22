# Changelog

## [Unreleased]

### Added

- Added `GET /api/orgs/{org}/repos` to list a GitHub organisation’s public repositories.
- Added filtering by language, minimum star count and archive status, plus sorting by name, stars or last update.
- Added paginated results with the total number of matching repositories.
- Added optional authentication via `GITHUB_TOKEN` and a 20-minute cache to reduce requests to GitHub.