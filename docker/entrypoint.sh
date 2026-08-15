#!/bin/sh
set -e

requirements="$CUSTOM_SERVICES_PATH/requirements.txt"

if [ -f "$requirements" ]; then
    echo "Installing custom service dependencies..."
    pip install --no-cache-dir --disable-pip-version-check --root-user-action=ignore -r "$requirements"
fi

echo "Starting Application."
exec everlink