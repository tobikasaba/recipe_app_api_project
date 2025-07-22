#!/bin/sh

# Exit immediately if any command returns a non-zero status/command fails. The script stops
set -e

# Replace environment variable placeholders in the template
# (/etc/nginx/default.conf.tpl) with their current values
# and write the result to nginx’s active config directory.
envsubst < /etc/nginx/default.conf.tpl > /etc/nginx/conf.d/default.conf

# Launch nginx in the foreground so the Docker container stays running
nginx -g 'daemon off;'