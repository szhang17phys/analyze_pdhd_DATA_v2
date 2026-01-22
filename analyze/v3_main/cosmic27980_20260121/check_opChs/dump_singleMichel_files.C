// dump_singleMichel_files.C
// Scan all ROOT files in a directory. For each TH1 histogram found (recursively),
// extract the integer after "ch" in the histogram name (e.g. "_ch58").
// Write ALL extracted channel numbers to one txt file (one per line), preserving repetitions.
//
// Run:
//   root -l -b -q dump_singleMichel_files.C

#include <TFile.h>
#include <TKey.h>
#include <TDirectory.h>
#include <TH1.h>

#include <TSystemDirectory.h>
#include <TSystemFile.h>
#include <TList.h>

#include <fstream>
#include <iostream>
#include <string>
#include <vector>
#include <regex>

// -------------------------
// User parameters
// -------------------------
static const std::string INPUT_DIR =
    "/Volumes/ssd_zhang/thesis_michel/server_processing/t0_rootFiles/cosmicData_new202512/28116/wvf_merged";

static const std::string OUTPUT_TXT = "channels_from_histnames.txt";
// -------------------------


// Recursively scan a directory, and for each histogram, append extracted channel to out_channels
static void ScanDirectoryRecursive(TDirectory* dir, std::vector<int>& out_channels)
{
    if (!dir) return;

    TIter nextkey(dir->GetListOfKeys());
    TKey* key = nullptr;

    // Match "ch" followed by digits, e.g. ch58, ch0067, etc.
    // Extract the LAST occurrence in the name (robust).
    static const std::regex re_ch(R"(ch(\d+))");

    while ((key = (TKey*)nextkey())) {
        TObject* obj = key->ReadObj();
        if (!obj) continue;

        // If it's a subdirectory, recurse
        if (obj->InheritsFrom(TDirectory::Class())) {
            ScanDirectoryRecursive((TDirectory*)obj, out_channels);
            continue;
        }

        // If it's a histogram, parse its name
        if (obj->InheritsFrom(TH1::Class())) {
            const std::string name = obj->GetName();

            int last_ch = -1;
            for (std::sregex_iterator it(name.begin(), name.end(), re_ch), end;
                 it != end; ++it) {
                last_ch = std::stoi((*it)[1].str());
            }

            if (last_ch >= 0) {
                out_channels.push_back(last_ch);  // keep duplicates
            }
        }
    }
}

void dump_singleMichel_files()
{
    // Collect ROOT files in INPUT_DIR
    TSystemDirectory dir("input_dir", INPUT_DIR.c_str());
    TList* files = dir.GetListOfFiles();
    if (!files) {
        std::cerr << "[ERROR] Cannot list directory: " << INPUT_DIR << "\n";
        return;
    }

    std::vector<std::string> root_paths;
    TIter next(files);
    while (TSystemFile* f = (TSystemFile*)next()) {
        std::string fname = f->GetName();
        if (f->IsDirectory()) continue;
        if (fname.size() >= 5 && fname.substr(fname.size() - 5) == ".root") {
            root_paths.push_back(INPUT_DIR + "/" + fname);
        }
    }

    if (root_paths.empty()) {
        std::cerr << "[ERROR] No .root files found in: " << INPUT_DIR << "\n";
        return;
    }

    std::cout << "[INFO] Found " << root_paths.size() << " ROOT files\n";

    std::vector<int> channels;  // includes repetitions

    // Loop over files
    int n_open_ok = 0;
    for (const auto& path : root_paths) {
        TFile* fin = TFile::Open(path.c_str(), "READ");
        if (!fin || fin->IsZombie()) {
            std::cerr << "[WARN] Failed to open: " << path << "\n";
            if (fin) fin->Close();
            continue;
        }
        ++n_open_ok;

        ScanDirectoryRecursive(fin, channels);

        fin->Close();
        delete fin;
    }

    std::cout << "[INFO] Opened OK: " << n_open_ok << " files\n";

    // Write output: one channel per line (duplicates preserved)
    std::ofstream fout(OUTPUT_TXT);
    if (!fout.is_open()) {
        std::cerr << "[ERROR] Cannot open output file: " << OUTPUT_TXT << "\n";
        return;
    }

    for (int ch : channels) {
        fout << ch << "\n";
    }

    fout.close();

    std::cout << "[INFO] Wrote " << channels.size()
              << " channel line(s) to " << OUTPUT_TXT << "\n";
}

// Auto-run when executed as a macro
void __run_dump_singleMichel_files() { dump_singleMichel_files(); }
__run_dump_singleMichel_files();
