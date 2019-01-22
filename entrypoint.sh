#!/bin/sh
set -e

# Set arguments/flags for sopel command
if [ "${#}" -eq 0 ] || [ "${1#-}" != "${1}" ]; then
  set -- sopel "${@}"
fi

exec "${@}"