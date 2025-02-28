{
  TChain *anatree = new TChain("t0/anatree");

  //Added by Shu, 20250228---
  //This script should be put at: dunegpvm server
  // '/exp/dune/data/users/szh2/running_results/PDHD_keepupData_list/beamRun_28867/newT0_extract'



  //Shu: Do not forget to modify kMaxWF correspondingly---
//  anatree->Add("/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/analyze_DATA_pdhd/result_server/michelt0_28059_1633.root");
//  anatree->Add("/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/analyze_DATA_pdhd/result_server/michelt0_28867_0351.root");


  //----------------------------------------------
  const char* directory = "/pnfs/dune/scratch/users/szh2/pdhd_DATA_Michel/beamRun_28867/ttt/";

  // Get the list of files using TSystem
  TSystemDirectory dir(directory, directory);
  TList* fileList = dir.GetListOfFiles();

  // Loop over the files in the directory
  TIterator *fileIter = fileList->MakeIterator();
  TObject *obj;
  while ((obj = fileIter->Next())) {
    TSystemFile *file = (TSystemFile*)obj;
    TString fileName = file->GetName();

    // Only add ROOT files to the TChain
    if (fileName.EndsWith(".root")) {
      TString fullFilePath = TString(directory) + "/" + fileName;
      anatree->Add(fullFilePath);  // Add the file to TChain

      // Print just the file name (not the full path)
      std::cout << "Added ROOT file: " << fileName << std::endl;
    }
  }

  //----------------------------------------------


  //Grid points (opch positions) in (y, z) plane
  std::vector<double> yGrid = {578.909, 518.159, 457.409, 396.659, 335.909, 275.159, 214.41, 153.66, 92.9099, 32.16};
  std::vector<double> zGrid = {427.071, 377.921, 316.671, 267.521, 195.011, 145.861, 84.6112, 35.4612};

  //OpCh Map---
  int grid[10][8] = {
    {0, 10, 20, 30, 40, 50, 60, 70},
    {1, 11, 21, 31, 41, 51, 61, 71},
    {2, 12, 22, 32, 42, 52, 62, 72},
    {3, 13, 23, 33, 43, 53, 63, 73},
    {4, 14, 24, 34, 44, 54, 64, 74},
    {5, 15, 25, 35, 45, 55, 65, 75},
    {6, 16, 26, 36, 46, 56, 66, 76},
    {7, 17, 27, 37, 47, 57, 67, 77},
    {8, 18, 28, 38, 48, 58, 68, 78},
    {9, 19, 29, 39, 49, 59, 69, 79}
  };


  int run;
  int event;
  vector<float> *pandorat0=0;
  vector<int> *trkid=0;
  vector<float> *vtxx=0;
  vector<float> *vtxy=0;
  vector<float> *vtxz=0;
  vector<float> *endx=0;
  vector<float> *endy=0;
  vector<float> *endz=0;
  vector<float> *michelscore=0;
  vector<int> *michelhits=0;
  vector<short> *pdchannel=0;
  vector<float> *pdt0=0;
  vector<float> *pd2t0=0;

  int nWF;
  constexpr int kMaxWF =4000;
  int waveform[kMaxWF][1024];

  anatree->SetBranchAddress("run", &run);
  anatree->SetBranchAddress("event", &event);
  anatree->SetBranchAddress("pandorat0", &pandorat0);
  anatree->SetBranchAddress("trkid", &trkid);
  anatree->SetBranchAddress("vtxx", &vtxx);//Shu: Not used...
  anatree->SetBranchAddress("vtxy", &vtxy);
  anatree->SetBranchAddress("vtxz", &vtxz);
  anatree->SetBranchAddress("endx", &endx);
  anatree->SetBranchAddress("endy", &endy);
  anatree->SetBranchAddress("endz", &endz);
  anatree->SetBranchAddress("michelscore", &michelscore);
  anatree->SetBranchAddress("michelhits", &michelhits);
  anatree->SetBranchAddress("pdchannel", &pdchannel);
  anatree->SetBranchAddress("pdt0", &pdt0);
  anatree->SetBranchAddress("nWF", &nWF);
  anatree->SetBranchAddress("waveform", waveform);


  TCanvas *c1 = new TCanvas("c1","c1",1200,1200);
  c1->Divide(4,4);
  c1->Print("michel.ps[");

  TH1D *hwf = new TH1D("hwf","hwf",1024,0,1024);
  
  TH1D *hdt = new TH1D("hdt",";(t_{Pandora}-t_{PDS})ms",1100,-6,5);

  TFile file("waveforms.root", "recreate");

  int nwfs = 0;

  //iEntry: event---
  for(int iEntry = 0; anatree->LoadTree(iEntry) >=0; ++iEntry){

    anatree->GetEntry(iEntry);

    //Shu: Test------
    std::cout<<"\n\n\niEntry (EVENT COUNT)===============================: "<<iEntry<<std::endl;

    //Test---
    std::cout<<"#pdt0 of the event: "<<pdt0->size()<<"\n"<<std::endl;

    for(size_t i = 0; i<pandorat0->size(); ++i){
      //pandorat0: track---
      std::cout<<"\npandorat0 (T0 TRACK COUNT)-------------------: "<<i<<std::endl;

      for (size_t j = 0; j<pdt0->size(); ++j){
        hdt->Fill((*pandorat0)[i]*1e-3 - (*pdt0)[j]*1e-3);
      }

    }



    //Shu: loop over tracks with t0 tagging---
    for(size_t i = 0; i<pandorat0->size(); ++i){

      //Shu: track contains Michel e candidate---
//      if ((*michelscore)[i]>0.1 && (*endx)[i]<-209.0 && (*endx)[i]>-209.1){
      if ((*michelscore)[i]>0.03){

        //Shu:---
        std::cout<<"======Michel e CAND! (score>0.03) COUNT======"<<std::endl;

        cout<<"Michel score: "<<(*michelscore)[i]<<",  Michel hits: "<<(*michelhits)[i]<<endl;
        cout<<"Run: "<<run<<",  Event: "<<event<<",  TrackID: "<<(*trkid)[i]<<endl;
        cout<<"Vertex(x, y, z) = ("<<(*vtxx)[i]<<", "<<(*vtxy)[i]<<", "<<(*vtxz)[i]<<")"<<endl;//starting point!---
        cout<<"End(x, y, z) = ("<<(*endx)[i]<<", "<<(*endy)[i]<<", "<<(*endz)[i]<<")"<<endl;



        //opch finder-------------------------------------------------------
        //Step 1: Find the closest grid point in y---
        int closestYIndex = 0;
        double minYDiff = std::abs((*endy)[i] - yGrid[0]);
        for (size_t k = 1; k < yGrid.size(); ++k) {
          double diff = std::abs((*endy)[i] - yGrid[k]);
          if (diff < minYDiff) {
            minYDiff = diff;
            closestYIndex = k;
          }
        }

        //Step 2: Find the closest grid point in z---
        int closestZIndex = 0;
        double minZDiff = std::abs((*endz)[i] - zGrid[0]);
        for (size_t j = 1; j < zGrid.size(); ++j) {
          double diff = std::abs((*endz)[i] - zGrid[j]);
          if (diff < minZDiff) {
            minZDiff = diff;
            closestZIndex = j;
          }
        }

//        std::cout << "Closest y, z distances: " << minYDiff << ", " << minZDiff << std::endl;

        //Step 3: Compute the corresponding channel number---
        int channel = closestZIndex * 10 + closestYIndex;


        //Step 4: Find nearby opchs---
        int column = channel / 10;  // Tens digit
        int row = channel % 10;  // Units digit
        int startR, startC;
    
        //Determine the top-left-bottom-right corner
        if (column == 0) {
          startC = 0;
        } 
        else if (column == 7) {
          startC = 5;
        } 
        else {
          startC = column - 1;
        }
    
        if (row == 0) {
          startR = 0;
        } 
        else if (row == 9) {
          startR = 7;
        } 
        else {
          startR = row - 1;
        }

        std::vector<int> opchSquare;

        //Generate the 3x3 grid around the starting point
        for (int p = 0; p < 3; ++p) {
          for (int q = 0; q < 3; ++q) {
            int x = startR + p;
            int y = startC + q;
            opchSquare.push_back(grid[x][y]);
          }
        }

        //For negative X (APA2)
        if ((*endx)[i] < 0) {
          for (size_t t = 0; t < opchSquare.size(); ++t) {
            opchSquare[t] += 80;
          }
          channel += 80;
        }

        std::cout<<"\nDistance to APA plane (+/-): "<<(356.346-std::abs((*endx)[i]))<<" cm"<<std::endl;

        std::cout<<"\nClosest OpCh (y, z): ("<<yGrid[closestYIndex]<<", "<<zGrid[closestZIndex]<<"); Label: "<<channel<<std::endl;

        //opch check & output
        for (int p = 0; p < 3; ++p) {
          for (int q = 0; q < 3; ++q) {
            std::cout << opchSquare[p * 3 + q] << " ";
          }
          std::cout << std::endl;
        }
        //--------------------------------------------------------

      }
    }

  }


  c1->Print("michel.ps]");
  file.Close();

  //Keep TPC & PDS time difference---
  TCanvas *c2 = new TCanvas("c2","c2",1000,600);
  hdt->Draw();
  c2->Print("dt.pdf");

  cout<<"\nTotal events saved: "<<nwfs<<endl;



}
