import ROOT

# Input file paths
file1_path = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/rawDecon_mismatch_explore/michelt0_Decon_run028867_0378_dataflow5.root"
file2_path = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/rawDecon_mismatch_explore/run028867_0378_dataflow5_datawriter_0_20240823T054434_michelt0.root"
output_path = "opch_extracted.root"

# Open input ROOT files
f1 = ROOT.TFile.Open(file1_path)
f2 = ROOT.TFile.Open(file2_path)

# Access TTrees
t1 = f1.Get("t0/anatree")
t2 = f2.Get("t0/anatree")

# Create output ROOT file
fout = ROOT.TFile(output_path, "RECREATE")

# Prepare TTrees to store pdchannel vectors
tree1 = ROOT.TTree("tree1", "DECON")
tree2 = ROOT.TTree("tree2", "RAW")

pdch1 = ROOT.std.vector('short')()
pdch2 = ROOT.std.vector('short')()
tree1.Branch("pdchannel", pdch1)
tree2.Branch("pdchannel", pdch2)

# Histograms to store flattened pdchannel values
h1 = ROOT.TH1D("h1", "Decon; opch; Counts", 140, 0, 140)
h2 = ROOT.TH1D("h2", "Raw; opch; Counts", 140, 0, 140)
h2.SetLineColor(ROOT.kRed)

# Fill tree1 and h1
for entry in t1:
    pdch1.clear()
    for val in entry.pdchannel:
        pdch1.push_back(val)
        h1.Fill(val)
    tree1.Fill()

# Fill tree2 and h2
for entry in t2:
    pdch2.clear()
    for val in entry.pdchannel:
        pdch2.push_back(val)
        h2.Fill(val)
    tree2.Fill()

# Print entries of h1 (Decon) and h2 (Raw)
print("\nEntries of h1 (Decon):")
for i in range(1, h1.GetNbinsX() + 1):
    print(f"Bin {i}: {h1.GetBinContent(i)}")

print("\nEntries of h2 (Raw):")
for i in range(1, h2.GetNbinsX() + 1):
    print(f"Bin {i}: {h2.GetBinContent(i)}")

# Calculate the bin entry difference (h2 - h1)
diff = [h2.GetBinContent(i) - h1.GetBinContent(i) for i in range(1, h1.GetNbinsX() + 1)]

# Create histogram for the difference
h_diff = ROOT.TH1D("h_diff", "Difference (Raw - Decon); opch; Difference", 140, 0, 140)

# Fill h_diff with the calculated difference
for i, val in enumerate(diff, start=1):
    h_diff.SetBinContent(i, val)

# Draw both histograms on a canvas
canvas = ROOT.TCanvas("c1", "pdchannel Comparison", 800, 600)
h1.Draw("HIST")
h2.Draw("HIST SAME")

legend = ROOT.TLegend(0.6, 0.7, 0.85, 0.85)
legend.AddEntry(h1, "Decon", "l")
legend.AddEntry(h2, "Raw", "l")
legend.Draw()

# Draw difference (h2 - h1) on a new canvas
raw_minus_decon_canvas = ROOT.TCanvas("rawMinusDecon", "Difference (Raw - Decon)", 800, 600)

# Check if difference contains negative values
has_negative_values = any(val < 0 for val in diff)

if has_negative_values:
    # If there are negative values, draw as scatter plot
    for i, val in enumerate(diff, start=1):
        h_diff.Fill(i, val)  # Fill histogram with difference values

    h_diff.Draw("PE")  # "PE" stands for Points and Errors
else:
    h_diff.Draw("HIST")

# Print entries of the difference (h2 - h1) in the requested format
print("\nEntries of the difference (h2 - h1):")
for i in range(1, h_diff.GetNbinsX() + 1):
    raw_val = h2.GetBinContent(i)
    decon_val = h1.GetBinContent(i)
    difference = raw_val - decon_val
    print(f"Bin {i}: {raw_val:.0f} - {decon_val:.0f} = {difference:.0f}")

# Write everything to the output file
fout.cd()
tree1.Write()
tree2.Write()
h1.Write()
h2.Write()
h_diff.Write()  # Write the difference histogram
canvas.Write()  # Save canvas into ROOT file
raw_minus_decon_canvas.Write()  # Save the difference canvas into ROOT file

# Close files
fout.Close()
f1.Close()
f2.Close()
