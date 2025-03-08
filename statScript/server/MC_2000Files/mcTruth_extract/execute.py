import os
import subprocess
import re

# Define paths
input_file = "/exp/dune/data/users/szh2/running_results/MC_PDHD_list/beam_cosmics_onlineExample/test_rucio.txt"
output_dir = "/exp/dune/data/users/szh2/running_results/MC_PDHD_list/mcTruth_extract"

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Read the root file links
with open(input_file, 'r') as f:
    root_files = [line.strip() for line in f.read().splitlines() if line.strip()]

# Loop through each root file and execute the command
for root_file in root_files:
    # Extract relevant filename segment using regex
    match = re.search(r'prod_.*?_(\d{8}T\d{6}Z_\d{6}_\d{6}_g4_stage1_g4_stage2_sce_off)', root_file)
    base_name = match.group(1) if match else os.path.basename(root_file).replace(".root", "")
    output_file = os.path.join(output_dir, f"{base_name}.txt")
    
    # Construct the command
    command = ["lar", "-c", "pdhd_Truechecks.fcl", "-s", root_file]
    
    # Execute the command and save output
    with open(output_file, "w") as out:
        process = subprocess.run(command, stdout=out, stderr=subprocess.STDOUT, text=True)
    
    print(f"Processed {root_file} -> {output_file}")
