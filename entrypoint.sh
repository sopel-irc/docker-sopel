#!/bin/sh
set -e

# Run `sopel` with the provided arguments
if [ "${#}" -eq 0 ] || [ "${1#-}" != "${1}" ]; then
  set -- sopel "${@}"
fi

# OR, just run sopel
if [ "${1}" = "sopel" ]; then
  exec sopel
fi

# Otherwise, try to run what the user specified.
exec "${@}"