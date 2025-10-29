# Shu: Only keep contents related to Michel electron---
# Mar 3, 2025---

import re

# Accepts 1, 1.2, .3, -0.5, 1e-5, 1.2E+6, etc.
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
        # Per-block fields
        score = None
        hits  = None
        end_x = end_y = end_z = None
        keep_block = False

        def maybe_commit():
            if current_block and keep_block:
                outfile.writelines(current_block)
                outfile.write("\n")

        for line in infile:
            # New block begins
            if michel_block_pattern.search(line):
                # Commit previous block if it passed
                maybe_commit()
                # Reset state for new block
                current_block = [line]
                score = None
                hits  = None
                end_x = end_y = end_z = None
                keep_block = False
                continue

            # Accumulate lines in the current block
            current_block.append(line)

            # Try to extract fields
            m = score_pattern.search(line)
            if m:
                score = float(m.group(1))

            m = hits_pattern.search(line)
            if m:
                hits = int(m.group(1))

            m = end_pattern.search(line)
            if m:
                end_x, end_y, end_z = map(float, m.groups())

            # Evaluate selection whenever we have all fields
            if not keep_block and selection_ok(score, hits, end_x, end_y, end_z):
                keep_block = True

        # Handle the last block
        maybe_commit()

# Usage
extract_michel_blocks(
    "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/analyze_pdhd_DATA_v2/statScript/server/MC_new202510/michelt0_process_original/print_New20251022_initial.txt",
    "./filtered_New20251022_print.txt"
)
