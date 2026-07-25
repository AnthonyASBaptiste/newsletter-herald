# SALLTO Herald — Changelog

All notable changes to the SALLTO Herald platform are documented in this file.

---

## [0.2.0] — 2026-07-25
### Added
- **Clerk Authentication Migration**: Swapped the entire authentication engine from Stack Auth to Clerk to align with core SaaS stack frameworks.
- **Premium Rounded Favicons**: Generated circular squircle web, Apple Touch, PWA manifest, and tab favicon files from custom user graphics.
- **Ignored Build Steps**: Added Vercel build-minute optimization scripts targeting only production branches.
- **Dynamic Documents Center**: Integrated frontend docs directory to render user manuals and version changelogs natively.

### Changed
- **Unified State Console**: Extracted component rendering state into modular components for strict Next.js static rendering compliance.
- **Root Git Ignore**: Optimized workspace tracking to isolate root-level dependency node folders and developer credential profiles.

---

## [0.1.1] — 2026-07-20
### Added
- **Concurrently Root Runner**: Configured cross-directory runner scripts to boot frontend and backend environments simultaneously with a single command.
- **Google CSV Subscriber Import**: Implemented parsing utilities that automatically extract contacts from Google Contacts export structures and sync them to PostgreSQL.

### Fixed
- **Name Parsing Logic**: Corrected layout mapping issues during contact ingestion when importing users with missing phone details or compound last names.

---

## [0.1.0] — 2026-06-12
### Added
- **FastAPI Core Processor**: Configured document extraction routes using PyMuPDF and Llama 3.1 70B summaries.
- **Liturgical Auditing Log**: Implemented state-machine validators for liturgical season calendar tracking and database ingestion error reporting.
- **Human-in-the-Loop Dialog**: Developed override controls allowing admins to edit failed metadata, bypass delivery queues, and execute direct archiving.
