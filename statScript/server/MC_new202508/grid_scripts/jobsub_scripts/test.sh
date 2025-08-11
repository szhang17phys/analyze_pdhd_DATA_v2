#!/bin/bash

echo "[INFO] Starting GEN-only test job with -e option..."

# Get unique job ID (from CLUSTER_PROCESS or fallback to PID)
jobid="${CLUSTER_PROCESS:-$$}"

# Simulation settings
RUN_ID=1
EVENTS_PER_JOB=5
FIRST_EVENT=$(( jobid * EVENTS_PER_JOB + 1 ))
START_EVENT_STRING="${RUN_ID}:0:${FIRST_EVENT}"
echo "[INFO] Event offset set via -e '${START_EVENT_STRING}'"

# Timestamp for file naming
timestamp=$(date -u +%Y%m%dT%H%M%SZ)

# Path to FHiCL
GEN_FCL="./prod_cosmics_radiologicals_protodunehd.fcl"

# Run GEN stage with event offset and output filename
lar -c "$GEN_FCL" -n $EVENTS_PER_JOB -e "$START_EVENT_STRING" \
    -o "cosmic_gen_${jobid}_${timestamp}.root"

# Check status
if [ $? -ne 0 ]; then
    echo "[ERROR] GEN stage failed"
    exit 2
fi

echo "[INFO] GEN stage completed successfully."
ls -lh "cosmic_gen_${jobid}_${timestamp}.root"
