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
DATA_DIR="/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/t0_rootFiles/new202510_MC/mcTruth_20251032"
INITIAL_FILE="/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/analyze_pdhd_DATA_v2/statScript/server/MC_new202510/michelt0_process_original/print_New20251032_initial.txt"
OUTPUT_FILE="./updated_New20251032_initial.txt"

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
