#include <TFile.h>
#include <TKey.h>
#include <TClass.h>
#include <TSystemDirectory.h>
#include <TSystemFile.h>

#include <fstream>
#include <iostream>
#include <string>

void dump_singleMichel_nWF()
{
    // ===============================
    // User parameters
    // ===============================
    const std::string input_dir =
        "/Volumes/ssd_zhang/thesis_michel/server_processing/t0_rootFiles/cosmicData_new202512/27980/wvf_merged";





    const std::string output_txt = "TH1D_count_only.txt";

    std::ofstream fout(output_txt);
    if (!fout.is_open()) {
        std::cerr << "ERROR: cannot open output file\n";
        return;
    }

    TSystemDirectory dir("inputDir", input_dir.c_str());
    TList* files = dir.GetListOfFiles();
    if (!files) {
        std::cerr << "ERROR: cannot list files\n";
        return;
    }

    TIter next(files);
    TSystemFile* file;

    while ((file = (TSystemFile*)next())) {
        std::string fname = file->GetName();

        if (file->IsDirectory()) continue;
        if (fname.size() < 5 || fname.substr(fname.size() - 5) != ".root") continue;

        std::string fullpath = input_dir + "/" + fname;
        TFile* f = TFile::Open(fullpath.c_str(), "READ");

        if (!f || f->IsZombie()) {
            std::cerr << "WARNING: cannot open " << fullpath << "\n";
            continue;
        }

        int nTH1D = 0;

        TIter keyIter(f->GetListOfKeys());
        TKey* key;

        while ((key = (TKey*)keyIter())) {
            TClass* cl = gROOT->GetClass(key->GetClassName());
            if (!cl) continue;

            if (cl->InheritsFrom("TH1D")) {
                nTH1D++;
            }
        }

        // only write the number
        fout << nTH1D << "\n";

        f->Close();
        delete f;
    }

    fout.close();

    std::cout << "Done. Saved to " << output_txt << std::endl;
}
