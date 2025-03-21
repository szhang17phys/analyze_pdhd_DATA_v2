import os
import re

# --- Part 1: Process noMerge folder ---
noMerge_input_dir = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/t0_rootFiles/data/small_test/noMerge_wvf_coincidence"
noMerge_output_txt = "./singleTest_results/noMerge_opNum_values.txt"

# Regex pattern to match "opNum" followed by one or more digits
pattern = re.compile(r"opNum(\d+)")

# List to hold extracted values for noMerge folder
extracted_values_noMerge = []

# Iterate over all ROOT files in the noMerge directory
for filename in os.listdir(noMerge_input_dir):
    if filename.endswith(".root"):
        match = pattern.search(filename)
        if match:
            value = match.group(1)
            extracted_values_noMerge.append(value)

# Write the extracted values to a text file (one value per line)
with open(noMerge_output_txt, "w") as f:
    for value in extracted_values_noMerge:
        f.write(value + "\n")

print(f"Extracted {len(extracted_values_noMerge)} opNum values from noMerge folder. Saved in {noMerge_output_txt}.")

# --- Part 2: Process merged folder ---
merged_input_dir = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/t0_rootFiles/data/small_test/merged_wvf_coincidence"
merged_output_txt = "./singleTest_results/merged_opNum_values.txt"

# List to hold extracted values for merged folder
extracted_values_merged = []

# Iterate over all ROOT files in the merged directory
for filename in os.listdir(merged_input_dir):
    if filename.endswith(".root"):
        match = pattern.search(filename)
        if match:
            # Extract the number after "opNum" as an integer
            value = int(match.group(1))
            # For filenames with "_merged", add 1 to the extracted value
            if "_merged" in filename:
                value += 1
            extracted_values_merged.append(str(value))

# Write the extracted values to a text file (one value per line)
with open(merged_output_txt, "w") as f:
    for value in extracted_values_merged:
        f.write(value + "\n")

print(f"Extracted {len(extracted_values_merged)} opNum values from merged folder. Saved in {merged_output_txt}.")
