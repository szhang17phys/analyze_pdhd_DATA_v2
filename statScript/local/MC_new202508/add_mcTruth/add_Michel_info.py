import os
import re

# Input and output file paths
initial_file = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/analyze_pdhd_DATA_v2/statScript/server/MC_new202508/michelt0_process_original/print_New20250809_initial.txt"
info_file = "./info_jeremy_stage2.txt"
output_file = "./updated_New20250809_initial.txt"

# --------------------------------------------------------------------
# Build a lookup: (run, event, track_id) -> (trueE, lifetime)
# Lines look like:
#   Run: 1000,  Event: 5,  TrackID: 2,  TrueE[MeV]: 39.4482,  lifetime[us]: 2.24695
# Ignore header lines like: [5th record] run: 1000 subRun: 0 event: 5
# --------------------------------------------------------------------
energy_life_dict = {}

# Regex for the energy/lifetime lines
energy_line_re = re.compile(
    r'Run:\s*(\d+),\s*Event:\s*(\d+),\s*TrackID:\s*(\d+),\s*'
    r'TrueE\[MeV\]:\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)),\s*'
    r'lifetime\[us\]:\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+))'
)

with open(info_file, 'r') as finfo:
    for line in finfo:
        m = energy_line_re.search(line)
        if m:
            run, event, track_id, e_mev, life_us = m.groups()
            # Store as strings to preserve formatting
            energy_life_dict[(run, event, track_id)] = (e_mev, life_us)

# --------------------------------------------------------------------
# Process the initial file and append TrueE/lifetime where applicable
# Lines to update look like:
#   Run: 1000,  Event: 2,  TrackID: 6
# We produce:
#   Run: 1000,  Event: 2,  TrackID: 6,   TrueE[MeV]: -1,  lifetime[us]: -1
# --------------------------------------------------------------------
run_evt_trk_re = re.compile(r'Run:\s*(\d+),\s*Event:\s*(\d+),\s*TrackID:\s*(\d+)')

updated_lines = []
with open(initial_file, 'r') as fin:
    for raw in fin:
        line = raw.rstrip('\n')
        m = run_evt_trk_re.search(line)
        if m:
            run, event, track_id = m.groups()
            e_mev, life_us = energy_life_dict.get((run, event, track_id), ("-1", "-1"))
            # Reconstruct a clean, appended line
            updated_line = f"Run: {run},  Event: {event},  TrackID: {track_id},   TrueE[MeV]: {e_mev},  lifetime[us]: {life_us}"
            updated_lines.append(updated_line)
        else:
            updated_lines.append(line)

# Write updated content to a new file
with open(output_file, 'w') as fout:
    for line in updated_lines:
        fout.write(line + "\n")

print(f"Processing complete. Data saved to {output_file}")
