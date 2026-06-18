import re

matched_file = "/Volumes/ssd_zhang/thesis_michel/server_processing/statScript_local/event_wvf_extract/beam28891/print_part3.log"

initial_file = "/Volumes/ssd_zhang/thesis_michel/server_processing/statScript_local/michelt0_process_initial/beam28891_202602/print_28891new202602_initial.txt"

out_end_file = "end_xyz_part3.txt"
out_t0_file = "pandora_t0_part3.txt"
out_vertex_file = "vertex_xyz_part3.txt"


# ============================================================
# 1. Extract Run/Event/TrackID, End(x,y,z), Pandora_T0
#    from print_part1.log
# ============================================================

matched_records = []

with open(matched_file, "r") as f:
    lines = f.readlines()

for i, line in enumerate(lines):

    if line.startswith("Michel score:"):

        # Fixed structure:
        # Michel score
        # Run/Event/TrackID
        # End(x,y,z)
        # Pandora_T0

        run_line = lines[i + 1].strip()
        end_line = lines[i + 2].strip()
        t0_line  = lines[i + 3].strip()

        run_match = re.search(
            r"Run:\s*(\d+),\s*Event:\s*(\d+),\s*TrackID:\s*(\d+)",
            run_line
        )

        end_match = re.search(
            r"End\(x,\s*y,\s*z\)\s*=\s*\(([^,]+),\s*([^,]+),\s*([^)]+)\)",
            end_line
        )

        t0_match = re.search(
            r"Pandora_T0\[ms\]:\s*([-\d.eE+]+)",
            t0_line
        )

        if run_match and end_match and t0_match:
            run = int(run_match.group(1))
            event = int(run_match.group(2))
            trackID = int(run_match.group(3))

            end_x = float(end_match.group(1))
            end_y = float(end_match.group(2))
            end_z = float(end_match.group(3))

            pandora_t0 = float(t0_match.group(1))

            matched_records.append({
                "run": run,
                "event": event,
                "trackID": trackID,
                "end_x": end_x,
                "end_y": end_y,
                "end_z": end_z,
                "pandora_t0": pandora_t0
            })


print("Matched candidates found:", len(matched_records))


# Save End(x,y,z)
with open(out_end_file, "w") as f:
    f.write("Run Event TrackID EndX EndY EndZ\n")
    for rec in matched_records:
        f.write(
            f"{rec['run']} {rec['event']} {rec['trackID']} "
            f"{rec['end_x']} {rec['end_y']} {rec['end_z']}\n"
        )


# Save Pandora_T0
with open(out_t0_file, "w") as f:
    f.write("Run Event TrackID Pandora_T0_ms\n")
    for rec in matched_records:
        f.write(
            f"{rec['run']} {rec['event']} {rec['trackID']} "
            f"{rec['pandora_t0']}\n"
        )


# ============================================================
# 2. Search initial file and extract matching Vertex(x,y,z)
# ============================================================

target_keys = set(
    (rec["run"], rec["event"], rec["trackID"])
    for rec in matched_records
)

vertex_records = []

with open(initial_file, "r") as f:
    lines = f.readlines()

for i, line in enumerate(lines):

    if line.startswith("Michel score:"):

        run_line = lines[i + 1].strip()
        vertex_line = lines[i + 2].strip()

        run_match = re.search(
            r"Run:\s*(\d+),\s*Event:\s*(\d+),\s*TrackID:\s*(\d+)",
            run_line
        )

        vertex_match = re.search(
            r"Vertex\(x,\s*y,\s*z\)\s*=\s*\(([^,]+),\s*([^,]+),\s*([^)]+)\)",
            vertex_line
        )

        if run_match and vertex_match:
            run = int(run_match.group(1))
            event = int(run_match.group(2))
            trackID = int(run_match.group(3))

            key = (run, event, trackID)

            if key in target_keys:
                vertex_x = float(vertex_match.group(1))
                vertex_y = float(vertex_match.group(2))
                vertex_z = float(vertex_match.group(3))

                vertex_records.append({
                    "run": run,
                    "event": event,
                    "trackID": trackID,
                    "vertex_x": vertex_x,
                    "vertex_y": vertex_y,
                    "vertex_z": vertex_z
                })


print("Matched vertices found:", len(vertex_records))


# Save Vertex(x,y,z)
with open(out_vertex_file, "w") as f:
    f.write("Run Event TrackID VertexX VertexY VertexZ\n")
    for rec in vertex_records:
        f.write(
            f"{rec['run']} {rec['event']} {rec['trackID']} "
            f"{rec['vertex_x']} {rec['vertex_y']} {rec['vertex_z']}\n"
        )