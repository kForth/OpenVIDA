#!/usr/bin/env bash

# Allow running via `sh script.sh` by re-executing in bash.
if [ -z "${BASH_VERSION:-}" ]; then
    exec bash "$0" "$@"
fi

set -euo pipefail

usage() {
    cat <<'EOF'
Usage:
    attach_mssql_from_yml.sh <container-name> <path-to-db_files.yml> <db-files-directory>

Arguments:
  container-name         Name of the running SQL Server container (e.g. vida-db)
  path-to-db_files.yml   Path to YAML file containing database entries.
                         Expected entry keys: database, mdf, ldf
    db-files-directory     Directory containing MDF/LDF files referenced by YAML.

Notes:
    - mdf/ldf values in YAML are treated as filenames.
    - Paths are built as <db-files-directory>/<mdf-or-ldf-filename>.
  - Each entry is attached by calling scripts/attach_mssql_db.sh.
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    usage
    exit 0
fi

if [[ $# -ne 3 ]]; then
    usage
    exit 1
fi

CONTAINER_NAME="$1"
YAML_FILE="$2"
DB_FILES_DIR="$3"
ATTACH_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ATTACH_SCRIPT="$ATTACH_SCRIPT_DIR/attach_mssql_db.sh"

if [[ ! -f "$YAML_FILE" ]]; then
    echo "Error: YAML file not found: $YAML_FILE" >&2
    exit 1
fi

if [[ ! -f "$ATTACH_SCRIPT" ]]; then
    echo "Error: attach script not found: $ATTACH_SCRIPT" >&2
    exit 1
fi

if [[ ! -d "$DB_FILES_DIR" ]]; then
    echo "Error: DB files directory not found: $DB_FILES_DIR" >&2
    exit 1
fi

build_file_path() {
    local file_name="$1"

    # Strip optional wrapping single/double quotes from YAML scalar values.
    file_name="${file_name#\"}"
    file_name="${file_name%\"}"
    file_name="${file_name#\'}"
    file_name="${file_name%\'}"

    # Use only the filename component from YAML.
    file_name="$(basename "$file_name")"
    echo "$DB_FILES_DIR/$file_name"
}

current_db=""
current_mdf=""
current_ldf=""
entry_count=0

run_entry() {
    if [[ -z "$current_db" && -z "$current_mdf" && -z "$current_ldf" ]]; then
        return 0
    fi

    if [[ -z "$current_db" || -z "$current_mdf" || -z "$current_ldf" ]]; then
        echo "Error: Incomplete entry in YAML. Required keys: database, mdf, ldf" >&2
        exit 1
    fi

    local mdf_path
    local ldf_path
    mdf_path="$(build_file_path "$current_mdf")"
    ldf_path="$(build_file_path "$current_ldf")"

    echo "Attaching database '$current_db'..."
    "$ATTACH_SCRIPT" "$mdf_path" "$ldf_path" "$current_db" "$CONTAINER_NAME"

    entry_count=$((entry_count + 1))
    current_db=""
    current_mdf=""
    current_ldf=""
}

while IFS= read -r raw_line || [[ -n "$raw_line" ]]; do
    line="${raw_line%$'\r'}"

    if [[ "$line" =~ ^[[:space:]]*-[[:space:]]*database:[[:space:]]*(.+)[[:space:]]*$ ]]; then
        run_entry
        current_db="${BASH_REMATCH[1]}"
        continue
    fi

    if [[ "$line" =~ ^[[:space:]]*database:[[:space:]]*(.+)[[:space:]]*$ ]]; then
        current_db="${BASH_REMATCH[1]}"
        continue
    fi

    if [[ "$line" =~ ^[[:space:]]*mdf:[[:space:]]*(.+)[[:space:]]*$ ]]; then
        current_mdf="${BASH_REMATCH[1]}"
        continue
    fi

    if [[ "$line" =~ ^[[:space:]]*ldf:[[:space:]]*(.+)[[:space:]]*$ ]]; then
        current_ldf="${BASH_REMATCH[1]}"
        continue
    fi
done < "$YAML_FILE"

run_entry

if [[ $entry_count -eq 0 ]]; then
    echo "Error: No valid database entries found in YAML file." >&2
    exit 1
fi

echo "Done. Attached $entry_count database(s)."
