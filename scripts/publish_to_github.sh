#!/usr/bin/env bash
set -euo pipefail
# This script pushes after the empty PUBLIC GitHub repo has been created.
# It does not create the repo or log in to GitHub.
cd "$(dirname "${BASH_SOURCE[0]}")/.."
REPO='https://github.com/venkatreddymallidi/devtrack.git'
if ! git rev-parse --verify HEAD >/dev/null 2>&1; then
  echo 'No local Git commit found; run git init, git add ., and git commit first.' >&2
  exit 1
fi
if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "$REPO"
else
  git remote add origin "$REPO"
fi
git branch -M main
git push -u origin main
printf '\nPublished: https://github.com/venkatreddymallidi/devtrack\n'
