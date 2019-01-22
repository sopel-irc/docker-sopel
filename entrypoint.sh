#!/bin/sh
set -e

# Set arguments/flags for sopel command
if [ "${#}" -eq 0 ] || [ "${1#-}" != "${1}" ]; then
  set -- sopel "${@}"
fi

# Run `sopel`
if [ "${1}" = "sopel" ]; then
  exec sopel "${@}"
fi

# Otherwise, try to run what the user specified.
exec "${@}"
