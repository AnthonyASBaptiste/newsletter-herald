# Newsletter Herald Debug Report — 2026-10-12

## Symptom and scope

The Sanity integration had passing unit tests, but the application had not established a safe, end-to-end editorial handoff. Review state could be reset by retries, invalid dates could enter the review queue, and fields emitted by the API were missing from the Studio schema.

## Root causes

- `sanity_mapper.py` emitted `workflow` and `delivery` references for `newsletterEdition`, while the Studio schema did not declare them.
- `sanity_editorial.py` used `createOrReplace` for editorial, workflow, and delivery records. Retries could replace human edits and decisions.
- Upload and retry paths did not pass the date-validation result into the Sanity writer, which always set `awaiting_review`.
- The local `develop` branch did not contain six remote commits that restricted CORS and protected subscriber batch import and deletion endpoints.

## Fixes applied

- Declared the workflow and delivery references in the newsletter edition schema.
- Changed editorial mutations to `createIfNotExists` so a retry cannot replace an existing record.
- Kept date-invalid editions and workflows in `draft`, recorded the failed date check, and cancelled their delivery record.
- Passed validation state from both upload and retry paths and returned the matching review state.
- Sent a validation alert rather than a review request when retrying a date-invalid edition.
- Applied the current `develop` changes that narrow the Vercel CORS pattern and require API-key authentication for batch subscriber import and subscriber deletion.
- Added regression assertions for schema payload references, non-destructive retries, invalid-date handling, CORS rejection, and endpoint authentication.

## Verification

- Backend: `pytest -q` — 57 passed.
- Sanity Studio: `npm run build` — passed. Sanity warned that the local packages are 6.16.0 while the Studio runtime serves 6.18.0, and that no `appId` is configured.
- Frontend: `npm run build` — passed. Next.js warned that the monorepo has multiple lockfiles.
- Frontend lint: `npm run lint` — passed.
- `git diff --check` — passed.

## Remaining concerns

- The local Git branch reference still reports six commits behind because local `git fetch` is blocked by the host SSH configuration. The changes from those six commits were applied to the working tree through a read-only GitHub view; remote history was not changed.
- The frontend's pinned Next.js version is reported by `npm audit` as affected by a critical advisory. The Next.js project announced an out-of-band update for October 14, 2026; recheck and upgrade to its patched release before deployment.
- The Sanity Studio schema has not been deployed, and no live Content Lake write was attempted. The live verification script targets the production dataset and was not run.
- Backend tests emit deprecation warnings for Pydantic config, Starlette/httpx, and a validation test returning a value.

## Status

**DONE_WITH_CONCERNS** — local code fixes and builds pass. Production schema deployment, live Sanity verification, upstream Next.js security remediation, and local Git remote synchronization remain outstanding.
