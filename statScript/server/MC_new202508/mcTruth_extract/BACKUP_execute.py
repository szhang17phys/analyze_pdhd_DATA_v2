import os
import subprocess
import re

import os
import subprocess
import re

# Define input/output paths
input_dir = "/pnfs/dune/scratch/users/szh2/MC_pdhd_Michel/my_production_20250804"
output_dir = "/exp/dune/data/users/szh2/running_results/MC_PDHD_list/mcTruth_extract/new20250804_MC"

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Get all .root files in the input directory (non-recursive)
root_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith(".root")]

# Loop through each root file and execute the command
for root_file in root_files:

    # Extract the string after "reco_" and before ".root"
    match = re.search(r'reco_(.*)\.root', os.path.basename(root_file))
    base_name = match.group(1) if match else os.path.basename(root_file).replace(".root", "")
    output_file = os.path.join(output_dir, f"{base_name}.txt")

    
    # Construct the command
    command = ["lar", "-c", "pdhd_Truechecks.fcl", "-s", root_file]
    
    # Execute the command and save output
    with open(output_file, "w") as out:
        process = subprocess.run(command, stdout=out, stderr=subprocess.STDOUT, text=True)
    
    print(f"Processed {root_file} -> {output_file}")

