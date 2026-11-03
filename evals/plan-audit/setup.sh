#!/usr/bin/env bash
# Build a fresh git repo for one plan-audit eval run and print its path.
#
# Usage: setup.sh [TARGET_DIR]
#   TARGET_DIR must not exist or must be empty. Without it, a new
#   temporary directory is created.
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fixture="$script_dir/fixture-repo"
plans="$script_dir/plans"

if [[ $# -gt 1 ]]; then
  echo "usage: $0 [TARGET_DIR]" >&2
  exit 2
fi

if [[ $# -eq 1 ]]; then
  target="$1"
  if [[ -e "$target" && -n "$(ls -A "$target")" ]]; then
    echo "error: $target exists and is not empty" >&2
    exit 1
  fi
  mkdir -p "$target"
  target="$(cd "$target" && pwd)"
else
  target="$(mktemp -d "${TMPDIR:-/tmp}/plan-audit-eval.XXXXXX")"
fi

cp -R "$fixture/." "$target/"
find "$target" -name __pycache__ -type d -prune -exec rm -rf {} +
mkdir -p "$target/docs/plans"
cp "$plans"/*.md "$target/docs/plans/"

git -C "$target" init --quiet
git -C "$target" config user.name "Eval Setup"
git -C "$target" config user.email "eval-setup@example.invalid"
git -C "$target" add --all
git -C "$target" -c commit.gpgsign=false commit --quiet --no-verify -m "Initial import"

echo "$target"
