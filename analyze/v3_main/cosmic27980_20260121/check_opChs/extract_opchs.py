#!/usr/bin/env python3
import re

# ===============================
# User parameters (edit here)
# ===============================
INPUT_TXT  = "/Volumes/ssd_zhang/thesis_michel/server_processing/statScript_local/applyCut_print/cosmic27980/filtered_cosmic27980_print.txt"
OUTPUT_TXT = "./opchs_filtered.txt"
# ===============================


def extract_opch_blocks():
    closest_re = re.compile(r"^\s*Closest\s+OpCh\b")
    int_re = re.compile(r"[-+]?\d+")

    with open(INPUT_TXT, "r", encoding="utf-8", errors="replace") as fin:
        lines = fin.readlines()

    output_lines = []
    n_blocks = 0
    i = 0
    n = len(lines)

    while i < n:
        if closest_re.search(lines[i]):
            # Expect next 3 lines to contain the 3×3 OpCh grid
            if i + 3 >= n:
                break

            values = []
            for j in range(1, 4):
                nums = [int(x) for x in int_re.findall(lines[i + j])]
                if len(nums) >= 3:
                    values.extend(nums[:3])

            if len(values) == 9:
                output_lines.extend(f"{v}\n" for v in values)
                n_blocks += 1

            i += 4
        else:
            i += 1

    with open(OUTPUT_TXT, "w", encoding="utf-8") as fout:
        fout.writelines(output_lines)

    print(f"[INFO] Extracted {n_blocks} Closest OpCh blocks")
    print(f"[INFO] Output written to: {OUTPUT_TXT}")


if __name__ == "__main__":
    extract_opch_blocks()
