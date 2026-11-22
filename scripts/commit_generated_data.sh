#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -lt 2 ]]; then
  echo "Usage: $0 <commit-message> <path> [<path> ...]" >&2
  exit 2
fi

message="$1"
shift

git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git add -- "$@"

if git diff --cached --quiet; then
  echo "Generated outputs are unchanged."
  exit 0
fi

git commit -m "$message"

# Generated-data workflows may overlap. Rebase ordinary, non-conflicting
# changes; never resolve scientific-data conflicts by blindly choosing ours/theirs.
for attempt in 1 2 3 4 5; do
  git fetch origin main
  if git rebase origin/main; then
    if git push origin HEAD:main; then
      echo "Published generated outputs."
      exit 0
    fi
  else
    echo "::error::Generated-data commit conflicts with newer main. Refusing an automatic conflict resolution."
    git rebase --abort || true
    exit 1
  fi
  delay=$((attempt * 3))
  echo "Publish attempt $attempt/5 did not complete; retrying in ${delay}s."
  sleep "$delay"
done

echo "::error::Could not publish generated outputs after five attempts."
exit 1
