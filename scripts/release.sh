#!/bin/bash
set -e

# Release Tagging Script for Newsletter Herald
#
# Usage:
#   ./scripts/release.sh [patch|minor|major|<version>]
#
# Process:
#   1. Verify current branch is 'main' and working tree is clean.
#   2. Determine next semantic version.
#   3. Update package.json, frontend/package.json, backend/pyproject.toml.
#   4. Update CHANGELOG.md with conventional commits since last tag.
#   5. Commit: chore(release): X.Y.Z
#   6. Tag: vX.Y.Z
#   7. Guide user to push main and tags.

BUMP_TYPE="${1:-patch}"

# 1. Safety Checks
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
  echo "❌ Error: Releases must be cut on the 'main' branch."
  echo "Current branch is '${CURRENT_BRANCH}'."
  echo "Please merge 'develop' into 'main' first, then run release from 'main'."
  exit 1
fi

if [ -n "$(git status --porcelain)" ]; then
  echo "❌ Error: Working tree is dirty. Please commit or stash changes before releasing."
  git status --short
  exit 1
fi

# 2. Determine Current Version
CURRENT_VERSION=$(node -e "console.log(require('./package.json').version)")
echo "Current version: $CURRENT_VERSION"

# Parse semver numbers
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"

case "$BUMP_TYPE" in
  patch)
    NEW_PATCH=$((PATCH + 1))
    NEW_VERSION="${MAJOR}.${MINOR}.${NEW_PATCH}"
    ;;
  minor)
    NEW_MINOR=$((MINOR + 1))
    NEW_VERSION="${MAJOR}.${NEW_MINOR}.0"
    ;;
  major)
    NEW_MAJOR=$((MAJOR + 1))
    NEW_VERSION="${NEW_MAJOR}.0.0"
    ;;
  *)
    # Treat argument as exact version string
    NEW_VERSION="$BUMP_TYPE"
    ;;
esac

TAG_NAME="v${NEW_VERSION}"
echo "Cutting release: ${CURRENT_VERSION} -> ${NEW_VERSION} (${TAG_NAME})"

# Check if tag already exists
if git rev-parse "$TAG_NAME" >/dev/null 2>&1; then
  echo "❌ Error: Git tag '${TAG_NAME}' already exists."
  exit 1
fi

# 3. Update Versions in Project Files
echo "Updating version numbers in project files..."

# Root package.json
node -e "
  const fs = require('fs');
  const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));
  pkg.version = '${NEW_VERSION}';
  fs.writeFileSync('package.json', JSON.stringify(pkg, null, 2) + '\n');
"

# Root package-lock.json if it exists
if [ -f "package-lock.json" ]; then
  node -e "
    const fs = require('fs');
    const lock = JSON.parse(fs.readFileSync('package-lock.json', 'utf8'));
    lock.version = '${NEW_VERSION}';
    if (lock.packages && lock.packages['']) {
      lock.packages[''].version = '${NEW_VERSION}';
    }
    fs.writeFileSync('package-lock.json', JSON.stringify(lock, null, 2) + '\n');
  "
fi

# Frontend package.json
if [ -f "frontend/package.json" ]; then
  node -e "
    const fs = require('fs');
    const pkg = JSON.parse(fs.readFileSync('frontend/package.json', 'utf8'));
    pkg.version = '${NEW_VERSION}';
    fs.writeFileSync('frontend/package.json', JSON.stringify(pkg, null, 2) + '\n');
  "
fi

# Frontend package-lock.json if it exists
if [ -f "frontend/package-lock.json" ]; then
  node -e "
    const fs = require('fs');
    const lock = JSON.parse(fs.readFileSync('frontend/package-lock.json', 'utf8'));
    lock.version = '${NEW_VERSION}';
    if (lock.packages && lock.packages['']) {
      lock.packages[''].version = '${NEW_VERSION}';
    }
    fs.writeFileSync('frontend/package-lock.json', JSON.stringify(lock, null, 2) + '\n');
  "
fi

# Backend pyproject.toml
if [ -f "backend/pyproject.toml" ]; then
  python3 -c "
import re
with open('backend/pyproject.toml', 'r') as f:
    content = f.read()
updated = re.sub(r'version = \"[0-9\.]+\"', 'version = \"${NEW_VERSION}\"', content, count=1)
with open('backend/pyproject.toml', 'w') as f:
    f.write(updated)
"
fi

# 4. Generate CHANGELOG.md entry
PREV_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
RELEASE_DATE=$(date +%Y-%m-%d)

echo "Generating changelog entry since ${PREV_TAG:-initial commit}..."

CHANGES_FEAT=""
CHANGES_FIX=""
CHANGES_OTHER=""

if [ -n "$PREV_TAG" ]; then
  LOG_RANGE="${PREV_TAG}..HEAD"
else
  LOG_RANGE="HEAD"
fi

# Group commits
while IFS= read -r line; do
  [ -z "$line" ] && continue
  if echo "$line" | grep -Eq '^[a-f0-9]+ feat(\(.*\))?:'; then
    CHANGES_FEAT="${CHANGES_FEAT}* ${line}\n"
  elif echo "$line" | grep -Eq '^[a-f0-9]+ fix(\(.*\))?:'; then
    CHANGES_FIX="${CHANGES_FIX}* ${line}\n"
  elif ! echo "$line" | grep -Eq '^[a-f0-9]+ chore\(release\):'; then
    CHANGES_OTHER="${CHANGES_OTHER}* ${line}\n"
  fi
done < <(git log "$LOG_RANGE" --oneline --no-merges)

TEMP_CHANGELOG=$(mktemp)
cat <<EOF > "$TEMP_CHANGELOG"
# Changelog

### [${NEW_VERSION}] (${RELEASE_DATE})

EOF

if [ -n "$CHANGES_FEAT" ]; then
  cat <<EOF >> "$TEMP_CHANGELOG"
### Features

$(echo -e "$CHANGES_FEAT")
EOF
fi

if [ -n "$CHANGES_FIX" ]; then
  cat <<EOF >> "$TEMP_CHANGELOG"
### Bug Fixes

$(echo -e "$CHANGES_FIX")
EOF
fi

if [ -n "$CHANGES_OTHER" ]; then
  cat <<EOF >> "$TEMP_CHANGELOG"
### Improvements & Chores

$(echo -e "$CHANGES_OTHER")
EOF
fi

# Append previous changelog content (skipping header line)
if [ -f "CHANGELOG.md" ]; then
  tail -n +2 "CHANGELOG.md" >> "$TEMP_CHANGELOG"
fi
mv "$TEMP_CHANGELOG" CHANGELOG.md

# 5. Git Commit and Tag
echo "Committing release ${NEW_VERSION}..."
git add package.json package-lock.json CHANGELOG.md
[ -f "frontend/package.json" ] && git add frontend/package.json
[ -f "frontend/package-lock.json" ] && git add frontend/package-lock.json
[ -f "backend/pyproject.toml" ] && git add backend/pyproject.toml

git commit -m "chore(release): ${NEW_VERSION}"
git tag -a "${TAG_NAME}" -m "chore(release): ${NEW_VERSION}"

echo "=========================================================="
echo "🎉 Release ${TAG_NAME} successfully created!"
echo "=========================================================="
echo "Next Steps:"
echo "  1. Push release commit and tag to GitHub:"
echo "       git push origin main --tags"
echo "  2. Sync develop branch with the new release:"
echo "       git checkout develop && git merge main && git push origin develop"
echo "=========================================================="
