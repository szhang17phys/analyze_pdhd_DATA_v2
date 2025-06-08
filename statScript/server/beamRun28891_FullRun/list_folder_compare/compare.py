import re

# Read all lines from part1.txt
with open("part1.txt", "r") as f1:
    part1_lines = f1.readlines()

# Extract all X_dataflowX segments from part1.txt
pattern = re.compile(r"(\d{3,5}_dataflow\d+)")
part1_keys = set()

for line in part1_lines:
    match = pattern.search(line)
    if match:
        part1_keys.add(match.group(1))

# Check each line in list_part1.txt
with open("list_part1.txt", "r") as f2:
    list_lines = f2.readlines()

# Find lines in list_part1.txt that don't match any key from part1.txt
unmatched_lines = []

for line in list_lines:
    match = pattern.search(line)
    if match:
        if match.group(1) not in part1_keys:
            unmatched_lines.append(line.strip())
    else:
        unmatched_lines.append(line.strip())  # No match at all

# Print or save the unmatched lines
print("Lines in list_part1.txt without correspondence in part1.txt:")
for line in unmatched_lines:
    print(line)
