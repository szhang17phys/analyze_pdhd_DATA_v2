import re
import os

base_dir = "/Volumes/ssd_zhang/thesis_michel/server_processing/statScript_local/event_wvf_extract/MCminus5GeV"

input_files = [
    "print_part1.log",
    "print_part2.log",
    "print_part3.log"
]

output_all = "PDSt0_all.txt"
output_block_unique = "PDSt0_block_unique.txt"

pdst0_pattern = re.compile(r"PDSt0:\s*([+-]?\d+(?:\.\d+)?)us")
opch_pattern = re.compile(r"Target Opch:\s*(\d+)")

# ============================================================
# Method 1:
# collect every PDSt0 value from all Target Opch lines
# ============================================================
with open(output_all, "w") as fout:

    for filename in input_files:

        input_file = os.path.join(base_dir, filename)
        print(f"Processing all PDSt0 from: {input_file}")

        with open(input_file, "r") as fin:

            for line in fin:
                line_stripped = line.strip()

                if line_stripped.startswith("Target Opch:") and "PDSt0:" in line_stripped:

                    pdst0_match = pdst0_pattern.search(line_stripped)

                    if pdst0_match:
                        pdst0 = pdst0_match.group(1)
                        fout.write(pdst0 + "\n")


# ============================================================
# Method 2:
# within each Michel candidate block,
# if the same Target Opch appears multiple times,
# only count its first PDSt0 value once
# ============================================================
with open(output_block_unique, "w") as fout:

    for filename in input_files:

        input_file = os.path.join(base_dir, filename)
        print(f"Processing block-unique PDSt0 from: {input_file}")

        seen_opch_in_block = set()

        with open(input_file, "r") as fin:

            for line in fin:

                line_stripped = line.strip()

                # A new Michel candidate block starts here
                if "======Michel electron candidate!======" in line_stripped:
                    seen_opch_in_block.clear()
                    continue

                # Only process Target Opch lines with PDSt0
                if line_stripped.startswith("Target Opch:") and "PDSt0:" in line_stripped:

                    opch_match = opch_pattern.search(line_stripped)
                    pdst0_match = pdst0_pattern.search(line_stripped)

                    if opch_match and pdst0_match:

                        opch = opch_match.group(1)
                        pdst0 = pdst0_match.group(1)

                        # If this opch already appeared in this block, skip it
                        if opch in seen_opch_in_block:
                            continue

                        seen_opch_in_block.add(opch)
                        fout.write(pdst0 + "\n")

print("Done.")