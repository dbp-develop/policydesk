#!/bin/sh
# Copy named paths from an artifact onto a bot branch and open a pull request.
# Does not push to main. Usage:
#   open_data_pr.sh <branch> <title> <artifact-dir> <path> [path...]
# BASE_SHA, when set, is the commit the fetch job started from. Files the
# fetch did not change are left as they are on this branch.
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
  _want=$1
  if [ -e "$artifact/$_want" ]; then
    printf '%s\n' "$artifact/$_want"
    return 0
  fi
  _rest=$_want
  while :; do
    case $_rest in
      */*) _rest=${_rest#*/} ;;
      *) break ;;
    esac
    if [ -e "$artifact/$_rest" ]; then
      printf '%s\n' "$artifact/$_rest"
      return 0
    fi
  done
  if [ "$_want" = "data/news" ] && [ -f "$artifact/index.json" ]; then
    printf '%s\n' "$artifact"
    return 0
  fi
  echo "ERROR: missing artifact path $_want" >&2
  return 1
}

# Vacancy files are edited by a person, not by the fetch. Any other file
# that is still byte-for-byte the job-start copy is left alone too, so a
# newer edit on main is not reverted.
leave_unchanged() {
  _path=$1
  _src=$2
  case $_path in
    */vacancies.json | vacancies.json) return 0 ;;
  esac
  if [ -n "${BASE_SHA:-}" ] && git cat-file -e "${BASE_SHA}:${_path}" 2>/dev/null; then
    if git show "${BASE_SHA}:${_path}" | cmp -s - "$_src"; then
      return 0
    fi
  fi
  return 1
}

copy_changed_dir() {
  _src=$1
  _dest=$2
  if [ -z "${BASE_SHA:-}" ]; then
    rm -rf "$_dest"
    mkdir -p "$_dest"
    cp -a "$_src/." "$_dest/"
    return 0
  fi
  mkdir -p "$_dest"
  _list=$(mktemp)
  find "$_src" -type f | sort > "$_list"
  while IFS= read -r _file; do
    [ -n "$_file" ] || continue
    _rest=${_file#"$_src"/}
    _target="$_dest/$_rest"
    if leave_unchanged "$_target" "$_file"; then
      echo "Leaving $_target unchanged"
      continue
    fi
    mkdir -p "$(dirname "$_target")"
    cp "$_file" "$_target"
  done < "$_list"
  git ls-tree -r --name-only "${BASE_SHA}" "$_dest" > "$_list"
  while IFS= read -r _rel; do
    [ -n "$_rel" ] || continue
    _rest=${_rel#"$_dest"/}
    if [ ! -f "$_src/$_rest" ]; then
      rm -f "$_dest/$_rest"
      echo "Removing $_rel (fetch deleted it)"
    fi
  done < "$_list"
  rm -f "$_list"
}

copied_members=""
for path in "$@"; do
  src=$(resolve_src "$path")
  if [ -d "$src" ]; then
    copy_changed_dir "$src" "$path"
    continue
  fi
  if leave_unchanged "$path" "$src"; then
    echo "Leaving $path unchanged"
    continue
  fi
  if [ -f "$src" ]; then
    mkdir -p "$(dirname "$path")"
    cp "$src" "$path"
  else
    echo "ERROR: missing artifact path $path" >&2
    exit 1
  fi
  case $path in
    data/members.json | data/*/members.json) copied_members="$copied_members $path" ;;
  esac
done

# members.json embeds the vacancy list read at job start. Put back the list
# now on this branch so that embed cannot revert a newer vacancy file.
for path in $copied_members; do
  case $path in
    data/members.json) vac=data/vacancies.json ;;
    data/*/members.json) vac=${path%/members.json}/vacancies.json ;;
    *) continue ;;
  esac
  if [ -f "$vac" ]; then
    python3 - "$path" "$vac" << 'PY'
import json
import sys

members_path, vac_path = sys.argv[1], sys.argv[2]
members = json.loads(open(members_path, encoding="utf-8").read())
vacancies = json.loads(open(vac_path, encoding="utf-8").read())
if (
    isinstance(members, dict)
    and isinstance(vacancies, list)
    and members.get("vacancies") != vacancies
):
    members["vacancies"] = vacancies
    with open(members_path, "w", encoding="utf-8") as handle:
        json.dump(members, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
PY
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
