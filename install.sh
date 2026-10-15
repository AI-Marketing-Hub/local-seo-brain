#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: install.sh --client SLUG --owner NAME --target-parent ABSOLUTE_PATH --as-of YYYY-MM-DD [--dry-run]"
}

if [[ ${1:-} == "--help" ]]; then usage; exit 0; fi

client="" owner="" target_parent="" as_of="" dry_run=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --client) client=${2:-}; shift 2 ;;
    --owner) owner=${2:-}; shift 2 ;;
    --target-parent) target_parent=${2:-}; shift 2 ;;
    --as-of) as_of=${2:-}; shift 2 ;;
    --dry-run) dry_run="--dry-run"; shift ;;
    *) usage >&2; exit 2 ;;
  esac
done

if [[ -z $client || -z $owner || -z $target_parent || -z $as_of || $target_parent != /* ]]; then
  usage >&2
  exit 2
fi

repo_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
python3 "$repo_dir/scripts/scaffold_vault.py" \
  --client "$client" --owner "$owner" --out-dir "$target_parent" --as-of "$as_of" ${dry_run:+"$dry_run"}
