#!/bin/bash
set -e

if [ $# -eq 0 ] || [ "${1#-}" != "$1" ]; then
    set -- supervisord "$@"
fi

exec "$@"
