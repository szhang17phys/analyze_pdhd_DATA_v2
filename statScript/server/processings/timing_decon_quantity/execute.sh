#!/bin/bash
# Script to process a list of ROOT file links:
# 1. Run deconvolution: lar -c protodunehd_deconvolution_run.fcl -s <link>
# 2. Run Michel time matching: lar -c runmicheltime.fcl -s deconv_gen.root
# 3. Rename and move michelt0_Decon.root to TARGET_DIR with an extracted name

# --- Configuration ---
input_list="/exp/dune/data/users/szh2/running_results/PDHD_keepupData_list/beamRun_28867/rucio_metacat/ttt_rucio.txt"
TARGET_DIR="/pnfs/dune/scratch/users/szh2/pdhd_DATA_Michel/beamRun_28867_DECON/ttt"

# Check if the input list exists.
if [ ! -f "$input_list" ]; then
    echo "Error: Input list file not found: $input_list"
    exit 1
fi

# --- Processing Loop ---
while IFS= read -r file_link; do
    # Skip empty lines.
    if [ -z "$file_link" ]; then
        continue
    fi

    echo "------------------------------------------------------------"
    echo "Processing input file: $file_link"

    # Extract the basename from the URL.
    file_basename=$(basename "$file_link")
    
    # Expected file name example:
    # np04hd_raw_run028867_0385_dataflow5_datawriter_0_20240823T055509_reco_stage1_reco_stage2_20240823T134056_keepup.root
    # Extract fields 3-8 (delimited by underscores):
    # run028867_0385_dataflow5_datawriter_0_20240823T055509
    extracted=$(echo "$file_basename" | awk -F'_' '{print $3"_"$4"_"$5"_"$6"_"$7"_"$8}')
    
    # Construct the output file name.
    output_file="michelt0_decon_${extracted}.root"
    echo "Extracted base: ${extracted}"
    echo "Final output file will be named: ${output_file}"
    
    # Remove any previous output files if present.
    [ -f deconv_gen.root ] && rm deconv_gen.root
    [ -f michelt0_Decon.root ] && rm michelt0_Decon.root

    # --- Step 1: Run deconvolution ---
    echo "Running deconvolution..."
    lar -c protodunehd_deconvolution_run.fcl -s "$file_link"
    if [ $? -ne 0 ]; then
        echo "Error: Deconvolution command failed for $file_link"
        continue
    fi

    if [ ! -f deconv_gen.root ]; then
        echo "Error: deconv_gen.root was not created for $file_link"
        continue
    fi

    # --- Step 2: Run Michel time matching ---
    echo "Running Michel time matching..."
    lar -c runmicheltime.fcl -s deconv_gen.root
    if [ $? -ne 0 ]; then
        echo "Error: Michel time matching command failed for $file_link"
        continue
    fi

    if [ ! -f michelt0_Decon.root ]; then
        echo "Error: michelt0_Decon.root was not created for $file_link"
        continue
    fi

    # --- Step 3: Move and rename the output file ---
    echo "Moving and renaming michelt0_Decon.root to ${TARGET_DIR}/${output_file}"
    mv michelt0_Decon.root "${TARGET_DIR}/${output_file}"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to move and rename the file for $file_link"
        continue
    fi

    echo "Successfully processed: $file_link"
done < "$input_list"

echo "------------------------------------------------------------"
echo "All processing completed."
