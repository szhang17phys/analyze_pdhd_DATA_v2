{
  TChain *anatree = new TChain("t0/anatree");


  //===================================================================
  // Shu: Do not forget to modify kMaxWF correspondingly---
  anatree->Add("/pnfs/dune/scratch/users/szh2/MC_pdhd_Michel/michelt0_20251060/*.root");
  anatree->Add("/pnfs/dune/scratch/users/szh2/MC_pdhd_Michel/michelt0_20251061/*.root");
  anatree->Add("/pnfs/dune/scratch/users/szh2/MC_pdhd_Michel/michelt0_20251062/*.root");
  anatree->Add("/pnfs/dune/scratch/users/szh2/MC_pdhd_Michel/michelt0_20251063/*.root");
  anatree->Add("/pnfs/dune/scratch/users/szh2/MC_pdhd_Michel/michelt0_20251064/*.root");
  anatree->Add("/pnfs/dune/scratch/users/szh2/MC_pdhd_Michel/michelt0_20251065/*.root");
  //===================================================================


  int run;
  int event;
  vector<float> *pandorat0 = 0;
  vector<int>   *trkid     = 0;
  vector<float> *pdt0      = 0;

  anatree->SetBranchAddress("run", &run);
  anatree->SetBranchAddress("event", &event);
  anatree->SetBranchAddress("pandorat0", &pandorat0);
  anatree->SetBranchAddress("trkid", &trkid);
  anatree->SetBranchAddress("pdt0", &pdt0);

  // Histogram for time difference
  TH1D *hdt = new TH1D("hdt", ";(t_{Pandora}-t_{PDS})ms", 20000, -10, 10);

  // Histogram for Pandora t0
  TH1D *h_pandorat0 = new TH1D("h_pandorat0", ";Pandora t0 (ms);Counts", 1000, -5, 5); // binning can be adjusted

  // Histogram for PDS t0
  TH1D *h_pdt0 = new TH1D("h_pdt0", ";PDS t0 (ms);Counts", 1000, -5, 5); // binning can be adjusted


  //============================================================
  // Open output ROOT file
  TFile file("TPC_PDS_Matching.root", "RECREATE");
  //============================================================


  // Loop over events
  for (int iEntry = 0; anatree->LoadTree(iEntry) >= 0; ++iEntry) {
    anatree->GetEntry(iEntry);
    std::cout << "\niEntry====================: " << iEntry << std::endl;
    std::cout << "#pdt0 of the event: " << pdt0->size() << "\n" << std::endl;

    // Fill pdt0 histogram
    for (size_t j = 0; j < pdt0->size(); ++j) {
      h_pdt0->Fill((*pdt0)[j] * 1e-3);  // convert to ms
    }

    // Fill pandorat0 histogram and delta t histogram
    for (size_t i = 0; i < pandorat0->size(); ++i) {
      std::cout << "pandorat0 i----------: " << i << std::endl;
      h_pandorat0->Fill((*pandorat0)[i] * 1e-3);  // convert to ms

      for (size_t j = 0; j < pdt0->size(); ++j) {
        hdt->Fill((*pandorat0)[i] * 1e-3 - (*pdt0)[j] * 1e-3);
      }
    }
  }

  // Write the histograms to the ROOT file
  hdt->Write();
  h_pandorat0->Write();
  h_pdt0->Write();

  // Write changes and close the file
  file.Write();
  file.Close();
}
