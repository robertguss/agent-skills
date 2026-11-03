#!/usr/bin/env bash
# Build a fresh git repo for one plan-audit eval run and print its path.
#
# Usage: setup.sh PLAN [TARGET_DIR]
#   PLAN is a file name from plans/, for example stats-command-plan.md.
#   Only that plan is copied, so audits don't see sibling plans.
#   TARGET_DIR must not exist or must be empty. Without it, a new
#   temporary directory is created.
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fixture="$script_dir/fixture-repo"
plans="$script_dir/plans"

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "usage: $0 PLAN [TARGET_DIR]" >&2
  exit 2
fi

plan="$plans/$1"
if [[ ! -f "$plan" ]]; then
  echo "error: no plan named $1 in $plans" >&2
  exit 1
fi

if [[ $# -eq 2 ]]; then
  target="$2"
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
cp "$plan" "$target/docs/plans/"

git -C "$target" init --quiet
git -C "$target" config user.name "Eval Setup"
git -C "$target" config user.email "eval-setup@example.invalid"
git -C "$target" add --all
git -C "$target" -c commit.gpgsign=false commit --quiet --no-verify -m "Initial import"

echo "$target"
