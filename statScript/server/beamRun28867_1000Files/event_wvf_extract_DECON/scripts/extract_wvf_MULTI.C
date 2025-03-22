{
  //Commented by Shu (20250321):
  //Pay attention that the variable type of DECON waveform is float, NOT int---


  // Create a TChain and add ROOT files from the directory
  TChain *anatree = new TChain("t0/anatree");

  //---- Read ROOT files from folder --------------------------------
  const char* directory = "/pnfs/dune/scratch/users/szh2/pdhd_DATA_Michel/beamRun_28867_DECON/michelt0_1k/";
  TSystemDirectory dir(directory, directory);
  TList* fileList = dir.GetListOfFiles();
  TIterator *fileIter = fileList->MakeIterator();
  TObject *obj;
  while ((obj = fileIter->Next())) {
    TSystemFile *file = (TSystemFile*)obj;
    TString fileName = file->GetName();

    // Only add ROOT files to the TChain
    if (fileName.EndsWith(".root")) {
      TString fullFilePath = TString(directory) + "/" + fileName;
      anatree->Add(fullFilePath);
      std::cout << "Added ROOT file: " << fileName << std::endl;
    }
  }
  //------------------------------------------------------------------

  // Read candidate event and track IDs from text files
  std::vector<int> candidateEvents;
  std::vector<int> candidateTracks;
  std::ifstream eventFile("./eventID_filtered_sorted.txt");
  std::ifstream trackFile("./trackID_filtered_sorted.txt");

  int tempEvent, tempTrack;
  while (eventFile >> tempEvent && trackFile >> tempTrack) {
    candidateEvents.push_back(tempEvent);
    candidateTracks.push_back(tempTrack);
  }
  eventFile.close();
  trackFile.close();
  std::cout << "\n\nLoaded " << candidateEvents.size() << " candidate events.\n";

  // Read candidate allowed channels from opchs_filtered_sorted.txt.
  // Each line should contain the allowed channels (space-separated) for the corresponding candidate record.
  std::vector< std::vector<int> > candidateOpchs;
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
    candidateOpchs.push_back(chans);
  }
  opchsFile.close();
  std::cout << "Loaded allowed channels for " << candidateOpchs.size() << " candidate records.\n";

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

  // Candidate pointer for the sorted candidate list
  size_t candIdx = 0;
  size_t numCandidates = candidateEvents.size();
  // (Assuming candidateEvents, candidateTracks, and candidateOpchs all have the same number of entries)

  // Loop over events in the TChain
  for (int iEntry = 0; anatree->LoadTree(iEntry) >= 0; ++iEntry) {
    anatree->GetEntry(iEntry);
    std::cout << "\niEntry=====================================: " << iEntry << std::endl;
    std::cout << "Event label: "<< event << std::endl;

    // Fill overall timing histogram
    for (size_t i = 0; i < pandorat0->size(); ++i) {
      std::cout<<"pandorat0 i-----------------------: "<<i<<std::endl;
      std::cout<<"Track ID: "<<(*trkid)[i]<<std::endl;

      for (size_t j = 0; j < pdt0->size(); ++j) {
        hdt->Fill((*pandorat0)[i]*1e-3 - (*pdt0)[j]*1e-3);
      }
    }

    // Advance candidate pointer until candidateEvents[candIdx] >= current event
    while (candIdx < numCandidates && candidateEvents[candIdx] < event) {
      candIdx++;
    }

    // If the current event matches one or more candidate events
    if (candIdx < numCandidates && candidateEvents[candIdx] == event) {
      // Collect indices for all candidate records corresponding to the current event.
      std::vector<size_t> candidateIndicesForEvent;
      size_t tempIdx = candIdx;
      while (tempIdx < numCandidates && candidateEvents[tempIdx] == event) {
        candidateIndicesForEvent.push_back(tempIdx);
        tempIdx++;
      }
      std::cout << "\nEvent " << event << " is in the candidate list with " 
                << candidateIndicesForEvent.size() << " record(s).\n";

      // Process each candidate record for the current event individually
      for (size_t ci = 0; ci < candidateIndicesForEvent.size(); ci++) {
        size_t candRecord = candidateIndicesForEvent[ci];
        int candTrack = candidateTracks[candRecord];
        std::vector<int> allowedCh = candidateOpchs[candRecord];

        // Loop over Pandora t0 entries for this event
        for (size_t i = 0; i < pandorat0->size(); ++i) {
          if ((*trkid)[i] == candTrack) {
            std::cout << "Matching track ID " << (*trkid)[i] << " found for event " << event << " (candidate record " << candRecord << ")!\n";

            // Define output file name and open a new ROOT file to save the waveforms
            TString outputFileName = Form("/exp/dune/data/users/szh2/running_results/PDHD_keepupData_list/beamRun_28867/event_wvf_extract_DECON/extracted_files/extractDecon_event%d_trackID%d.root", event, (*trkid)[i]);
            TFile file(outputFileName, "RECREATE");

            int nwfs = 0;  // Counter for waveforms saved

            // Cross-check information
            std::cout << "======Michel electron candidate!======" << std::endl;
            std::cout << "Michel score: " << (*michelscore)[i] << std::endl;
            std::cout << "Run: " << run << ",  Event: " << event << ",  TrackID: " << (*trkid)[i] << std::endl;
            std::cout << "End(x, y, z) = (" << (*endx)[i] << ", " << (*endy)[i] << ", " << (*endz)[i] << ")\n" << std::endl;

            // Loop over PDS t0 entries for waveform extraction
            for (size_t j = 0; j < pdt0->size(); ++j) {
              float dt = (*pandorat0)[i]*1e-3 - (*pdt0)[j]*1e-3;


              //Apply timing matching constraint (IMPORTANT!)----------------------------------
              if (dt > -0.15 && dt < 0.05) {
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
                  hwf->SetTitle(Form("evt:%d,ch:%d,%d,x:%.0f,y:%.0f,z:%.0f", event, ch, int(j),
                                       (*endx)[i], (*endy)[i], (*endz)[i]));
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
          } // end check for matching candidate track
        } // end loop over pandora t0 entries
      } // end loop over candidate records for event

      candIdx = 0;//Sometimes one event has >1 trckIDs for Michel
    } // end candidate event check

    //Shu: reset candIdx! 20250305---
    candIdx = 0;
  } // end event loop

  // Draw and save the overall timing histogram
  TCanvas *cALLdt = new TCanvas("cALLdt", "cALLdt", 1000, 600);
  hdt->Draw();
  cALLdt->Print("dt_1000Files.pdf");
}
