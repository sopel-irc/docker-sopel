#!/bin/sh
set -e

export PATH="/home/sopel/.local/bin:${PATH}"

# Define functions
change_uid () {
  NEW_UID="${1}"
  echo -n "Setting UID for user sopel to ${NEW_UID}... "
  (usermod -u "${NEW_UID}" sopel && echo "Done.") || (echo "FAILED!" && return 1)
}

change_gid () {
  NEW_GID="${1}"
  echo -n "Setting GID for user sopel to ${NEW_GID}... "
  (groupmod -g "${NEW_GID}" sopel && echo "Done.") || (echo "FAILED!" && return 1)
}

# Check if IDs need to be changed
[ -n "${PUID}" ] && change_uid "${PUID}"
[ -n "${PGID}" ] && change_gid "${PGID}"

# Set arguments/flags for sopel command
if [ "${#}" -eq 0 ] || [ "${1#-}" != "${1}" ]; then
  set -- sopel "${@}"
fi

if [ "${1}" = "sopel" ]; then
  if [ -f "/pypi_packages.txt" ]; then
    cat /pypi_packages.txt | grep -v '^#' | grep -v '^$' | \
      while read line; do
        [ "${line}" = "\#*" ] && continue
        su-exec sopel pip install --user "${line}"
      done
  fi
  exec su-exec sopel "${@}"
fi

if [ -n "${USER}" ]; then
  set -- su-exec "${USER}" "${@}"
fi

exec "${@}"