#include <TFile.h>
#include <TTree.h>
#include <TH1D.h>
#include <TDirectory.h>
#include <vector>
#include <string>
#include <iostream>

void merge_pdchannel_hist() {
    // Input files
    std::vector<std::string> filenames = {
        "/pnfs/dune/scratch/users/szh2/pdhd_DATA_Michel/beamRun_28891_DECON/part1/michelt0_decon_run028891_0800_dataflow3_datawriter_0_20240824T114013.root",
        "/pnfs/dune/scratch/users/szh2/pdhd_DATA_Michel/beamRun_28891_DECON/part1/michelt0_decon_run028891_0683_dataflow5_datawriter_0_20240824T083508.root",
        "/pnfs/dune/scratch/users/szh2/pdhd_DATA_Michel/beamRun_28891_DECON/part1/michelt0_decon_run028891_0674_dataflow0_datawriter_0_20240824T082156.root",
        "/pnfs/dune/scratch/users/szh2/pdhd_DATA_Michel/beamRun_28891_DECON/part1/michelt0_decon_run028891_0670_dataflow4_datawriter_0_20240824T081632.root",
        "/pnfs/dune/scratch/users/szh2/pdhd_DATA_Michel/beamRun_28891_DECON/part1/michelt0_decon_run028891_0664_dataflow4_datawriter_0_20240824T080513.root"
    };

    // Output histogram
    TH1D* h_pdchannel = new TH1D("h_pdchannel", "Merged pdchannel;Channel Number;Counts", 160, 0, 160);

    for (const auto& fname : filenames) {
        std::cout << "Processing file: " << fname << std::endl;

        TFile* f = TFile::Open(fname.c_str(), "READ");
        if (!f || f->IsZombie()) {
            std::cerr << "  [ERROR] Failed to open file: " << fname << std::endl;
            continue;
        }

        TDirectory* dir = (TDirectory*)f->Get("t0");
        if (!dir) {
            std::cerr << "  [ERROR] No 't0' directory in file: " << fname << std::endl;
            f->Close();
            continue;
        }

        TTree* tree = (TTree*)dir->Get("anatree");
        if (!tree) {
            std::cerr << "  [ERROR] No 'anatree' in 't0' directory of file: " << fname << std::endl;
            f->Close();
            continue;
        }

        std::vector<short>* pdchannel = nullptr;
        tree->SetBranchAddress("pdchannel", &pdchannel);

        Long64_t nentries = tree->GetEntries();
        for (Long64_t i = 0; i < nentries; ++i) {
            tree->GetEntry(i);

            for (short ch : *pdchannel) {
                h_pdchannel->Fill(ch);
            }
        }

        f->Close();
    }

    // Save to output file
    TFile* fout = new TFile("pdchannel_hist.root", "RECREATE");
    h_pdchannel->Write();
    fout->Close();

    std::cout << "[DONE] Histogram saved to merged_pdchannel_hist.root\n";
}
