import re
import argparse

# Input and output file paths
#initial_file = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/analyze_pdhd_DATA_v2/statScript/server/MC_new202510/michelt0_process_original/print_New20251023_initial.txt"
#info_file = "./info_jeremy_stage2.txt"
#output_file = "./updated_New20251023_initial.txt"


# ================================================================
# Allow input and output files to be passed from shell script
# ================================================================
parser = argparse.ArgumentParser(description="Add Michel info script")
parser.add_argument("--input", required=True, help="Path to the initial input file")
parser.add_argument("--output", required=True, help="Path to the output file")
args = parser.parse_args()

# ================================================================
# Define file paths
# ================================================================
initial_file = args.input
info_file = "./info_jeremy_stage2.txt"   # fixed, not passed from .sh
output_file = args.output

print(f"[add_Michel_info] Input file: {initial_file}")
print(f"[add_Michel_info] Info file: {info_file}")
print(f"[add_Michel_info] Output file: {output_file}")
# ================================================================
# (rest of your script continues here)




# --------------------------------------------------------------------
# Build a lookup: (run, event, track_id) -> (pdg, trueE, lifetime)
# Lines look like:
#   Run: 5,  Event: 8778,  TrackID: 21,  PDG: -11,  TrueE[MeV]: 39.44,  lifetime[us]: 2.24
# --------------------------------------------------------------------
lookup = {}

info_re = re.compile(
    r'Run:\s*(\d+),\s*Event:\s*(\d+),\s*TrackID:\s*(\d+),\s*'
    r'PDG:\s*(-?\d+),\s*TrueE\[MeV\]:\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)),\s*'
    r'lifetime\[us\]:\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+))'
)

with open(info_file, 'r') as finfo:
    for line in finfo:
        m = info_re.search(line)
        if m:
            run, event, track_id, pdg, e_mev, life_us = m.groups()
            lookup[(run, event, track_id)] = (pdg, e_mev, life_us)

# --------------------------------------------------------------------
# Process the initial file and add PDG/TrueE/lifetime
# Lines to update look like:
#   Run: 5,  Event: 8778,  TrackID: 21
# We produce:
#   Run: 5,  Event: 8778,  TrackID: 21,  PDG: -11,  TrueE[MeV]: 39.44,  lifetime[us]: 2.24
# --------------------------------------------------------------------
run_evt_trk_re = re.compile(r'Run:\s*(\d+),\s*Event:\s*(\d+),\s*TrackID:\s*(\d+)')

updated_lines = []
with open(initial_file, 'r') as fin:
    for raw in fin:
        line = raw.rstrip('\n')
        m = run_evt_trk_re.search(line)
        if m:
            run, event, track_id = m.groups()
            pdg, e_mev, life_us = lookup.get((run, event, track_id), ("0", "-1", "-1"))
            updated_line = (
                f"Run: {run},  Event: {event},  TrackID: {track_id},  "
                f"PDG: {pdg},  TrueE[MeV]: {e_mev},  lifetime[us]: {life_us}"
            )
            updated_lines.append(updated_line)
        else:
            updated_lines.append(line)

# Write updated content
with open(output_file, 'w') as fout:
    for line in updated_lines:
        fout.write(line + "\n")

print(f"Processing complete. Data saved to {output_file}")
