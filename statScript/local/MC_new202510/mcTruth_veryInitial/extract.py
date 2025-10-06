import re
import glob
import os

# Input directory
input_dir = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/t0_rootFiles/new202510_MC/mcTruth_20251002"

# Output files
out_pdg = "20251002_pdg.txt"
out_kinetic = "20251002_kinetic.txt"
out_lifetime = "20251002_lifetime.txt"
out_x = "20251002_x.txt"
out_y = "20251002_y.txt"
out_z = "20251002_z.txt"
out_muStart = "20251002_muStart.txt"
out_muEnd = "20251002_muEnd.txt"

# Regex: capture Michel + muStart + muEnd in one shot
pattern = re.compile(
    r"Michel \(PDG = ([\-\d]+)\).*?"
    r"Kinetic = ([\d\.]+) MeV, lifetime = ([\d\.Ee\+\-]+) us.*?"
    r"Start \(x,y,z,t\) = \(([\-\d\.Ee\+]+), ([\-\d\.Ee\+]+), ([\-\d\.Ee\+]+),"
    r".*?Mu\(x0,y0,z0,t0\) = \(([\-\d\.Ee\+]+), ([\-\d\.Ee\+]+), ([\-\d\.Ee\+]+),"
    r".*?Mu\(x1,y1,z1,t1\) = \(([\-\d\.Ee\+]+), ([\-\d\.Ee\+]+), ([\-\d\.Ee\+]+),",
    re.DOTALL
)

# Storage
pdgs, kinetics, lifetimes = [], [], []
xs, ys, zs = [], [], []
mu_starts, mu_ends = [], []

# Loop over all txt files
files = sorted(glob.glob(os.path.join(input_dir, "*.txt")))

for fname in files:
    with open(fname, "r") as f:
        text = f.read()

        for m in pattern.finditer(text):
            pdg, kinetic, lifetime = m.group(1), m.group(2), m.group(3)
            x, y, z = m.group(4), m.group(5), m.group(6)
            mu_x0, mu_y0, mu_z0 = m.group(7), m.group(8), m.group(9)
            mu_x1, mu_y1, mu_z1 = m.group(10), m.group(11), m.group(12)

            # Michel
            pdgs.append(pdg)
            kinetics.append(kinetic)
            lifetimes.append(lifetime)
            xs.append(x)
            ys.append(y)
            zs.append(z)

            # Mu start & end (space-separated triples)
            mu_starts.append(f"{mu_x0} {mu_y0} {mu_z0}")
            mu_ends.append(f"{mu_x1} {mu_y1} {mu_z1}")

# Write outputs
with open(out_pdg, "w") as f: f.write("\n".join(pdgs) + "\n")
with open(out_kinetic, "w") as f: f.write("\n".join(kinetics) + "\n")
with open(out_lifetime, "w") as f: f.write("\n".join(lifetimes) + "\n")
with open(out_x, "w") as f: f.write("\n".join(xs) + "\n")
with open(out_y, "w") as f: f.write("\n".join(ys) + "\n")
with open(out_z, "w") as f: f.write("\n".join(zs) + "\n")
with open(out_muStart, "w") as f: f.write("\n".join(mu_starts) + "\n")
with open(out_muEnd, "w") as f: f.write("\n".join(mu_ends) + "\n")

print("Extraction done from", len(files), "files.")
print("Saved outputs:")
print(f" - {out_pdg}")
print(f" - {out_kinetic}")
print(f" - {out_lifetime}")
print(f" - {out_x}")
print(f" - {out_y}")
print(f" - {out_z}")
print(f" - {out_muStart}")
print(f" - {out_muEnd}")
