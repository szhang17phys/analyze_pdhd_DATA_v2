#!/bin/bash
# ==========================================================
#  run_cut_extract.sh — Run cut.py then extractValues.py
# ==========================================================

set -e
set -u

# -----------------------------
# Define input/output files
# -----------------------------
INITIAL_FILE="/exp/dune/data/users/szh2/running_results/MC_PDHD_list/michelt0_process_original/print_New20251042_initial.txt"
FILTERED_FILE="./filtered_New20251042_print.txt"

# -----------------------------
# Clean old filtered file
# -----------------------------
echo ">>> Cleaning old filtered file..."
rm -f "$FILTERED_FILE"

# -----------------------------
# Step 1: cut.py
# -----------------------------
echo ">>> Running cut.py ..."
python3 cut.py --input "$INITIAL_FILE" --output "$FILTERED_FILE"

# -----------------------------
# Step 2: extractValues.py
# -----------------------------
echo ">>> Running extractValues.py ..."
python3 extractValues.py --input "$FILTERED_FILE"

# -----------------------------
# Step 3: sorting.py
# -----------------------------
echo ">>> Running sorting.py ..."
python3 sorting.py


echo ">>> All steps completed successfully!"
