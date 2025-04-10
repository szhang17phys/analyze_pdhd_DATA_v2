import os
import ROOT

# Input directories
raw_dir = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/analyze_DATA_pdhd/result_server/raw_wvf"
decon_dir = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/analyze_DATA_pdhd/result_server/decon_wvf"
output_file = "opch_extract_5raw_5decon.root"

# Create output file
fout = ROOT.TFile(output_file, "RECREATE")

# Prepare combined histograms
combined_raw = ROOT.TH1D("Raw_combined", "Combined Raw pdchannel; opch; Counts", 140, 0, 140)
combined_raw.SetLineColor(ROOT.kRed)

combined_decon = ROOT.TH1D("Decon_combined", "Combined Decon pdchannel; opch; Counts", 140, 0, 140)
combined_decon.SetLineColor(ROOT.kBlue)

# --- Process RAW files ---
raw_files = sorted([f for f in os.listdir(raw_dir) if f.endswith(".root") and "datawriter" in f])[:5]

for filename in raw_files:
    full_path = os.path.join(raw_dir, filename)
    f = ROOT.TFile.Open(full_path)
    t = f.Get("t0/anatree")

    base = filename.split("_datawriter")[0]
    hist_name = f"Raw_{base}"
    hist_title = f"{hist_name}; opch; Counts"

    h = ROOT.TH1D(hist_name, hist_title, 140, 0, 140)

    for entry in t:
        for val in entry.pdchannel:
            h.Fill(val)
            combined_raw.Fill(val)

    fout.cd()
    h.Write()
    f.Close()

# Write combined raw histogram
fout.cd()
combined_raw.Write()

# --- Process DECON files ---
decon_files = sorted([f for f in os.listdir(decon_dir) if f.endswith(".root") and "Decon" in f])[:5]

for filename in decon_files:
    full_path = os.path.join(decon_dir, filename)
    f = ROOT.TFile.Open(full_path)
    t = f.Get("t0/anatree")

    base = filename.replace("michelt0_Decon_", "").replace(".root", "")
    hist_name = f"Decon_{base}"
    hist_title = f"{hist_name}; opch; Counts"

    h = ROOT.TH1D(hist_name, hist_title, 140, 0, 140)

    for entry in t:
        for val in entry.pdchannel:
            h.Fill(val)
            combined_decon.Fill(val)

    fout.cd()
    h.Write()
    f.Close()

# Write combined decon histogram
fout.cd()
combined_decon.Write()

# --- Draw Raw_combined and Decon_combined together ---
canvas = ROOT.TCanvas("combined_canvas", "Raw vs Decon Combined", 800, 600)
combined_raw.Draw("HIST")
combined_decon.Draw("HIST SAME")

legend = ROOT.TLegend(0.65, 0.75, 0.88, 0.88)
legend.AddEntry(combined_raw, "Raw_combined", "l")
legend.AddEntry(combined_decon, "Decon_combined", "l")
legend.Draw()

canvas.Write()

# --- Print entries ---
print("\nEntries of Raw_combined:")
for i in range(1, combined_raw.GetNbinsX() + 1):
    print(f"Bin {i}: {combined_raw.GetBinContent(i):.0f}")

print("\nEntries of Decon_combined:")
for i in range(1, combined_decon.GetNbinsX() + 1):
    print(f"Bin {i}: {combined_decon.GetBinContent(i):.0f}")

# --- Print differences ---
print("\nBin-by-bin Difference (Raw - Decon):")
for i in range(1, combined_raw.GetNbinsX() + 1):
    raw_val = combined_raw.GetBinContent(i)
    decon_val = combined_decon.GetBinContent(i)
    diff = raw_val - decon_val
    print(f"Bin {i}: {raw_val:.0f} - {decon_val:.0f} = {diff:.0f}")

# Close output file
fout.Close()
print(f"\n✅ All histograms and canvas saved to '{output_file}'")
