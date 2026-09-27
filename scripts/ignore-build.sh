#!/bin/bash
# Vercel Ignored Build Step Script
#
# Rules:
# - Exit code 0: Skip / Cancel build (does not consume build minutes)
# - Exit code 1: Proceed with build
#
# Goals:
# 1. Only build production on 'main' branch.
# 2. Skip preview builds on 'develop' and feature branches to save build minutes.
# 3. On 'main', skip builds if only backend/docs/tooling changed (no frontend changes).

echo "--- Vercel Ignore Build Check ---"
echo "Target Branch (VERCEL_GIT_COMMIT_REF): '${VERCEL_GIT_COMMIT_REF}'"
echo "Previous SHA (VERCEL_GIT_PREVIOUS_SHA): '${VERCEL_GIT_PREVIOUS_SHA}'"
echo "Current SHA (VERCEL_GIT_COMMIT_SHA):   '${VERCEL_GIT_COMMIT_SHA}'"

# 0. Autonomous Agent / Manual Skip Filter: Check for [skip vercel] or [skip ci]
COMMIT_MSG="${VERCEL_GIT_COMMIT_MESSAGE}"
if [ -z "$COMMIT_MSG" ]; then
  COMMIT_MSG=$(git log -1 --pretty=%B 2>/dev/null || echo "")
fi

# Convert message to lowercase for case-insensitive matching
COMMIT_MSG_LOWER=$(echo "$COMMIT_MSG" | tr '[:upper:]' '[:lower:]')

if echo "$COMMIT_MSG_LOWER" | grep -Eq "\[skip vercel\]|\[vercel skip\]|\[skip ci\]|\[ci skip\]|\*\*\*no_ci\*\*\*"; then
  echo "🛑 [SKIP BUILD] Commit message contains skip flag ([skip vercel] / [skip ci]). Skipping build to conserve build minutes."
  exit 0
fi

# 1. Branch filter: Only 'main' should ever build on Vercel
if [ -n "$VERCEL_GIT_COMMIT_REF" ] && [ "$VERCEL_GIT_COMMIT_REF" != "main" ]; then
  echo "🛑 [SKIP BUILD] Branch '${VERCEL_GIT_COMMIT_REF}' is not 'main'. Skipping preview deployment to conserve build minutes."
  exit 0
fi

# 2. Path filter: On 'main', only build if frontend files were modified
BASE_SHA="${VERCEL_GIT_PREVIOUS_SHA}"

# If VERCEL_GIT_PREVIOUS_SHA is not provided or empty (e.g. first deployment or manual trigger)
if [ -z "$BASE_SHA" ]; then
  if git rev-parse HEAD^ >/dev/null 2>&1; then
    BASE_SHA="HEAD^"
  else
    echo "✅ [BUILD] Initial commit or no previous commit reference found on main. Proceeding with build."
    exit 1
  fi
fi

# Determine whether the script is executed from the repository root or frontend/ directory
if [ -d "frontend" ]; then
  TARGET_PATH="frontend/"
else
  TARGET_PATH="."
fi

echo "Checking git diff between $BASE_SHA and HEAD for path: ${TARGET_PATH}"

# Check if any changes occurred in the frontend path
if git diff --quiet "$BASE_SHA" HEAD -- "$TARGET_PATH"; then
  echo "🛑 [SKIP BUILD] No changes detected in '${TARGET_PATH}'. Backend, documentation, or tooling only. Skipping build to conserve build minutes."
  exit 0
else
  echo "✅ [BUILD] Changes detected in '${TARGET_PATH}'. Proceeding with production build."
  exit 1
fi
