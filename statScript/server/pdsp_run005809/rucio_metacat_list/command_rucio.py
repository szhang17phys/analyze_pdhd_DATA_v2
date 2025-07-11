import subprocess
import re
import os

# Input and output file names
input_file = "run005809_metacat_6856Files.txt"
output_file = "rucio_paths_Full.txt"

#Example: root://fndca1.fnal.gov:1094/pnfs/fnal.gov/usr/dune/tape_backed/dunepro//protodune-sp/full-reconstructed/2020/detector/physics/PDSPProd4/00/00/58/09/np04_raw_run005809_0052_dl6_reco1_39134907_0_20201111T043652Z.root

# Regex pattern to extract the root:// URL
#url_pattern = re.compile(r'(root://[\w\.:/-]*persistent[\w\.:/-]*)')
url_pattern = re.compile(r'(root://[\w\.:/-]*persistent[\w\.:/-]*)')

# Get the actual username
user = os.getenv("USER")

with open(input_file, "r") as infile, open(output_file, "w") as outfile:
    for line in infile:
        dataset = line.strip()
        if dataset:
            # Construct the rucio command with actual username
            cmd = ["rucio", "-a", "justinreadonly", "list-file-replicas", dataset]
            
            print(f"Executing command: {' '.join(cmd)}")
            
            try:
                # Run the command and capture output
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                
                # Extract file paths using regex
                matches = url_pattern.findall(result.stdout)
                for match in matches:
                    outfile.write(match + "\n")
                    print("Extracted:", match)
            except subprocess.CalledProcessError as e:
                print(f"Error processing {dataset}: {e}")
                print("Standard Error:", e.stderr)
