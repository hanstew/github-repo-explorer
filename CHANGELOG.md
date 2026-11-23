# Changelog

## [1.0.0] - 2026-11-23

First stable release of GitHub Repository Explorer.

### Added
- Backend logs now saved to `backend/logs/backend.log` and rotated automatically.

### Changed
- Updated browser tab title to “GitHub Repository Explorer”.
- Expanded README with setup instructions, testing guidance, design decisions, trade-offs and planned improvements.

## [0.2.1] - 2026-11-22
- Fixed an error that caused repository searches to return `500 Internal Server Error` when GitHub was unreachable. The API now returns `502 Bad Gateway` with the message “Could not reach GitHub.”

## [0.2.0] - 2026-11-22

### Added
- Added a web interface for browsing a GitHub organisation’s repositories.
  Users can filter by language, archive status, and minimum stars, sort by
  name, stars, or last update, and page through the results.

### Fixed
- Fixed a `KeyError` when sorting repositories by stars.


## [0.1.0]

### Added

- Added `GET /api/orgs/{org}/repos` to list a GitHub organisation’s public repositories.
- Added filtering by language, minimum star count and archive status, plus sorting by name, stars or last update.
- Added paginated results with the total number of matching repositories.
- Added optional authentication via `GITHUB_TOKEN` and a 20-minute cache to reduce requests to GitHub.