{
  TChain *anatree = new TChain("t0/anatree");

  // Shu: Do not forget to modify kMaxWF correspondingly---
  anatree->Add("/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/analyze_DATA_pdhd/result_server/decon_wvf/*.root");

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

  TH1D *hdt = new TH1D("hdt", ";(t_{Pandora}-t_{PDS})ms", 1100, -6, 5);

  // Open output ROOT file
  TFile file("TPC_PDS_Matching.root", "RECREATE");

  // Loop over events
  for (int iEntry = 0; anatree->LoadTree(iEntry) >= 0; ++iEntry) {
    anatree->GetEntry(iEntry);
    std::cout << "\niEntry====================: " << iEntry << std::endl;
    std::cout << "#pdt0 of the event: " << pdt0->size() << "\n" << std::endl;

    for (size_t i = 0; i < pandorat0->size(); ++i) {
      std::cout << "pandorat0 i----------: " << i << std::endl;
      for (size_t j = 0; j < pdt0->size(); ++j) {
        hdt->Fill((*pandorat0)[i] * 1e-3 - (*pdt0)[j] * 1e-3);
      }
    }
  }

  // Write the histogram to the ROOT file
  hdt->Write();

  // Write changes and close the file
  file.Write();
  file.Close();
}
