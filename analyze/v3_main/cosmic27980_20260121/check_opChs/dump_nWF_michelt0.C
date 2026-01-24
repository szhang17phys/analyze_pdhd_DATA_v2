// dump_nWF_michelt0.C
// Read nWF (Int_t) from t0/anatree across many ROOT files,
// dump all values into one txt file (one value per line),
// and print number of entries per ROOT file.
//
// Run:
//   root -l -b -q dump_nWF_michelt0.C

#include <TChain.h>
#include <TTree.h>
#include <TFile.h>

#include <fstream>
#include <iostream>
#include <string>
#include <vector>

void dump_nWF_michelt0()
{
    // =========================================
    // User parameters (edit here only)
    // =========================================
    const std::string input_dir =
        "/Volumes/ssd_zhang/thesis_michel/server_processing/t0_rootFiles/cosmicData_new202512/28116/michelT0_files/";

    std::vector<std::string> root_files = {

        "michelt0_decon_run028116_0837_dataflow3_datawriter_0_20240724T155043.root",
        "michelt0_decon_run028116_0838_dataflow0_datawriter_0_20240724T155116.root",
        "michelt0_decon_run028116_0838_dataflow3_datawriter_0_20240724T155116.root",
        "michelt0_decon_run028116_0838_dataflow6_datawriter_0_20240724T155117.root",
        "michelt0_decon_run028116_0839_dataflow0_datawriter_0_20240724T155147.root",
        "michelt0_decon_run028116_0839_dataflow1_datawriter_0_20240724T155147.root",
        "michelt0_decon_run028116_0839_dataflow3_datawriter_0_20240724T155147.root",
        "michelt0_decon_run028116_0839_dataflow6_datawriter_0_20240724T155147.root",
        "michelt0_decon_run028116_0839_dataflow7_datawriter_0_20240724T155147.root",
        "michelt0_decon_run028116_0840_dataflow6_datawriter_0_20240724T155222.root"

    };

    const std::string tree_path = "t0/anatree";
    const std::string out_txt   = "nWF_all.txt";
    // =========================================

    TChain chain(tree_path.c_str());
    int n_added = 0;
    Long64_t total_entries_check = 0;

    std::cout << "=========================================\n";
    std::cout << "[INFO] Per-file entry counts\n";
    std::cout << "=========================================\n";

    for (const auto& f : root_files) {
        const std::string fullpath = input_dir + f;

        // ---- open file explicitly to count entries
        TFile *tf = TFile::Open(fullpath.c_str(), "READ");
        if (!tf || tf->IsZombie()) {
            std::cerr << "[WARN] Cannot open file: " << fullpath << "\n";
            continue;
        }

        TTree *t = nullptr;
        tf->GetObject(tree_path.c_str(), t);
        if (!t) {
            std::cerr << "[WARN] Tree not found in file: " << fullpath << "\n";
            tf->Close();
            continue;
        }

        Long64_t nfile_entries = t->GetEntries();
        total_entries_check += nfile_entries;

        std::cout << "[INFO] File: " << f
                  << "  entries = " << nfile_entries << "\n";

        tf->Close();

        // ---- now add to chain
        int added = chain.Add(fullpath.c_str());
        if (added == 0) {
            std::cerr << "[WARN] Failed to add file to TChain: " << fullpath << "\n";
        } else {
            n_added += added;
        }
    }

    std::cout << "=========================================\n";

    Long64_t nentries = chain.GetEntries();
    std::cout << "[INFO] Files added (TChain.Add sum): " << n_added << "\n";
    std::cout << "[INFO] Total entries in chain     : " << nentries << "\n";
    std::cout << "[INFO] Sum of per-file entries   : " << total_entries_check << "\n";

    if (nentries <= 0) {
        std::cerr << "[ERROR] No entries found. Check tree_path and files.\n";
        return;
    }

    // Speed: only read nWF
    chain.SetBranchStatus("*", 0);
    chain.SetBranchStatus("nWF", 1);

    // nWF is Int_t (confirmed by Print(): nWF/I)
    Int_t nWF = 0;
    chain.SetBranchAddress("nWF", &nWF);

    std::ofstream fout(out_txt);
    if (!fout.is_open()) {
        std::cerr << "[ERROR] Cannot open output file: " << out_txt << "\n";
        return;
    }

    Long64_t n_values_total = 0;

    for (Long64_t i = 0; i < nentries; ++i) {
        chain.GetEntry(i);
        fout << nWF << "\n";
        ++n_values_total;
    }

    fout.close();

    std::cout << "[INFO] Done. Total nWF values written: " << n_values_total << "\n";
    std::cout << "[INFO] Output file: " << out_txt << "\n";
}

// Make it run when executed as a macro file
void __run_dump_nWF_michelt0() { dump_nWF_michelt0(); }
__run_dump_nWF_michelt0();
