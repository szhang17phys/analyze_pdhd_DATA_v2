#!/bin/bash
# ===================================================================
#  Script: run_wvf_pipeline.sh
#  Purpose: Full waveform processing pipeline (Steps 1–6)
#  Author:  Shu
# ===================================================================

# ----------------- Global Configuration ------------------
DATE="20251043"          # <-- change this for each dataset
runID="43"

# ---------------------------------------------------------


# Base directory for your dataset
base_root="/Volumes/ssd_zhang/work/thesis_michel/server_processing/t0_rootFiles"

# mcTruth files
mcTruth_file="/Volumes/ssd_zhang/work/thesis_michel/server_processing/statScript_local/add_mcTruth_npMichel/updated_New${DATE}_initial.txt"



# Derived directories & filenames
input_dir="${base_root}/event_wvf_extract_${DATE}/"
merged_dir="${base_root}/wvf_merged_${DATE}/"
output_txt="./print_wvfCoin_count${DATE}.txt"

# localtion of applyCut directory 
input_dir_peak="${base_root}/wvf_merged_applyCut_${DATE}/"

# Log files
log_exe1="print_wvfCoin_merged${DATE}.log"
log_exe2="print_wvfCoin_count${DATE}.log"
log_exe3="print_trueInfo${DATE}.log"
log_exe4="print_applyCut${DATE}.log"
# --------------------------------------------------------

echo "=================================================================="
echo "   Waveform Processing Pipeline (DATE=${DATE}, RunID=${runID})"
echo "=================================================================="

# ===============================================================
# STEP 1 — Waveform Merging
# ===============================================================
echo ""
echo "=================== Step 1: Merging ==================="
echo "[INFO] Input directory : ${input_dir}"
echo "[INFO] Output directory: ${merged_dir}"
echo "[INFO] Run ID          : ${runID}"
echo "[INFO] Log file        : ${log_exe1}"
echo "--------------------------------------------------------"

# === Clean up old directory and recreate ===
if [ -d "${merged_dir}" ]; then
    echo "[WARNING] Existing directory detected: ${merged_dir}"
    echo "[INFO] Removing old directory..."
    rm -rf "${merged_dir}"
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to remove old directory: ${merged_dir}"
        exit 99
    fi
fi

echo "[INFO] Creating fresh output directory: ${merged_dir}"
mkdir -p "${merged_dir}"
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to create output directory: ${merged_dir}"
    exit 98
fi

# ===== Run merging script =====
python3 wvf_coin_merged_exe1.py \
    --input_dir "${input_dir}" \
    --output_dir "${merged_dir}" \
    --runID "${runID}" \
    > "${log_exe1}" 2>&1

if [ $? -ne 0 ]; then
    echo "[ERROR] Step 1 failed! Check ${log_exe1} for details."
    exit 1
fi
echo "[SUCCESS] Step 1 completed successfully."
echo ""

# ===============================================================
# STEP 2 — Coincidence Counting
# ===============================================================
echo ""
echo ""
echo "=================== Step 2: Coincidence Count ==================="
echo "[INFO] Input directory : ${merged_dir}"
echo "[INFO] Output txt file : ${output_txt}"
echo "[INFO] Log file        : ${log_exe2}"
echo "--------------------------------------------------------"

python3 wvf_coin_count_exe2.py \
    --input_dir "${merged_dir}" \
    --output_txt "${output_txt}" \
    > "${log_exe2}" 2>&1

if [ $? -ne 0 ]; then
    echo "[ERROR] Step 2 failed! Check ${log_exe2} for details."
    exit 2
fi
echo "[SUCCESS] Step 2 completed successfully."
echo ""

# ===============================================================
# STEP 3 — Extract True PDG and Energy
# ===============================================================
echo ""
echo ""
echo "=================== Step 3: Extract True Info ==================="


wvfCoin_file="./print_wvfCoin_count${DATE}.txt"

# Output files
E_out="./print_trueE${DATE}.txt"
PDG_out="./print_truePDG${DATE}.txt"

echo "[INFO] mcTruth file : ${mcTruth_file}"
echo "[INFO] wvfCoin file : ${wvfCoin_file}"
echo "[INFO] Output E     : ${E_out}"
echo "[INFO] Output PDG   : ${PDG_out}"
echo "[INFO] Log file     : ${log_exe3}"
echo "--------------------------------------------------------"

python3 extract_trueInfo_exe3.py \
    --mcTruth_file "${mcTruth_file}" \
    --wvfCoin_file "${wvfCoin_file}" \
    --E_out "${E_out}" \
    --PDG_out "${PDG_out}" \
    > "${log_exe3}" 2>&1

if [ $? -ne 0 ]; then
    echo "[ERROR] Step 3 failed! Check ${log_exe3} for details."
    exit 3
fi
echo "[SUCCESS] Step 3 completed successfully."
echo ""

# ===============================================================
# STEP 4 — Apply Waveform Coincidence Cut
# ===============================================================
echo ""
echo ""
echo "=================== Step 4: Apply Waveform Coincidence Cut ==================="

# Input/output directories
source_dir="${base_root}/wvf_merged_${DATE}/"
dest_dir="${base_root}/wvf_merged_applyCut_${DATE}/"

echo "[INFO] Source directory : ${source_dir}"
echo "[INFO] Destination dir  : ${dest_dir}"
echo "[INFO] Log file         : ${log_exe4}"
echo "--------------------------------------------------------"

# --- Clean or create destination directory ---
if [ -d "${dest_dir}" ]; then
    echo "[WARNING] Existing directory detected: ${dest_dir}"
    echo "[INFO] Removing old directory..."
    rm -rf "${dest_dir}"
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to remove old directory: ${dest_dir}"
        exit 94
    fi
fi

echo "[INFO] Creating new destination directory: ${dest_dir}"
mkdir -p "${dest_dir}"
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to create destination directory: ${dest_dir}"
    exit 95
fi

# --- Run the Python script ---
python3 wvf_coin_applyCut_exe4.py \
    --source_dir "${source_dir}" \
    --dest_dir "${dest_dir}" \
    > "${log_exe4}" 2>&1

if [ $? -ne 0 ]; then
    echo "[ERROR] Step 4 failed! Check ${log_exe4} for details."
    exit 4
fi
echo "[SUCCESS] Step 4 completed successfully."
echo ""


# ===============================================================
# STEP 5 — Peak Finding and Intensity Extraction
# ===============================================================
echo ""
echo ""
echo "=================== Step 5: Peak Finding and Intensity Extraction ==================="


log_exe5="./print_intensity_thre${DATE}.log"

echo "[INFO] Input directory : ${input_dir_peak}"
echo "[INFO] Log file        : ${log_exe5}"
echo "[INFO] DATE            : ${DATE}"
echo "--------------------------------------------------------"

# --- Run ROOT macro and pass DATE and input_dir_peak ---
root -l -b -q "./intensity_thre_exe5.C(\"${DATE}\", \"${input_dir_peak}\")" > "${log_exe5}" 2>&1

if [ $? -ne 0 ]; then
    echo "[ERROR] Step 5 failed! Check ${log_exe5} for details."
    exit 5
fi
echo "[SUCCESS] Step 5 completed successfully."
echo ""





# ===============================================================
# STEP 6 — Extract Final True Information
# ===============================================================
echo ""
echo ""
echo "=================== Step 6: Extract Final True Information ==================="

log_exe6="./print_final_trueInfo.log"



echo "[INFO] DATE variable     : ${DATE}"
echo "[INFO] Python script     : final_true_info_exe6.py"
echo "[INFO] mcTruth path      : ${mcTruth_file}"
echo "[INFO] Log file          : ${log_exe6}"
echo "--------------------------------------------------------"

# Run Python with environment variables
DATE="${DATE}" MCTRUTH_PATH="${mcTruth_file}" python3 final_true_info_exe6.py > "${log_exe6}" 2>&1

if [ $? -ne 0 ]; then
    echo "[ERROR] Step 6 failed! Check ${log_exe6} for details."
    exit 6
fi
echo "[SUCCESS] Step 6 completed successfully."
echo ""
echo "=================== All Defined Steps Completed ==================="

