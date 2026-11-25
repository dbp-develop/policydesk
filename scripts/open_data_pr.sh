#!/bin/sh
# Copy named paths from an artifact onto a bot branch and open a pull request.
# Does not push to main. Usage:
#   open_data_pr.sh <branch> <title> <artifact-dir> <path> [path...]
set -eu

branch=$1
title=$2
artifact=$3
shift 3

git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git fetch origin main

if git ls-remote --exit-code --heads origin "$branch" >/dev/null 2>&1; then
  git checkout -B "$branch" "origin/$branch"
  git merge origin/main --no-edit
else
  git checkout -B "$branch" origin/main
fi

# upload-artifact stores files relative to their least common directory, so
# data/qld/members.json may arrive as qld/members.json. A directory upload of
# data/news arrives as the files themselves (index.json at the artifact root).
resolve_src() {
  path=$1
  if [ -e "$artifact/$path" ]; then
    printf '%s\n' "$artifact/$path"
    return 0
  fi
  rest=$path
  while :; do
    case $rest in
      */*) rest=${rest#*/} ;;
      *) break ;;
    esac
    if [ -e "$artifact/$rest" ]; then
      printf '%s\n' "$artifact/$rest"
      return 0
    fi
  done
  if [ "$path" = "data/news" ] && [ -f "$artifact/index.json" ]; then
    printf '%s\n' "$artifact"
    return 0
  fi
  echo "ERROR: missing artifact path $path" >&2
  return 1
}

for path in "$@"; do
  src=$(resolve_src "$path")
  if [ -d "$src" ]; then
    rm -rf "$path"
    mkdir -p "$path"
    cp -a "$src/." "$path/"
  elif [ -f "$src" ]; then
    mkdir -p "$(dirname "$path")"
    cp "$src" "$path"
  else
    echo "ERROR: missing artifact path $path" >&2
    exit 1
  fi
done

git add -- "$@"
if [ "$1" = "data/news" ]; then
  if git diff --staged --quiet -- data/news ':!data/news/index.json'; then
    echo "No news item changes"
    exit 0
  fi
elif git diff --staged --quiet; then
  echo "No changes"
  exit 0
fi

git commit -m "$title"
git push origin "HEAD:$branch"

existing=$(gh pr list --base main --head "$branch" --state open --json number --jq '.[0].number')
if [ -n "$existing" ] && [ "$existing" != "null" ]; then
  echo "Updated open pull request #$existing"
  exit 0
fi

gh pr create --base main --head "$branch" --title "$title" \
  --body "Automated data update. Review the diff before merging. This workflow does not push to main."
