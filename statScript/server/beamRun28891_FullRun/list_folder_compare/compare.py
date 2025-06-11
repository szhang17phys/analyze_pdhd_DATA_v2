import re

# Read all lines from part1.txt
with open("part1.txt", "r") as f1:
    part1_lines = f1.readlines()

# Updated pattern: match _1506_dataflow7_datawriter_
pattern = re.compile(r"(_\d{2,6}_dataflow\d{1,2}_datawriter_)")
part1_keys = set()

for line in part1_lines:
    match = pattern.search(line)
    if match:
        part1_keys.add(match.group(1))

# Read rucio_paths_Full.txt
with open("rucio_paths_Full.txt", "r") as f2:
    list_lines = f2.readlines()

# Find unmatched lines
unmatched_lines = []

for line in list_lines:
    match = pattern.search(line)
    if match:
        if match.group(1) not in part1_keys:
            unmatched_lines.append(line.strip())
    else:
        unmatched_lines.append(line.strip())  # No match at all

# Print results
print("Lines in rucio_paths_Full.txt without correspondence in part1.txt:")
for line in unmatched_lines:
    print(line)
