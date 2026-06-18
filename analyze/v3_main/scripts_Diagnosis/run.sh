#!/bin/bash
# ===================================================================
#  Script: run_wvf_pipeline.sh
#  Purpose: Full waveform processing pipeline (Steps 1–6)
#  Author:  Shu
# ===================================================================

# Base directory for your dataset
base_root="/Volumes/ssd_zhang/thesis_michel/server_processing/t0_rootFiles/Offical2025_mcProduction"
base_file="/Volumes/ssd_zhang/thesis_michel/server_processing/statScript_local"



# It is enough to only change the following! (20260308)====================
# ----------------- Global Configuration ----------------------------------
# Make sure all related files in proper place:
# 1. updated_xxx_print for step 2' (extract true Info)
# 2. print.log for step 4 (removeBeam)

# Configurations:
runFolder="minus5GeV"  # <-- change this for each dataset          
runID="20250627"                    # <-- full official MC, runID is shown at event_wvf_extract

# Step 2' and Step 6
mcTruth_file1="${base_file}/add_mcTruth_npMichel/updated_${runFolder}_part1_initial.txt"
mcTruth_file2="${base_file}/add_mcTruth_npMichel/updated_${runFolder}_part2_initial.txt"
mcTruth_file3="${base_file}/add_mcTruth_npMichel/updated_${runFolder}_part3_initial.txt"

# Step 4 (if more than one print, add!)
# From server event_wvf_extract
log_files=(
    "${base_file}/event_wvf_extract/MC${runFolder}/print_part1.log"    
    "${base_file}/event_wvf_extract/MC${runFolder}/print_part2.log"
    "${base_file}/event_wvf_extract/MC${runFolder}/print_part3.log"
)

# ------------------------------------------------------------------------


# Step 1:------
# Derived directories & filenames
input_dir="${base_root}/${runFolder}/event_wvf_extract/"
merged_dir="${base_root}/${runFolder}/wvf_merged/"

# Step 2:------
output_txt="./print_count_${runID}.txt"
remove_folder="${base_root}/${runFolder}/wvf_merged_10wvfEvents/"


# Step 2':------
E_out="./print_trueE${runID}.txt"
PDG_out="./print_truePDG${runID}.txt"
MS_out="./print_trueMS${runID}.txt"
MH_out="./print_trueMH${runID}.txt"

# Step 3:------
applyCut_dir="${base_root}/${runFolder}/wvf_merged_applyCut_thre3/"


# Step 4:------
removeBeam_dir="${base_root}/${runFolder}/wvf_removeBeam_afterMerge"
beamA="-0.05" # Beam-removal cut window; [ms]
beamB="0.05"
search_window_exe4="4"


# STEP 5:------
thre_summed="0.3"
muon_txt="muon_total_${runID}.txt"
michel_txt="michel_total_${runID}.txt"
third_txt="third_total_${runID}.txt"


# STEP 6 configuration - extract TPC info
x_txt="posX_extract_${runID}.txt"
y_txt="posY_extract_${runID}.txt"
z_txt="posZ_extract_${runID}.txt"
score_txt="michelScore_extract_${runID}.txt"
hits_txt="michelHits_extract_${runID}.txt"
energy_txt="energy_extract_${runID}.txt"
lifetime_txt="lifetime_extract_${runID}.txt"
pdg_txt="pdg_extract_${runID}.txt"


# Log files------
log_exe4="print_removeBeam_${runID}.log"
# ---------------------------------------------------------------------------------



echo "=================================================================="
echo "  Pipeline (runFolder=${runFolder}, RunID=${runID})"
echo "=================================================================="







# ===============================================================
# STEP 4 — Remove Beam Window Candidates
# ===============================================================
echo ""
echo ""
echo "======== Step 4: Remove Beam Window Candidates =========="

echo "[INFO] Source directory : ${merged_dir}"
echo "[INFO] Destination dir  : ${removeBeam_dir}"
echo "[INFO] Beam window      : [${beamA}, ${beamB}] ms"
echo "[INFO] Search window    : ${search_window_exe4}"
echo "[INFO] Log file         : ${log_exe4}"
echo "--------------------------------------------------------"

echo "[INFO] Input log files:"
for lf in "${log_files[@]}"; do
    echo "       ${lf}"
done

# --- Clean or create destination directory ---
if [ -d "${removeBeam_dir}" ]; then
    echo "[WARNING] Existing directory detected: ${removeBeam_dir}"
    echo "[INFO] Removing old directory..."
    rm -rf "${removeBeam_dir}"
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to remove old directory: ${removeBeam_dir}"
        exit 93
    fi
fi

echo "[INFO] Creating new removeBeam directory: ${removeBeam_dir}"
mkdir -p "${removeBeam_dir}"
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to create removeBeam directory: ${removeBeam_dir}"
    exit 92
fi

# --- Run the Python script ---
python3 wvf_removeBeam_exe4.py \
    --src_dir "${merged_dir}" \
    --dst_dir "${removeBeam_dir}" \
    --a "${beamA}" \
    --b "${beamB}" \
    --log_files "${log_files[@]}" \
    --search_window "${search_window_exe4}" \
    > "${log_exe4}" 2>&1

if [ $? -ne 0 ]; then
    echo "[ERROR] Step 4 failed! Check ${log_exe4} for details."
    exit 5
fi

echo "[SUCCESS] Step 4 completed successfully."
echo ""



