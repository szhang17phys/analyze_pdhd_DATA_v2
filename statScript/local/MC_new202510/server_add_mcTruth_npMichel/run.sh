#!/bin/bash
# ==========================================================
#  run_all.sh — Sequentially run 3 Python scripts
#  Author: Shuaixiang Zhang
#  Date: $(date)
# ==========================================================

set -e  # stop on any error
set -u  # treat unset variables as errors

# -----------------------------
# 1. Define paths and variables
# -----------------------------
DATA_DIR="/exp/dune/data/users/szh2/running_results/MC_PDHD_list/mcTruth_extract/mcTruth_20251042"
INITIAL_FILE="/exp/dune/data/users/szh2/running_results/MC_PDHD_list/michelt0_process_original/print_New20251042_initial.txt"
OUTPUT_FILE="./updated_New20251042_initial.txt"

STAGE1_FILE="info_jeremy_stage1.txt"
STAGE2_FILE="info_jeremy_stage2.txt"

# -----------------------------
# 2. Clean up old intermediate files
# -----------------------------
echo ">>> Cleaning up old stage files..."
rm -f "$STAGE1_FILE" "$STAGE2_FILE"
echo ">>> Old files removed (if existed)."

# -----------------------------
# 3. Run the three stages
# -----------------------------
echo ">>> Running extract_stage1.py ..."
python3 extract_stage1.py --data_dir "$DATA_DIR"

echo ">>> Running extract_stage2.py ..."
python3 extract_stage2.py

echo ">>> Running add_Michel_info.py ..."
python3 add_Michel_info.py --input "$INITIAL_FILE" --output "$OUTPUT_FILE"

echo ">>> All scripts completed successfully!"
