// dump_opch_michelt0.C
// Read pdchannel (vector<short>) from t0/anatree across many ROOT files,
// dump all values into one txt file (one value per line).
//
// Run:
//   root -l -b -q dump_opch_michelt0.C

#include <TChain.h>
#include <TTree.h>

#include <fstream>
#include <iostream>
#include <string>
#include <vector>

void dump_opch_michelt0()
{
    // =========================================
    // User parameters (edit here only)
    // =========================================
    const std::string input_dir =
        "/Volumes/ssd_zhang/thesis_michel/server_processing/t0_rootFiles/cosmicData_new202512/27980/michelT0_files/";

    std::vector<std::string> root_files = {
        "michelt0_decon_run027980_0402_dataflow3_datawriter_0_20240711T191804.root",
        "michelt0_decon_run027980_0402_dataflow4_datawriter_0_20240711T191804.root",
        "michelt0_decon_run027980_0402_dataflow6_datawriter_0_20240711T191804.root",
        "michelt0_decon_run027980_0403_dataflow0_datawriter_0_20240711T191831.root",
        "michelt0_decon_run027980_0403_dataflow1_datawriter_0_20240711T191831.root",
        "michelt0_decon_run027980_0811_dataflow4_datawriter_0_20240711T223227.root",
        "michelt0_decon_run027980_0811_dataflow6_datawriter_0_20240711T223227.root",
        "michelt0_decon_run027980_1219_dataflow6_datawriter_0_20240712T014630.root",
        "michelt0_decon_run027980_1219_dataflow7_datawriter_0_20240712T014630.root",
        "michelt0_decon_run027980_1220_dataflow2_datawriter_0_20240712T014704.root"
    };

    const std::string tree_path = "t0/anatree";
    const std::string out_txt   = "pdchannel_all.txt";
    // =========================================

    TChain chain(tree_path.c_str());
    int n_added = 0;
    for (const auto& f : root_files) {
        const std::string fullpath = input_dir + f;
        int added = chain.Add(fullpath.c_str());
        if (added == 0) {
            std::cerr << "[WARN] Failed to add file: " << fullpath << "\n";
        } else {
            n_added += added;
        }
    }

    Long64_t nentries = chain.GetEntries();
    std::cout << "[INFO] Files added (TChain.Add sum): " << n_added << "\n";
    std::cout << "[INFO] Total entries in chain: " << nentries << "\n";

    if (nentries <= 0) {
        std::cerr << "[ERROR] No entries found. Check tree_path and files.\n";
        return;
    }

    // Speed: only read pdchannel
    chain.SetBranchStatus("*", 0);
    chain.SetBranchStatus("pdchannel", 1);

    // pdchannel is vector<short>
    std::vector<short>* pdchannel = nullptr;
    chain.SetBranchAddress("pdchannel", &pdchannel);

    std::ofstream fout(out_txt);
    if (!fout.is_open()) {
        std::cerr << "[ERROR] Cannot open output file: " << out_txt << "\n";
        return;
    }

    Long64_t n_values_total = 0;

    for (Long64_t i = 0; i < nentries; ++i) {
        chain.GetEntry(i);

        if (!pdchannel) continue;

        for (size_t k = 0; k < pdchannel->size(); ++k) {
            fout << static_cast<int>((*pdchannel)[k]) << "\n";
            ++n_values_total;
        }
    }

    fout.close();

    std::cout << "[INFO] Done. Total pdchannel values written: " << n_values_total << "\n";
    std::cout << "[INFO] Output file: " << out_txt << "\n";
}

// Make it run when executed as a macro file
void __run_dump_opch_michelt0() { dump_opch_michelt0(); }
__run_dump_opch_michelt0();
