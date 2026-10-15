#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: uninstall.sh --vault ABSOLUTE_PATH --trash-dir ABSOLUTE_PATH --confirm MOVE_TO_TRASH [--dry-run]"
}

if [[ ${1:-} == "--help" ]]; then usage; exit 0; fi

vault="" trash_dir="" confirm="" dry_run=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --vault) vault=${2:-}; shift 2 ;;
    --trash-dir) trash_dir=${2:-}; shift 2 ;;
    --confirm) confirm=${2:-}; shift 2 ;;
    --dry-run) dry_run="--dry-run"; shift ;;
    *) usage >&2; exit 2 ;;
  esac
done

if [[ -z $vault || -z $trash_dir || $vault != /* || $trash_dir != /* || $confirm != "MOVE_TO_TRASH" ]]; then
  usage >&2
  exit 2
fi

repo_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
python3 "$repo_dir/scripts/uninstall_vault.py" \
  --vault "$vault" --trash-dir "$trash_dir" --confirm "$confirm" ${dry_run:+"$dry_run"}
