# Shu: Only keep contents related to Michel electron---
# Mar 3, 2025---

import re
import argparse

# ================================================================
# Function definition (unchanged)
# ================================================================
num_pat = r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?'

def extract_michel_blocks(input_file, output_file):
    michel_block_pattern = re.compile(r'^=+Michel e CAND!')  # start of a block
    score_pattern = re.compile(rf'Michel score:\s*({num_pat})')
    hits_pattern  = re.compile(r'Michel hits:\s*(\d+)')
    end_pattern   = re.compile(
        rf'End\(x, y, z\)\s*=\s*\(\s*({num_pat})\s*,\s*({num_pat})\s*,\s*({num_pat})\s*\)'
    )

    def selection_ok(score, hits, end_x, end_y, end_z):
        return (
            score is not None and hits is not None and
            end_x is not None and end_y is not None and end_z is not None and
            (score > 0.2 and hits > 2 and
             -356 < end_x < 356 and
             30 < end_y < 580 and
             30 < end_z < 435)
        )

    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        current_block = []
        score = hits = end_x = end_y = end_z = None
        keep_block = False

        def maybe_commit():
            if current_block and keep_block:
                outfile.writelines(current_block)
                outfile.write("\n")

        for line in infile:
            if michel_block_pattern.search(line):
                maybe_commit()
                current_block = [line]
                score = hits = end_x = end_y = end_z = None
                keep_block = False
                continue

            current_block.append(line)

            m = score_pattern.search(line)
            if m:
                score = float(m.group(1))

            m = hits_pattern.search(line)
            if m:
                hits = int(m.group(1))

            m = end_pattern.search(line)
            if m:
                end_x, end_y, end_z = map(float, m.groups())

            if not keep_block and selection_ok(score, hits, end_x, end_y, end_z):
                keep_block = True

        maybe_commit()

# ================================================================
# Command-line interface
# ================================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cut Michel electron blocks")
    parser.add_argument("--input", required=True, help="Path to the input text file")
    parser.add_argument("--output", required=True, help="Path to the filtered output text file")
    args = parser.parse_args()

    print(f"[cut.py] Input file : {args.input}")
    print(f"[cut.py] Output file: {args.output}")

    extract_michel_blocks(args.input, args.output)

