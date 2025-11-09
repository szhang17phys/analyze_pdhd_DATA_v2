import re

# Input file
input_file = "./updated_New20251032_initial.txt"

# Output files
decay_x_file = "./extract_initialList/decayX_New20251032_initial.txt"
decay_y_file = "./extract_initialList/decayY_New20251032_initial.txt"
decay_z_file = "./extract_initialList/decayZ_New20251032_initial.txt"  # end point of track
michel_score_file = "./extract_initialList/michelScore_New20251032_initial.txt"
michel_hits_file = "./extract_initialList/michelHits_New20251032_initial.txt"
start_x_file = "./extract_initialList/startX_New20251032_initial.txt"   # start point of track
start_y_file = "./extract_initialList/startY_New20251032_initial.txt"
start_z_file = "./extract_initialList/startZ_New20251032_initial.txt"

eventID_file = "./extract_initialList/eventID_New20251032_initial.txt"
trackID_file = "./extract_initialList/trackID_New20251032_initial.txt"

pdg_file = "./extract_initialList/pdg_New20251032_initial.txt"
energy_file = "./extract_initialList/energy_New20251032_initial.txt"
lifetime_file = "./extract_initialList/lifetime_New20251032_initial.txt"

# Initialize counters
michel_count = 0

# Regex for floats (accepts decimals and scientific notation)
FLOAT = r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?'
MICHEL_RE = re.compile(rf'Michel score:\s*({FLOAT}),\s*Michel hits:\s*(\d+)')

# Robust regex for the summary line with PDG / TrueE / lifetime
SUMMARY_RE = re.compile(
    rf'Run:\s*(\d+),\s*Event:\s*(\d+),\s*TrackID:\s*(\d+),\s*'
    rf'PDG:\s*(-?\d+),\s*TrueE\[MeV\]:\s*({FLOAT}),\s*lifetime\[us\]:\s*({FLOAT})'
)

# Vertex/End matchers (accept floats & scientific notation)
VERTEX_RE = re.compile(rf"Vertex\(x, y, z\)\s*=\s*\(\s*({FLOAT})\s*,\s*({FLOAT})\s*,\s*({FLOAT})\s*\)")
END_RE    = re.compile(rf"End\(x, y, z\)\s*=\s*\(\s*({FLOAT})\s*,\s*({FLOAT})\s*,\s*({FLOAT})\s*\)")

# Open files for writing
with open(decay_x_file, "w") as dx, \
     open(decay_y_file, "w") as dy, \
     open(decay_z_file, "w") as dz, \
     open(michel_score_file, "w") as ms, \
     open(michel_hits_file, "w") as mh, \
     open(start_x_file, "w") as sx, \
     open(start_y_file, "w") as sy, \
     open(start_z_file, "w") as sz, \
     open(eventID_file, "w") as eid, \
     open(trackID_file, "w") as tid, \
     open(pdg_file, "w") as pg, \
     open(energy_file, "w") as Eid, \
     open(lifetime_file, "w") as Lid:

    # Read input file line by line
    with open(input_file, "r") as f:
        for raw in f:
            line = raw.strip()

            # Detect Michel candidate count header
            if line.startswith("======Michel e CAND!"):
                michel_count += 1
                continue

            # Extract Michel score & Michel hits
            m_score = MICHEL_RE.search(line)
            if m_score:
                ms.write(m_score.group(1) + "\n")
                mh.write(m_score.group(2) + "\n")
                continue

            # Extract Run / Event / TrackID / PDG / TrueE / lifetime
            m_sum = SUMMARY_RE.search(line)
            if m_sum:
                event_val = int(m_sum.group(2))
                track_val = int(m_sum.group(3))
                pdg_val   = int(m_sum.group(4))
                trueE_val = float(m_sum.group(5))
                life_val  = float(m_sum.group(6))

                eid.write(f"{event_val}\n")
                tid.write(f"{track_val}\n")
                pg.write(f"{pdg_val}\n")
                Eid.write(f"{trueE_val}\n")
                Lid.write(f"{life_val}\n")
                continue

            # Extract Vertex(x, y, z) values (start vertex of track)
            m_v = VERTEX_RE.search(line)
            if m_v:
                sx.write(m_v.group(1) + "\n")
                sy.write(m_v.group(2) + "\n")
                sz.write(m_v.group(3) + "\n")
                continue

            # Extract End(x, y, z) values (end point of track)
            m_e = END_RE.search(line)
            if m_e:
                dx.write(m_e.group(1) + "\n")
                dy.write(m_e.group(2) + "\n")
                dz.write(m_e.group(3) + "\n")
                continue

# Print counts
print(f"\n=== Total Michel Candidates: {michel_count}")
