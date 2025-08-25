import re

# --- Input txt file list ---
input_files = [
    "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/analyze_pdhd_DATA_v2/statScript/server/MC_new202508/event_wvf_extract/print_new20250819.txt",
    "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/analyze_pdhd_DATA_v2/statScript/server/MC_new202508/event_wvf_extract/print_new20250820.txt"
]

# --- Output files ---
opch_out = "opch.txt"
pdst0_out = "PDSt0.txt"

# --- Regex to extract Target Opch and PDSt0 ---
num_pat = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"
pattern = re.compile(
    rf"^Target\s*Opch:\s*(\d+).*?PDSt0:\s*({num_pat})\s*us",
    flags=re.IGNORECASE
)

# --- Storage ---
opchs = []
pdst0s = []

# --- Process each file ---
for file_path in input_files:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                m = pattern.search(line)
                if m:
                    opchs.append(m.group(1))    # e.g., "24"
                    pdst0s.append(m.group(2))   # e.g., "-256.927"
    except FileNotFoundError:
        print(f"[Warning] File not found: {file_path}")

# --- Write output ---
with open(opch_out, "w", encoding="utf-8") as f:
    f.write("\n".join(opchs))

with open(pdst0_out, "w", encoding="utf-8") as f:
    f.write("\n".join(pdst0s))

print(f"✔️ Done. Extracted {len(opchs)} entries from {len(input_files)} files.")
print(f"→ Saved to {opch_out} and {pdst0_out}")
