{
  //Commented by Shu (20250321):
  //Pay attention that the variable type of DECON waveform is float, NOT int---



  // Create a TChain and add ROOT files from the directory
  TChain *anatree = new TChain("t0/anatree");



  //---- Read ROOT files from various folders --------------------------------------------
  //==========================================
  std::vector<std::string> partDirs = {"michelt0_20250804"};
  std::string baseDir = "/pnfs/dune/scratch/users/szh2/MC_pdhd_Michel/";
  //==========================================

  for (const auto& part : partDirs) {
    std::string fullDir = baseDir + part;
    TSystemDirectory dir(fullDir.c_str(), fullDir.c_str());
    TList* fileList = dir.GetListOfFiles();
    if (!fileList) {
      std::cerr << "Warning: No files found in directory " << fullDir << std::endl;
      continue;
    }

    TIterator* fileIter = fileList->MakeIterator();
    TObject* obj;
    while ((obj = fileIter->Next())) {
      TSystemFile* file = dynamic_cast<TSystemFile*>(obj);
      if (!file || file->IsDirectory()) continue;

      TString fileName = file->GetName();
      if (fileName.EndsWith(".root")) {
        TString fullFilePath = TString(fullDir.c_str()) + "/" + fileName;
        anatree->Add(fullFilePath);
        std::cout << "Added ROOT file: " << fullFilePath << std::endl;
      }
    }
  }
  //--------------------------------------------------------------------------------------



  // Read cand x, y, z, MS and track IDs from text files
  std::vector<float> candX; 
  std::vector<float> candY; 
  std::vector<float> candZ;   
  std::vector<float> candMS; 
  std::vector<int> candTrack;
  std::ifstream decayXFile("./decayX_filtered_sorted.txt");  
  std::ifstream decayYFile("./decayY_filtered_sorted.txt");  
  std::ifstream decayZFile("./decayZ_filtered_sorted.txt");  
  std::ifstream msFile("./ms_filtered_sorted.txt");
  std::ifstream trackFile("./trackID_filtered_sorted.txt");

  float tmpX; 
  float tmpY; 
  float tmpZ; 
  float tmpMS; 
  int tmpTrack;
  while (decayXFile >> tmpX && decayYFile >> tmpY && decayZFile >> tmpZ && msFile >> tmpMS && trackFile >> tmpTrack) {
    candX.push_back(tmpX);
    candY.push_back(tmpY);
    candZ.push_back(tmpZ);
    candMS.push_back(tmpMS);
    candTrack.push_back(tmpTrack);
  }
  decayXFile.close();
  decayYFile.close();
  decayZFile.close();
  msFile.close();
  trackFile.close();
  std::cout << "\n\nLoaded " << candX.size() << " cand events.\n";


  // Read cand opchs---
  std::vector< std::vector<int> > candOpchs;
  std::ifstream opchsFile("./opchs_filtered_sorted.txt");
  std::string line;
  while (std::getline(opchsFile, line)) {
    if(line.size() == 0) continue; // skip empty lines
    std::istringstream iss(line);
    std::vector<int> chans;
    int ch;
    while(iss >> ch) {
      chans.push_back(ch);
    }
    candOpchs.push_back(chans);
  }
  opchsFile.close();
  std::cout << "Loaded allowed channels for " << candOpchs.size() << " cand records.\n";



  // Set up branches
  int run;
  int event;
  std::vector<float> *pandorat0 = 0;
  std::vector<int> *trkid = 0;
  std::vector<float> *endx = 0;
  std::vector<float> *endy = 0;
  std::vector<float> *endz = 0;
  std::vector<float> *michelscore = 0;
  std::vector<short> *pdchannel = 0;
  std::vector<float> *pdt0 = 0;
  int nWF;
  constexpr int kMaxWF = 4000;
//  int waveform[kMaxWF][1024];
  float waveform[kMaxWF][1024];

  anatree->SetBranchAddress("run", &run);
  anatree->SetBranchAddress("event", &event);
  anatree->SetBranchAddress("pandorat0", &pandorat0);
  anatree->SetBranchAddress("trkid", &trkid);
  anatree->SetBranchAddress("endx", &endx);
  anatree->SetBranchAddress("endy", &endy);
  anatree->SetBranchAddress("endz", &endz);
  anatree->SetBranchAddress("michelscore", &michelscore);
  anatree->SetBranchAddress("pdchannel", &pdchannel);
  anatree->SetBranchAddress("pdt0", &pdt0);
  anatree->SetBranchAddress("nWF", &nWF);
  anatree->SetBranchAddress("waveform", waveform);

  // Create a histogram for overall timing differences (for checking)
  TH1D *hdt = new TH1D("hdt", ";(t_{Pandora}-t_{PDS})ms", 1100, -6, 5);

  // cand pointer for the sorted cand list
  int candID = 0; //cand ID in filtered list
  size_t numcands = candMS.size();
  // (Assuming candMS, candTrack, and candOpchs all have the same number of entries)


  // Loop over EVENTS in the TChain
  for (int iEntry = 0; anatree->LoadTree(iEntry) >= 0; ++iEntry) {
    anatree->GetEntry(iEntry);
    std::cout << "\niEntry=====================================: " << iEntry << std::endl;
    std::cout << "Event label: "<< event << std::endl;

    // Fill overall timing histogram
    for (size_t i = 0; i < pandorat0->size(); ++i) {

      for (size_t j = 0; j < pdt0->size(); ++j) {
        hdt->Fill((*pandorat0)[i]*1e-3 - (*pdt0)[j]*1e-3);
      }
    }



    //loop over Track of the event
    for (size_t i = 0; i < pandorat0->size(); ++i) {
      std::cout<<"pandorat0 i-----------------------: "<<i<<std::endl;
      std::cout<<"Track ID: "<<(*trkid)[i]<<std::endl;

      //Shu: reset candID! 20250305---
      candID = -1;

      for (size_t k = 0; k < numcands; ++k){
        float dx = (*endx)[i] - candX[k];

        if (dx > 1.0f){
          continue;
        }
        if (dx < -1.0f){
          break;
        }

        float dy = (*endy)[i] - candY[k];
        float dz = (*endz)[i] - candZ[k];
        float diff_squared = dx*dx + dy*dy + dz*dz;

        if (diff_squared < 0.1f){//Shu: distance judgement---
          if (std::fabs(candMS[k] - (*michelscore)[i]) < 1e-4f){//Shu: MS judgement---
            if (candTrack[k] == (*trkid)[i]){
              candID = k;
              break;
            }
          }
        }

      }

      if (candID == -1){
        std::cout << "\nNo matching in Candidate List for this track!\n" << std::endl;
        continue;
      }

      //The case that current track is matched with candidate list---
      std::cout << "\nMatching track ID " << (*trkid)[i] << " found for MS " << candMS[candID] << " (EventID: " << event << ")!\n";

      //Allowed opchs---
      std::vector<int> allowedCh = candOpchs[candID];


      // Compute floored end positions and handle negatives
      int endx_val = static_cast<int>(std::floor((*endx)[i]));
      int endy_val = static_cast<int>(std::floor((*endy)[i]));
      int endz_val = static_cast<int>(std::floor((*endz)[i]));

      TString endx_str = Form("endx%s%d", endx_val < 0 ? "N" : "", std::abs(endx_val));
      TString endy_str = Form("endy%s%d", endy_val < 0 ? "N" : "", std::abs(endy_val));
      TString endz_str = Form("endz%s%d", endz_val < 0 ? "N" : "", std::abs(endz_val));

      // Format the Michel score string: 0.872237 → 0_872237
      std::ostringstream oss;
      oss << std::fixed << std::setprecision(6) << (*michelscore)[i];
      std::string score_str = oss.str();
      std::replace(score_str.begin(), score_str.end(), '.', '_');

      //====================================================
      // Output: one root file one event with limited wvfs
      TString outputFileName = Form(
         "/exp/dune/data/users/szh2/running_results/MC_PDHD_list/event_wvf_extract/new202508/window_Pdot00_Pdot01/extracted_files/mcHD_%s_%s_%s_event%d_trackID%d_ms%s.root", endx_str.Data(), endy_str.Data(), endz_str.Data(), event, (*trkid)[i], score_str.c_str());
      //====================================================



      TFile file(outputFileName, "RECREATE");

      int nwfs = 0;  // Counter for waveforms saved

      // Cross-check information
      std::cout << "\n======Michel electron cand!======" << std::endl;
      std::cout << "Michel score: " << (*michelscore)[i] << std::endl;
      std::cout << "Run: " << run << ",  Event: " << event << ",  TrackID: " << (*trkid)[i] << std::endl;
      std::cout << "End(x, y, z) = (" << (*endx)[i] << ", " << (*endy)[i] << ", " << (*endz)[i] << ")\n" << std::endl;

      // Loop over PDS t0 entries for waveform extraction
      for (size_t j = 0; j < pdt0->size(); ++j) {
        float dt = (*pandorat0)[i]*1e-3 - (*pdt0)[j]*1e-3;

        //===============================================
        //Apply timing matching constraint (IMPORTANT!)
        if (dt > 0 && dt < 0.01) {
        //===============================================
          int ch = (*pdchannel)[j];
          // Instead of fixed channels, check if 'ch' is in allowedCh list
          if (std::find(allowedCh.begin(), allowedCh.end(), ch) != allowedCh.end()) {
            // Format dt string
            TString dtString;
            double abs_dt = fabs(dt);
            TString dtFormatted = Form("%.7f", abs_dt);
            dtFormatted.Remove(0, 2);  // Remove leading "0."
            if (dt < 0)
              dtString = Form("dtNdot%sms", dtFormatted.Data());
            else
              dtString = Form("dtPdot%sms", dtFormatted.Data());

            // Create waveform name and histogram
            TString hwfName = Form("%s_ch%d", dtString.Data(), ch);
            TH1D *hwf = new TH1D(hwfName, Form("Waveform dt: %s, Channel: %d", dtString.Data(), ch), 1024, 0, 1024);
            for (int k = 1; k <= 1024; ++k) {
              hwf->SetBinContent(k, waveform[j][k-1]);
            }
            hwf->SetTitle(Form("evt:%d,ch:%d,%d,x:%.0f,y:%.0f,z:%.0f", event, ch, int(j), (*endx)[i], (*endy)[i], (*endz)[i]));
            std::cout << "Target Opch: " << ch << "; wvf label: " << j 
                      << "; PDSt0: " << (*pdt0)[j] << "us; dt: " << dt << "us" << std::endl;
            hwf->Write();
            delete hwf;  // Free memory
            nwfs++;
          }
        } // end timing constraint
      } // end loop over PDS t0

      file.Close();
      std::cout << "\nTotal WVFs saved: " << nwfs << std::endl;

    } // end track loop

  } // end event loop

  // Draw and save the overall timing histogram
  TCanvas *cALLdt = new TCanvas("cALLdt", "cALLdt", 1000, 600);
  hdt->Draw();
  cALLdt->Print("dt_1000Files.pdf");
}
