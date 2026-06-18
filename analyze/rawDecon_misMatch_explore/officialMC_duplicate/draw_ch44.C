#include <TFile.h>
#include <TKey.h>
#include <TH1.h>
#include <TCanvas.h>
#include <TLegend.h>
#include <TList.h>
#include <iostream>
#include <vector>

void draw_ch44()
{
    TString inputFile =
    "/Volumes/ssd_zhang/thesis_michel/server_processing/t0_rootFiles/"
    "Offical2025_mcProduction/minus5GeV/"
    "wvf_merged_10wvfEvents/"
    "wvfFind_file259781_124_1_20251209T211907Z_event219_trackID14_opNum12_merged.root";

    TFile *fin = TFile::Open(inputFile, "READ");
    if (!fin || fin->IsZombie()) {
        std::cout << "Cannot open input file!" << std::endl;
        return;
    }

    std::vector<TH1*> hists;

    TIter next(fin->GetListOfKeys());
    TKey *key;

    while ((key = (TKey*)next())) {

        TObject *obj = key->ReadObj();

        if (!obj->InheritsFrom("TH1"))
            continue;

        TString hname = obj->GetName();

        if (hname.Contains("_ch44")) {
            hists.push_back((TH1*)obj);
            std::cout << "Found: " << hname << std::endl;
        }
    }

    if (hists.size() != 2) {
        std::cout << "Expected 2 histograms with _ch44, found "
                  << hists.size() << std::endl;
    }

    TCanvas *c1 = new TCanvas("c1", "ch44 comparison", 900, 600);

    hists[0]->SetLineColor(kRed);
    hists[0]->SetLineWidth(2);

    hists[1]->SetLineColor(kBlue);
    hists[1]->SetLineWidth(2);

    hists[0]->Draw("hist");
    hists[1]->Draw("hist same");

    TLegend *leg = new TLegend(0.60, 0.75, 0.90, 0.90);
    leg->AddEntry(hists[0], hists[0]->GetName(), "l");
    leg->AddEntry(hists[1], hists[1]->GetName(), "l");
    leg->Draw();

    c1->SaveAs("ch44_comparison.png");

    TFile fout("ch44_comparison.root", "RECREATE");
    c1->Write();
    fout.Close();

    fin->Close();
}