// extract_wvf_MULTI.C
// Run directly:  root -l extract_wvf_MULTI.C
//
// This macro reads many ROOT files into a TChain, matches candidate events/tracks,
// extracts waveforms with timing/window/channel constraints, and writes per-event ROOT files
// with safety checks for null pointers, size mismatches, and waveform bounds.

#include <TChain.h>
#include <TFile.h>
#include <TTree.h>
#include <TSystem.h>
#include <TError.h>
#include <TCanvas.h>
#include <TH1D.h>
#include <TString.h>

#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <unordered_map>
#include <algorithm>
#include <cmath>

void extract_wvf_MULTI_20250820(const char* eventFilePath = "eventID_filtered_sorted.txt",
                       const char* trackFilePath = "trackID_filtered_sorted.txt",
                       const char* opchsFilePath = "opchs_filtered_sorted.txt")
{
    gErrorIgnoreLevel = kWarning; // reduce ROOT verbosity

    // ---------------- Configuration ----------------
    const std::string baseDir = "/pnfs/dune/scratch/users/szh2/MC_pdhd_Michel/";
    const std::vector<std::string> partDirs = {
        // "mcTruth_20250809", "mcTruth_20250811",
        "michelt0_20250820"
    };

    const std::string outDir =
        "/exp/dune/data/users/szh2/running_results/MC_PDHD_list/event_wvf_extract/new202508/window_Pdot00_Pdot01/new20250820/extracted_files";

        
    // Timing window (ms), consistent with your filenames (...ms)
    const double dt_min_ms = 0.0;
    const double dt_max_ms = 0.01;

    // Waveform dimensions
    constexpr int kNSamples = 1024;
    constexpr int kMaxWF    = 4000; // cap first dimension of waveform leaf

    // ---------------- Build chain ----------------
    TChain* anatree = new TChain("t0/anatree");
    int files_added = 0;

    for (const auto& part : partDirs) {
        std::string pattern = baseDir + part + "/*.root";
        int n = anatree->Add(pattern.c_str(), -1); // add all
        if (n <= 0) {
            std::cerr << "[WARN] No files matched: " << pattern << "\n";
        } else {
            files_added += n;
            std::cout << "[INFO] Added " << n << " files from " << pattern << "\n";
        }
    }

    if (files_added == 0) {
        std::cerr << "[ERROR] No ROOT files added to chain. Abort.\n";
        return;
    }

    Long64_t nEntries = anatree->GetEntries();
    if (nEntries <= 0) {
        std::cerr << "[ERROR] Chain has no entries. Abort.\n";
        return;
    }
    std::cout << "[INFO] Chain entries: " << nEntries << "\n";

    // ---------------- Read candidate lists ----------------
    std::vector<int> candEvents, candTracks;

    {
        std::ifstream fe(eventFilePath), ft(trackFilePath);
        if (!fe) { std::cerr << "[ERROR] Cannot open " << eventFilePath << "\n"; return; }
        if (!ft) { std::cerr << "[ERROR] Cannot open " << trackFilePath << "\n"; return; }
        int e, t;
        while (fe >> e && ft >> t) {
            candEvents.push_back(e);
            candTracks.push_back(t);
        }
    }

    // Load allowed channels per candidate (one line per candidate; space-separated ints)
    std::vector<std::vector<int>> candOpchs;
    {
        std::ifstream fo(opchsFilePath);
        if (!fo) { std::cerr << "[ERROR] Cannot open " << opchsFilePath << "\n"; return; }
        std::string line;
        while (std::getline(fo, line)) {
            if (line.empty()) { candOpchs.push_back({}); continue; }
            std::istringstream iss(line);
            std::vector<int> chans; int ch;
            while (iss >> ch) chans.push_back(ch);
            candOpchs.push_back(chans);
        }
    }

    // Align sizes
    size_t nCand = std::min({candEvents.size(), candTracks.size(), candOpchs.size()});
    candEvents.resize(nCand);
    candTracks.resize(nCand);
    candOpchs.resize(nCand);

    if (nCand == 0) {
        std::cerr << "[ERROR] No candidate records. Abort.\n";
        return;
    }
    std::cout << "[INFO] Loaded " << nCand << " candidate records.\n";

    // Build a map: event -> list of candidate indices (handles unsorted event order)
    std::unordered_map<int, std::vector<size_t>> evtToIdx;
    evtToIdx.reserve(nCand * 2);
    for (size_t i = 0; i < nCand; ++i) {
        evtToIdx[candEvents[i]].push_back(i);
    }

    // ---------------- Branch setup (selective) ----------------
    anatree->SetBranchStatus("*", 0);
    anatree->SetBranchStatus("run", 1);
    anatree->SetBranchStatus("event", 1);
    anatree->SetBranchStatus("pandorat0", 1);
    anatree->SetBranchStatus("trkid", 1);
    anatree->SetBranchStatus("endx", 1);
    anatree->SetBranchStatus("endy", 1);
    anatree->SetBranchStatus("endz", 1);
    anatree->SetBranchStatus("michelscore", 1);
    anatree->SetBranchStatus("pdchannel", 1);
    anatree->SetBranchStatus("pdt0", 1);
    anatree->SetBranchStatus("nWF", 1);
    anatree->SetBranchStatus("waveform", 1);

    int run = 0;
    int event = 0;
    std::vector<float>* pandorat0   = nullptr;
    std::vector<int>*   trkid       = nullptr;
    std::vector<float>* endx        = nullptr;
    std::vector<float>* endy        = nullptr;
    std::vector<float>* endz        = nullptr;
    std::vector<float>* michelscore = nullptr;
    std::vector<short>* pdchannel   = nullptr;
    std::vector<float>* pdt0        = nullptr;
    int nWF = 0;

    // IMPORTANT: avoid huge stack arrays — keep in static storage
    static float waveform[kMaxWF][kNSamples];

    anatree->SetBranchAddress("run",        &run);
    anatree->SetBranchAddress("event",      &event);
    anatree->SetBranchAddress("pandorat0",  &pandorat0);
    anatree->SetBranchAddress("trkid",      &trkid);
    anatree->SetBranchAddress("endx",       &endx);
    anatree->SetBranchAddress("endy",       &endy);
    anatree->SetBranchAddress("endz",       &endz);
    anatree->SetBranchAddress("michelscore",&michelscore);
    anatree->SetBranchAddress("pdchannel",  &pdchannel);
    anatree->SetBranchAddress("pdt0",       &pdt0);
    anatree->SetBranchAddress("nWF",        &nWF);
    anatree->SetBranchAddress("waveform",    waveform);

    // ---------------- Ensure output dir exists ----------------
    gSystem->mkdir(outDir.c_str(), kTRUE);

    // ---------------- Diagnostic histogram ----------------
    TH1D* hdt = new TH1D("hdt", ";(t_{Pandora}-t_{PDS})ms", 1100, -6, 5);

    // ---------------- Event loop ----------------
    for (Long64_t iEntry = 0; iEntry < nEntries; ++iEntry) {
        if (anatree->GetEntry(iEntry) <= 0) continue;

        // Current file diagnostics
        TTree* curTree = anatree->GetTree();
        TFile* curFile = curTree ? curTree->GetCurrentFile() : nullptr;
        const char* fname = curFile ? curFile->GetName() : "(unknown)";
        std::cout << "\n[Entry " << iEntry << "] file: " << fname << "\n";
        std::cout << "Event label: " << event << "\n";

        // Null checks
        if (!pandorat0 || !trkid || !endx || !endy || !endz ||
            !michelscore || !pdchannel || !pdt0) {
            std::cerr << "[WARN] Null vector branch at entry " << iEntry << ". Skipping.\n";
            continue;
        }

        // Sizes and sanity
        const size_t nPandora = pandorat0->size();
        const size_t nPDS     = pdt0->size();
        const size_t nCh      = pdchannel->size();
        if (nPDS != nCh) {
            std::cerr << "[WARN] pdt0 size (" << nPDS << ") != pdchannel size (" << nCh
                      << ") at entry " << iEntry << ". Using min().\n";
        }
        size_t nPairs = std::min(nPDS, nCh);

        if (nWF < 0) {
            std::cerr << "[WARN] nWF < 0 at entry " << iEntry << ". Skipping.\n";
            continue;
        }
        int nWF_capped = std::min(nWF, kMaxWF);
        if (nWF > kMaxWF) {
            std::cerr << "[WARN] nWF=" << nWF << " > kMaxWF=" << kMaxWF
                      << " at entry " << iEntry << ". Capping.\n";
        }

        // dt histogram (ms)
        for (size_t i = 0; i < nPandora; ++i) {
            if (i >= trkid->size()) break;
            for (size_t j = 0; j < nPairs; ++j) {
                double dt_ms = ( (*pandorat0)[i] - (*pdt0)[j] ) * 1e-3;
                hdt->Fill(dt_ms);
            }
        }

        // Check if this event is among candidates
        auto it = evtToIdx.find(event);
        if (it == evtToIdx.end()) continue;

        const std::vector<size_t>& indices = it->second;
        std::cout << "Event " << event << " is in the candidate list with "
                  << indices.size() << " record(s).\n";

        // For each candidate record for this event
        for (size_t rec : indices) {
            int candTrack = candTracks[rec];
            const std::vector<int>& allowedCh = candOpchs[rec];

            // Loop Pandora rows (guard sizes)
            for (size_t i = 0; i < nPandora; ++i) {
                if (i >= trkid->size() || i >= michelscore->size()
                    || i >= endx->size() || i >= endy->size() || i >= endz->size()) {
                    std::cerr << "[WARN] Pandora vector size mismatch at entry "
                              << iEntry << " (i=" << i << "). Skipping this i.\n";
                    continue;
                }
                if ((*trkid)[i] != candTrack) continue;

                std::cout << "Matching track ID " << (*trkid)[i]
                          << " found for event " << event
                          << " (candidate record " << rec << ")!\n";

                // Prepare output file
                TString outputFileName = Form("%s/mcSingleEvent_run%d_event%d_trackID%d.root",
                                              outDir.c_str(), run, event, (*trkid)[i]);
                TFile out(outputFileName, "RECREATE");
                if (out.IsZombie()) {
                    std::cerr << "[ERROR] Cannot create output file: " << outputFileName << "\n";
                    continue;
                }

                int nwfs = 0;

                // Cross-check info
                std::cout << "======Michel electron candidate!======\n";
                std::cout << "Michel score: " << (*michelscore)[i] << "\n";
                std::cout << "Run: " << run << ",  Event: " << event
                          << ",  TrackID: " << (*trkid)[i] << "\n";
                std::cout << "End(x, y, z) = (" << (*endx)[i] << ", "
                          << (*endy)[i] << ", " << (*endz)[i] << ")\n\n";

                // Loop PDS entries with timing window & channel allowlist
                // Also limit by available waveform rows (nWF_capped)
                size_t nUse = std::min(nPairs, static_cast<size_t>(nWF_capped));

                for (size_t j = 0; j < nUse; ++j) {
                    double dt_ms = ( (*pandorat0)[i] - (*pdt0)[j] ) * 1e-3;
                    if (!(dt_ms > dt_min_ms && dt_ms < dt_max_ms)) continue;

                    int ch = (*pdchannel)[j];
                    if (!allowedCh.empty() &&
                        std::find(allowedCh.begin(), allowedCh.end(), ch) == allowedCh.end()) {
                        continue;
                    }

                    // Format dt string (ms)
                    double abs_dt = std::fabs(dt_ms);
                    TString dtFormatted = Form("%.7f", abs_dt); // "0.xxxxxxx"
                    dtFormatted.Remove(0, 2);                   // remove "0."
                    TString dtString = (dt_ms < 0)
                                     ? Form("dtNdot%sms", dtFormatted.Data())
                                     : Form("dtPdot%sms", dtFormatted.Data());

                    // Create & fill waveform histogram
                    TString hwfName  = Form("%s_ch%d", dtString.Data(), ch);
                    TString hwfTitle = Form("evt:%d,ch:%d,%d,x:%.0f,y:%.0f,z:%.0f",
                                            event, ch, int(j),
                                            (*endx)[i], (*endy)[i], (*endz)[i]);

                    TH1D* hwf = new TH1D(hwfName, hwfTitle, kNSamples, 0, kNSamples);
                    for (int k = 1; k <= kNSamples; ++k) {
                        hwf->SetBinContent(k, waveform[j][k-1]);
                    }
                    std::cout << "Target Opch: " << ch << "; wvf label: " << j
                              << "; PDSt0: " << (*pdt0)[j] << "us; dt: "
                              << (dt_ms * 1e3) << "us\n"; // print in µs for readability
                    hwf->Write();
                    delete hwf;
                    ++nwfs;
                }

                out.Close();
                std::cout << "\nTotal WVFs saved: " << nwfs << "\n";
            } // end loop Pandora rows
        } // end loop candidate records for this event
    } // end event loop

    // ---------------- Save diagnostic histogram ----------------
    TCanvas* cALLdt = new TCanvas("cALLdt", "cALLdt", 1000, 600);
    hdt->Draw();
    cALLdt->Print("dt_1000Files.pdf");

    std::cout << "[INFO] Done.\n";
}
