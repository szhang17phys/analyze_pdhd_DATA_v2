import subprocess
import re
import os

# Input and output file names
input_file = "run005809_metacat_6856Files.txt"
output_file = "rucio_paths_Full.txt"

# Regex pattern to extract the root:// URL
#url_pattern = re.compile(r'(root://[\w\.:/-]+)')
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
