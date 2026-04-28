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
runFolder="pos5GeV"  # <-- change this for each dataset          
runID="20250623"                    # <-- full official MC, runID is shown at event_wvf_extract

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
removeBeam_dir="${base_root}/${runFolder}/wvf_applyCut_removeBeam"
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
log_exe1="print_merged_${runID}.log"
log_exe2="print_count_${runID}.log"
log_exe2p="print_trueInfo${runID}.log"
log_exe3="print_applyCut${runID}.log"
log_exe4="print_removeBeam_${runID}.log"
log_exe5="print_intensityThre_${runID}.log"
log_exe6="print_extractTPC_${runID}.log"
# ---------------------------------------------------------------------------------



echo "=================================================================="
echo "  Pipeline (runFolder=${runFolder}, RunID=${runID})"
echo "=================================================================="



# # ===============================================================
# # STEP 1 — Waveform Merging
# # ===============================================================
# echo ""
# echo "=================== Step 1: Merging ==================="
# echo "[INFO] Input directory : ${input_dir}"
# echo "[INFO] Output directory: ${merged_dir}"
# echo "[INFO] Run ID          : ${runID}"
# echo "[INFO] Log file        : ${log_exe1}"
# echo "--------------------------------------------------------"

# # === Clean up old directory and recreate ===
# if [ -d "${merged_dir}" ]; then
#     echo "[WARNING] Existing directory detected: ${merged_dir}"
#     echo "[INFO] Removing old directory..."
#     rm -rf "${merged_dir}"
#     if [ $? -ne 0 ]; then
#         echo "[ERROR] Failed to remove old directory: ${merged_dir}"
#         exit 99
#     fi
# fi

# echo "[INFO] Creating fresh output directory: ${merged_dir}"
# mkdir -p "${merged_dir}"
# if [ $? -ne 0 ]; then
#     echo "[ERROR] Failed to create output directory: ${merged_dir}"
#     exit 98
# fi

# # ===== Run merging script =====
# python3 wvf_coin_merged_exe1.py \
#     --input_dir "${input_dir}" \
#     --output_dir "${merged_dir}" \
#     > "${log_exe1}" 2>&1

# if [ $? -ne 0 ]; then
#     echo "[ERROR] Step 1 failed! Check ${log_exe1} for details."
#     exit 1
# fi
# echo "[SUCCESS] Step 1 completed successfully."
# echo ""





# ===============================================================
# STEP 2 — Coincidence Counting
# ===============================================================
echo ""
echo ""
echo "=================== Step 2: Coincidence Count ==================="
echo "[INFO] Input directory    : ${merged_dir}"
echo "[INFO] 'Remove' directory : ${remove_folder}"
echo "[INFO] Output txt file    : ${output_txt}"
echo "[INFO] Log file           : ${log_exe2}"
echo "--------------------------------------------------------"

python3 wvf_coin_count_exe2.py \
    --input_dir "${merged_dir}" \
    --output_txt "${output_txt}" \
    --remove_dir "${remove_folder}" \
    > "${log_exe2}" 2>&1

if [ $? -ne 0 ]; then
    echo "[ERROR] Step 2 failed! Check ${log_exe2} for details."
    exit 2
fi
echo "[SUCCESS] Step 2 completed successfully."
echo ""



# ===============================================================
# STEP 2' — Extract True PDG and Energy
# ===============================================================
echo ""
echo ""
echo "=================== Step 2': Extract True Info ==================="

output_txt="./print_count_${runID}.txt"


echo "[INFO] mcTruth file : ${mcTruth_file1}"
echo "[INFO] mcTruth file : ${mcTruth_file2}"
echo "[INFO] mcTruth file : ${mcTruth_file3}"
echo "[INFO] wvfCoin file : ${output_txt}"
echo "[INFO] Output E     : ${E_out}"
echo "[INFO] Output PDG   : ${PDG_out}"
echo "[INFO] Output MS    : ${MS_out}"
echo "[INFO] Output MH    : ${MH_out}"
echo "[INFO] Log file     : ${log_exe2p}"
echo "--------------------------------------------------------"

python3 extract_trueInfo_exe2p.py \
    --mcTruth_file1 "${mcTruth_file1}" \
    --mcTruth_file2 "${mcTruth_file2}" \
    --mcTruth_file3 "${mcTruth_file3}" \
    --wvfCoin_file "${output_txt}" \
    --E_out "${E_out}" \
    --PDG_out "${PDG_out}" \
    --MS_out "${MS_out}" \
    --MH_out "${MH_out}" \
    > "${log_exe2p}" 2>&1

if [ $? -ne 0 ]; then
    echo "[ERROR] Step 2p failed! Check ${log_exe2p} for details."
    exit 3
fi
echo "[SUCCESS] Step 2p completed successfully."
echo ""




# # ===============================================================
# # STEP 3 — Apply Waveform Coincidence Cut
# # ===============================================================
# echo ""
# echo ""
# echo "======== Step 3: Apply Wvf Coincidence Cut =========="


# echo "[INFO] Source directory : ${merged_dir}"
# echo "[INFO] Destination dir  : ${applyCut_dir}"
# echo "[INFO] Log file         : ${log_exe3}"
# echo "--------------------------------------------------------"

# # --- Clean or create destination directory ---
# if [ -d "${applyCut_dir}" ]; then
#     echo "[WARNING] Existing directory detected: ${applyCut_dir}"
#     echo "[INFO] Removing old directory..."
#     rm -rf "${applyCut_dir}"
#     if [ $? -ne 0 ]; then
#         echo "[ERROR] Failed to remove old directory: ${applyCut_dir}"
#         exit 94
#     fi
# fi

# echo "[INFO] Creating new applyCut directory: ${applyCut_dir}"
# mkdir -p "${applyCut_dir}"
# if [ $? -ne 0 ]; then
#     echo "[ERROR] Failed to create applyCut directory: ${applyCut_dir}"
#     exit 95
# fi

# # --- Run the Python script ---
# python3 wvf_coin_applyCut_exe3.py \
#     --source_dir "${merged_dir}" \
#     --dest_dir "${applyCut_dir}" \
#     > "${log_exe3}" 2>&1

# if [ $? -ne 0 ]; then
#     echo "[ERROR] Step 3 failed! Check ${log_exe3} for details."
#     exit 4
# fi
# echo "[SUCCESS] Step 3 completed successfully."
# echo ""






# # ===============================================================
# # STEP 4 — Remove Beam Window Candidates
# # ===============================================================
# echo ""
# echo ""
# echo "======== Step 4: Remove Beam Window Candidates =========="

# echo "[INFO] Source directory : ${applyCut_dir}"
# echo "[INFO] Destination dir  : ${removeBeam_dir}"
# echo "[INFO] Beam window      : [${beamA}, ${beamB}] ms"
# echo "[INFO] Search window    : ${search_window_exe4}"
# echo "[INFO] Log file         : ${log_exe4}"
# echo "--------------------------------------------------------"

# echo "[INFO] Input log files:"
# for lf in "${log_files[@]}"; do
#     echo "       ${lf}"
# done

# # --- Clean or create destination directory ---
# if [ -d "${removeBeam_dir}" ]; then
#     echo "[WARNING] Existing directory detected: ${removeBeam_dir}"
#     echo "[INFO] Removing old directory..."
#     rm -rf "${removeBeam_dir}"
#     if [ $? -ne 0 ]; then
#         echo "[ERROR] Failed to remove old directory: ${removeBeam_dir}"
#         exit 93
#     fi
# fi

# echo "[INFO] Creating new removeBeam directory: ${removeBeam_dir}"
# mkdir -p "${removeBeam_dir}"
# if [ $? -ne 0 ]; then
#     echo "[ERROR] Failed to create removeBeam directory: ${removeBeam_dir}"
#     exit 92
# fi

# # --- Run the Python script ---
# python3 wvf_removeBeam_exe4.py \
#     --src_dir "${applyCut_dir}" \
#     --dst_dir "${removeBeam_dir}" \
#     --a "${beamA}" \
#     --b "${beamB}" \
#     --log_files "${log_files[@]}" \
#     --search_window "${search_window_exe4}" \
#     > "${log_exe4}" 2>&1

# if [ $? -ne 0 ]; then
#     echo "[ERROR] Step 4 failed! Check ${log_exe4} for details."
#     exit 5
# fi

# echo "[SUCCESS] Step 4 completed successfully."
# echo ""






# # ===============================================================
# # STEP 5 — Intensity Threshold Peak Finding
# # ===============================================================
# echo ""
# echo ""
# echo "======== Step 5: Intensity Threshold Peak Finding =========="

# echo "[INFO] Input directory  : ${removeBeam_dir}"
# echo "[INFO] Threshold        : ${thre_summed}"
# echo "[INFO] Muon txt         : ${muon_txt}"
# echo "[INFO] Michel txt       : ${michel_txt}"
# echo "[INFO] Third txt        : ${third_txt}"
# echo "[INFO] Log file         : ${log_exe5}"
# echo "--------------------------------------------------------"

# root -l -b -q "intensity_thre_exe5.C(\"${removeBeam_dir}\", ${thre_summed}, \"${muon_txt}\", \"${michel_txt}\", \"${third_txt}\")" \
#     > "${log_exe5}" 2>&1

# if [ $? -ne 0 ]; then
#     echo "[ERROR] Step 5 failed! Check ${log_exe5} for details."
#     exit 6
# fi

# echo "[SUCCESS] Step 5 completed successfully."
# echo ""





# # ===============================================================
# # STEP 6 — Extract TPC Info
# # ===============================================================
# echo ""
# echo ""
# echo "======== Step 6: Extract TPC Info =========="

# echo "[INFO] mcTruth file 1   : ${mcTruth_file1}"
# echo "[INFO] mcTruth file 2   : ${mcTruth_file2}"
# echo "[INFO] mcTruth file 3   : ${mcTruth_file3}"
# echo "[INFO] Muon txt         : ${muon_txt}"
# echo "[INFO] X output         : ${x_txt}"
# echo "[INFO] Y output         : ${y_txt}"
# echo "[INFO] Z output         : ${z_txt}"
# echo "[INFO] Score output     : ${score_txt}"
# echo "[INFO] Hits output      : ${hits_txt}"
# echo "[INFO] TrueE output     : ${energy_txt}"
# echo "[INFO] PDG output       : ${pdg_txt}"
# echo "[INFO] Lifetime output  : ${lifetime_txt}"
# echo "[INFO] Log file         : ${log_exe6}"
# echo "--------------------------------------------------------"

# python3 extract_tpc_info_exe6.py \
#     --mcTruth_file1 "${mcTruth_file1}" \
#     --mcTruth_file2 "${mcTruth_file2}" \
#     --mcTruth_file3 "${mcTruth_file3}" \
#     --muon_txt "${muon_txt}" \
#     --x_out "${x_txt}" \
#     --y_out "${y_txt}" \
#     --z_out "${z_txt}" \
#     --score_out "${score_txt}" \
#     --hits_out "${hits_txt}" \
#     --E_out "${energy_txt}" \
#     --PDG_out "${pdg_txt}" \
#     --lifetime_out "${lifetime_txt}" \
#     > "${log_exe6}" 2>&1

# if [ $? -ne 0 ]; then
#     echo "[ERROR] Step 6 failed! Check ${log_exe6} for details."
#     exit 7
# fi

# echo "[SUCCESS] Step 6 completed successfully."
# echo ""

