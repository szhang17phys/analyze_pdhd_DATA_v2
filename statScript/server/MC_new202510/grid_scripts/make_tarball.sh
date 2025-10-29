#!/bin/bash

# Exit immediately on error
set -e

# Output tarball name
TARBALL_NAME="michel20251001.tar.gz"

# Remove existing tarball if it exists
if [ -f "$TARBALL_NAME" ]; then
    echo "Removing existing $TARBALL_NAME"
    rm -f "$TARBALL_NAME"
fi

echo "Creating tarball: $TARBALL_NAME"

# Create tarball with selected contents
tar -czf "$TARBALL_NAME" \
    setup_Grid.sh \
    localProducts_larsoft_v10_08_02d00_e26_prof \
    work/my_pdhd_production/run_all.sh \
    work/my_pdhd_production/scripts \
    --exclude='*.root' \
    --exclude='*.log' \
    --exclude='*~' \
    --exclude='#*#'

# Print summary
echo "Tarball created successfully."
echo "Contents:"
tar -tzf "$TARBALL_NAME"

echo "Size:"
du -h "$TARBALL_NAME"
