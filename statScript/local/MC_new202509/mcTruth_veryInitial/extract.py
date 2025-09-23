import re
import glob
import os

# Input directory
input_dir = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/t0_rootFiles/new202509_MC/mcTruth_20250917"

# Output files (all Michel data combined)
out_pdg = "20250917_pdg.txt"
out_kinetic = "20250917_kinetic.txt"
out_lifetime = "20250917_lifetime.txt"
out_x = "20250917_x.txt"
out_y = "20250917_y.txt"
out_z = "20250917_z.txt"

# Regex pattern to capture values
michel_pattern = re.compile(
    r"Michel \(PDG = ([\-\d]+)\).*?"
    r"Kinetic = ([\d\.]+) MeV, lifetime = ([\d\.Ee\+\-]+) us.*?"
    r"Start \(x,y,z,t\) = \(([\-\d\.Ee\+]+), ([\-\d\.Ee\+]+), ([\-\d\.Ee\+]+),",
    re.DOTALL
)

pdgs, kinetics, lifetimes = [], [], []
xs, ys, zs = [], [], []

# Loop over all txt files in the directory
files = sorted(glob.glob(os.path.join(input_dir, "*.txt")))

for fname in files:
    with open(fname, "r") as f:
        text = f.read()

        for match in michel_pattern.finditer(text):
            pdg = match.group(1)
            kinetic = match.group(2)
            lifetime = match.group(3)
            x, y, z = match.group(4), match.group(5), match.group(6)

            pdgs.append(pdg)
            kinetics.append(kinetic)
            lifetimes.append(lifetime)
            xs.append(x)
            ys.append(y)
            zs.append(z)

# Write all results to the same output files
with open(out_pdg, "w") as f:
    f.write("\n".join(pdgs) + "\n")

with open(out_kinetic, "w") as f:
    f.write("\n".join(kinetics) + "\n")

with open(out_lifetime, "w") as f:
    f.write("\n".join(lifetimes) + "\n")

with open(out_x, "w") as f:
    f.write("\n".join(xs) + "\n")

with open(out_y, "w") as f:
    f.write("\n".join(ys) + "\n")

with open(out_z, "w") as f:
    f.write("\n".join(zs) + "\n")

print("Extraction done from", len(files), "files.")
print("Saved outputs:")
print(f" - {out_pdg}")
print(f" - {out_kinetic}")
print(f" - {out_lifetime}")
print(f" - {out_x}")
print(f" - {out_y}")
print(f" - {out_z}")
