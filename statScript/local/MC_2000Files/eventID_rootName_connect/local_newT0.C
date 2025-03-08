{
  const char* directory = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/t0_rootFiles/mc/beam_cosmics_onlineExample/initial_t0Files_2k/";

  // Get the list of files using TSystem
  TSystemDirectory dir(directory, directory);
  TList* fileList = dir.GetListOfFiles();
  TIterator *fileIter = fileList->MakeIterator();
  TObject *obj;

  int fileCount = 0;  // Counter for number of ROOT files processed

  while ((obj = fileIter->Next())) {
    TSystemFile *file = (TSystemFile*)obj;
    TString fileName = file->GetName();

    // Only process ROOT files
    if (fileName.EndsWith(".root")) {
      TString fullFilePath = TString(directory) + "/" + fileName;
      TFile *currentFile = TFile::Open(fullFilePath);

      if (!currentFile || currentFile->IsZombie()) {
        std::cerr << "Error opening file: " << fileName << std::endl;
        continue;
      }

      // Access TTree
      TTree *anatree = (TTree*)currentFile->Get("t0/anatree");
      if (!anatree) {
        std::cerr << "Error: Tree 't0/anatree' not found in file: " << fileName << std::endl;
        currentFile->Close();
        continue;
      }

      fileCount++;  

      // Print filename
      std::cout << "\n\n\nProcessing ROOT file:\n" << fileName << std::endl;

      // Set branch addresses
      int run, event;
      vector<int> *trkid = 0;

      anatree->SetBranchAddress("run", &run);
      anatree->SetBranchAddress("event", &event);
      anatree->SetBranchAddress("trkid", &trkid);

      // Loop over events (only printing each event's track IDs once)
      for (int iEntry = 0; iEntry < anatree->GetEntries(); ++iEntry) {
        anatree->GetEntry(iEntry);

        // Print Run, Event, and Track IDs in the requested format
        std::cout << "Run: " << run << " | Event: " << event << " | Track IDs: ";
        for (size_t i = 0; i < trkid->size(); ++i) {
          std::cout << (*trkid)[i] << " ";
        }
        std::cout << std::endl;
      }

      // Close the file after processing
      currentFile->Close();
    }
  }

  // Print the total number of ROOT files processed
  std::cout << "\nTotal number of ROOT files processed: " << fileCount << std::endl;
}
