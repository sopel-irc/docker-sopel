#!/bin/sh
set -e

export PATH="/home/sopel/.local/bin:${PATH}"

# Set arguments/flags for sopel command
if [ "${#}" -eq 0 ] || [ "${1#-}" != "${1}" ]; then
  set -- sopel "${@}"
fi

if [ "${1}" = "sopel" ]; then
  exec su-exec sopel "${@}"
fi

if [ -n "${USER}" ]; then
  set -- su-exec "${USER}" "${@}"
fi

exec "${@}"