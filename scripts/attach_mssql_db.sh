#!/usr/bin/env bash

# Allow running via `sh script.sh` by re-executing in bash.
if [ -z "${BASH_VERSION:-}" ]; then
    exec bash "$0" "$@"
fi

set -euo pipefail

usage() {
    cat <<'EOF'
Usage:
  attach_mssql_db.sh <path-to-file.mdf> <path-to-file.ldf> [database-name] [container-name]

Arguments:
  path-to-file.mdf   Local path to .mdf file
  path-to-file.ldf   Local path to .ldf file
  database-name      Optional. Defaults to the .mdf filename (without extension)
  container-name     Optional. Defaults to vida-db

Environment:
  MSSQL_SA_PASSWORD  Optional. SA password. If not set, script will try to read it
                     from the target container's MSSQL_SA_PASSWORD environment variable.
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    usage
    exit 0
fi

if [[ $# -lt 2 ]]; then
    usage
    exit 1
fi

MDF_PATH="$1"
LDF_PATH="$2"
DB_NAME="${3:-$(basename "$MDF_PATH" .mdf)}"
CONTAINER_NAME="${4:-vida-db}"
TARGET_DIR="/var/opt/mssql/data"

if [[ ! -f "$MDF_PATH" ]]; then
    echo "Error: MDF file not found: $MDF_PATH" >&2
    exit 1
fi

if [[ ! -f "$LDF_PATH" ]]; then
    echo "Error: LDF file not found: $LDF_PATH" >&2
    exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
    echo "Error: docker is not installed or not in PATH." >&2
    exit 1
fi

if ! docker ps --format '{{.Names}}' | grep -qx "$CONTAINER_NAME"; then
    echo "Error: container '$CONTAINER_NAME' is not running." >&2
    exit 1
fi

SA_PASSWORD="${MSSQL_SA_PASSWORD:-}"
if [[ -z "$SA_PASSWORD" ]]; then
    SA_PASSWORD="$(docker inspect -f '{{range .Config.Env}}{{println .}}{{end}}' "$CONTAINER_NAME" | sed -n 's/^MSSQL_SA_PASSWORD=//p' | tail -n 1 2>/dev/null || true)"
fi

if [[ -z "$SA_PASSWORD" ]]; then
    echo "Error: MSSQL SA password is missing. Set MSSQL_SA_PASSWORD or ensure the container has MSSQL_SA_PASSWORD configured." >&2
    exit 1
fi

MDF_BASENAME="$(basename "$MDF_PATH")"
LDF_BASENAME="$(basename "$LDF_PATH")"
MDF_TARGET="$TARGET_DIR/$MDF_BASENAME"
LDF_TARGET="$TARGET_DIR/$LDF_BASENAME"

if docker exec "$CONTAINER_NAME" test -x /opt/mssql-tools18/bin/sqlcmd; then
    SQLCMD_BIN="/opt/mssql-tools18/bin/sqlcmd"
elif docker exec "$CONTAINER_NAME" test -x /opt/mssql-tools/bin/sqlcmd; then
    SQLCMD_BIN="/opt/mssql-tools/bin/sqlcmd"
else
    echo "Error: sqlcmd not found in container '$CONTAINER_NAME'." >&2
    exit 1
fi

echo "Copying data files into container..."
docker cp "$MDF_PATH" "$CONTAINER_NAME:$MDF_TARGET"
docker cp "$LDF_PATH" "$CONTAINER_NAME:$LDF_TARGET"

DB_NAME_ESCAPED="${DB_NAME//]/]]}"
DB_NAME_SQL="${DB_NAME//\'/\'\'}"
read -r -d '' SQL <<EOF || true
IF DB_ID(N'$DB_NAME_SQL') IS NOT NULL
    THROW 50000, N'Database already exists.', 1;

CREATE DATABASE [$DB_NAME_ESCAPED]
ON (FILENAME = N'$MDF_TARGET'),
   (FILENAME = N'$LDF_TARGET')
FOR ATTACH;
EOF

echo "Attaching database '$DB_NAME' to SQL Server in container '$CONTAINER_NAME'..."
docker exec -e SQLCMDPASSWORD="$SA_PASSWORD" "$CONTAINER_NAME" \
    "$SQLCMD_BIN" -S localhost -U sa -C -b -Q "$SQL"

echo "Done. Database '$DB_NAME' attached successfully."
