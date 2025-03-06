{
  TChain *anatree = new TChain("t0/anatree");


  //---- Read ROOT files from folder --------------------------------
  const char* directory = "../../../../t0_rootFiles/data/small_test/initial_t0Files/";
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
  TH1D *hwftot = new TH1D("hwftot","hwftot",1024,0,1024);
  TH1D *hwftot2 = new TH1D("hwftot2","hwftot2",1024,0,1024);
  
  TH1D *hdt = new TH1D("hdt",";(t_{Pandora}-t_{PDS})ms",1100,-6,5);

  TFile file("waveforms.root", "recreate");

  int nwfs = 0;

  //iEntry: event---
  for(int iEntry = 0; anatree->LoadTree(iEntry) >=0; ++iEntry){

    anatree->GetEntry(iEntry);

    //Shu: Test------
    std::cout<<"\niEntry====================: "<<iEntry<<std::endl;

    //Test---
    std::cout<<"#pdt0 of the event: "<<pdt0->size()<<"\n"<<std::endl;

    for(size_t i = 0; i<pandorat0->size(); ++i){
      //pandorat0: track---
      std::cout<<"pandorat0 i----------: "<<i<<std::endl;

      for (size_t j = 0; j<pdt0->size(); ++j){
        hdt->Fill((*pandorat0)[i]*1e-3 - (*pdt0)[j]*1e-3);
      }

    }



    //Shu: loop over tracks with t0 tagging---
    for(size_t i = 0; i<pandorat0->size(); ++i){

      //Shu: track contains Michel e candidate---
      //(score > 0.4 and hits > 5 and 
      //-356 < end_x < 356 and
      //30 < end_y < 580 and
      //30 < end_z < 435):
//      if ((*michelscore)[i]>0.1 ){
      if ((*michelscore)[i]>0.3 && (*michelhits)[i]>5 && (*endx)[i]<356 && (*endx)[i]>-356 && (*endy)[i]<580 && (*endy)[i]>30 && (*endz)[i]<435 && (*endz)[i]>30  ){

        //Shu:---
        std::cout<<"======Michel electron candidate!======"<<std::endl;

        cout<<"Michel score: "<<(*michelscore)[i]<<",  Michel hits: "<<(*michelhits)[i]<<endl;
        cout<<"Run: "<<run<<",  Event: "<<event<<",  TrackID: "<<(*trkid)[i]<<endl;
        cout<<"End(x, y, z) = ("<<(*endx)[i]<<", "<<(*endy)[i]<<", "<<(*endz)[i]<<")"<<endl;


        //Check if close to APA planes------
        if ((*endx)[i] < -156 || (*endx)[i] > 156){
          cout<<"------------Decay close to APA planes!------------"<<endl;
        }
        std::cout<<"Distance to APA: "<<(356.346-std::abs((*endx)[i]))<<" cm\n"<<std::endl;




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

        //Step 3: Compute the corresponding channel number---
        int channel = closestZIndex * 10 + closestYIndex;
//        channel = 60;//Only for test

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

        std::cout<<"Closest OpCh (y, z): ("<<yGrid[closestYIndex]<<","<<zGrid[closestZIndex]<<"); Label: "<<channel<<"\n"<<std::endl;

        //opch check & output
        for (int p = 0; p < 3; ++p) {
          for (int q = 0; q < 3; ++q) {
            std::cout << opchSquare[p * 3 + q] << " ";
          }
          std::cout << std::endl;
        }
        //--------------------------------------------------------





        //Shu: initialize wvfs---
        for(int t = 1; t<=1024; ++t){
          hwftot->SetBinContent(t,0);//Shu: total wvfs---
          hwftot2->SetBinContent(t,0);
        } 

        bool firstwf = true;

        //Shu: For certain track (t0)(i), loop over internal triggers(j)(of certain opch)---
        for(size_t j = 0; j<pdt0->size(); ++j){
          float dt = (*pandorat0)[i]*1e-3 - (*pdt0)[j]*1e-3;

          //Shu: make sure internal and external triggers are close---
          if(dt>-0.15 && dt < 0.05){

            //Shu: choose opch with good TPC & PDS matching---
            int ch = (*pdchannel)[j];

//            std::cout<<"Opch: "<<ch<<"; wvf label: "<<j<<"; PDSt0: "<<(*pdt0)[j]<<"us; dt: "<<dt<<"us"<<std::endl;


            if(ch==opchSquare[0]){
              c1->cd(1);
              for(int k = 1; k<=1024; ++k){
                hwf->SetBinContent(k, waveform[j][k-1]);
                hwftot->SetBinContent(k, hwftot->GetBinContent(k)+waveform[j][k-1]);
              }
              hwf->SetTitle(Form("evt:%d,ch:%d,%d,x:%.0f,y:%.0f,z:%.0f",event,ch,int(j),(*endx)[i],(*endy)[i],(*endz)[i]));
              hwf->DrawCopy();
              std::cout<<"Target Opch: "<<ch<<"; wvf label: "<<j<<"; PDSt0: "<<(*pdt0)[j]<<"us; dt: "<<dt<<"us"<<std::endl;
            }
            if(ch==opchSquare[1]){
              c1->cd(2);
              for(int k = 1; k<=1024; ++k){
                hwf->SetBinContent(k, waveform[j][k-1]);
                hwftot->SetBinContent(k, hwftot->GetBinContent(k)+waveform[j][k-1]);
              }
              hwf->SetTitle(Form("evt:%d,ch:%d,%d,x:%.0f,y:%.0f,z:%.0f",event,ch,int(j),(*endx)[i],(*endy)[i],(*endz)[i]));
              hwf->DrawCopy();
              std::cout<<"Target Opch: "<<ch<<"; wvf label: "<<j<<"; PDSt0: "<<(*pdt0)[j]<<"us; dt: "<<dt<<"us"<<std::endl;
            }
            if(ch==opchSquare[2]){
              c1->cd(3);
              for(int k = 1; k<=1024; ++k){
                hwf->SetBinContent(k, waveform[j][k-1]);

                if (waveform[j][k-1] > 1e6) {
                  std::cout << "Unexpected (opch103): " << waveform[j][k-1] << " at j=" << j << ", (k-1)=" << (k-1) << std::endl;
                }

                hwftot->SetBinContent(k, hwftot->GetBinContent(k)+waveform[j][k-1]);
              }
              hwf->SetTitle(Form("evt:%d,ch:%d,%d,x:%.0f,y:%.0f,z:%.0f",event,ch,int(j),(*endx)[i],(*endy)[i],(*endz)[i]));
              hwf->DrawCopy();
              std::cout<<"Target Opch: "<<ch<<"; wvf label: "<<j<<"; PDSt0: "<<(*pdt0)[j]<<"us; dt: "<<dt<<"us"<<std::endl;
            }


            if(ch==opchSquare[3]){
              c1->cd(5);
              for(int k = 1; k<=1024; ++k){
                hwf->SetBinContent(k, waveform[j][k-1]);

                if (waveform[j][k-1] > 1e6) {
                  std::cout << "Unexpected (opch103): " << waveform[j][k-1] << " at j=" << j << ", (k-1)=" << (k-1) << std::endl;
                }

                hwftot->SetBinContent(k, hwftot->GetBinContent(k)+waveform[j][k-1]);
              }
              hwf->SetTitle(Form("evt:%d,ch:%d,%d,x:%.0f,y:%.0f,z:%.0f",event,ch,int(j),(*endx)[i],(*endy)[i],(*endz)[i]));
              hwf->DrawCopy();
              std::cout<<"Target Opch: "<<ch<<"; wvf label: "<<j<<"; PDSt0: "<<(*pdt0)[j]<<"us; dt: "<<dt<<"us"<<std::endl;
            }
            if(ch==opchSquare[4]){
              c1->cd(6);
              for(int k = 1; k<=1024; ++k){
                hwf->SetBinContent(k, waveform[j][k-1]);
                hwftot->SetBinContent(k, hwftot->GetBinContent(k)+waveform[j][k-1]);
              }
              hwf->SetTitle(Form("evt:%d,ch:%d,%d,x:%.0f,y:%.0f,z:%.0f",event,ch,int(j),(*endx)[i],(*endy)[i],(*endz)[i]));
              hwf->DrawCopy();
              std::cout<<"Target Opch: "<<ch<<"; wvf label: "<<j<<"; PDSt0: "<<(*pdt0)[j]<<"us; dt: "<<dt<<"us"<<std::endl;
            }
            if(ch==opchSquare[5]){
              c1->cd(7);
              for(int k = 1; k<=1024; ++k){
                hwf->SetBinContent(k, waveform[j][k-1]);
                hwftot->SetBinContent(k, hwftot->GetBinContent(k)+waveform[j][k-1]);
              }
              hwf->SetTitle(Form("evt:%d,ch:%d,%d,x:%.0f,y:%.0f,z:%.0f",event,ch,int(j),(*endx)[i],(*endy)[i],(*endz)[i]));
              hwf->DrawCopy();
              std::cout<<"Target Opch: "<<ch<<"; wvf label: "<<j<<"; PDSt0: "<<(*pdt0)[j]<<"us; dt: "<<dt<<"us"<<std::endl;
            }


            if(ch==opchSquare[6]){
              c1->cd(9);
              for(int k = 1; k<=1024; ++k){
                hwf->SetBinContent(k, waveform[j][k-1]);
                hwftot->SetBinContent(k, hwftot->GetBinContent(k)+waveform[j][k-1]);
              }
              hwf->SetTitle(Form("evt:%d,ch:%d,%d,x:%.0f,y:%.0f,z:%.0f",event,ch,int(j),(*endx)[i],(*endy)[i],(*endz)[i]));
              hwf->DrawCopy();
              std::cout<<"Target Opch: "<<ch<<"; wvf label: "<<j<<"; PDSt0: "<<(*pdt0)[j]<<"us; dt: "<<dt<<"us"<<std::endl;
            }
            if(ch==opchSquare[7]){
              c1->cd(10);
              for(int k = 1; k<=1024; ++k){
                hwf->SetBinContent(k, waveform[j][k-1]);
                hwftot->SetBinContent(k, hwftot->GetBinContent(k)+waveform[j][k-1]);
              }
              hwf->SetTitle(Form("evt:%d,ch:%d,%d,x:%.0f,y:%.0f,z:%.0f",event,ch,int(j),(*endx)[i],(*endy)[i],(*endz)[i]));
              hwf->DrawCopy();
              std::cout<<"Target Opch: "<<ch<<"; wvf label: "<<j<<"; PDSt0: "<<(*pdt0)[j]<<"us; dt: "<<dt<<"us"<<std::endl;
            }
            if(ch==opchSquare[8]){
              c1->cd(11);
              for(int k = 1; k<=1024; ++k){
                hwf->SetBinContent(k, waveform[j][k-1]);
                hwftot->SetBinContent(k, hwftot->GetBinContent(k)+waveform[j][k-1]);
              }
              hwf->SetTitle(Form("evt:%d,ch:%d,%d,x:%.0f,y:%.0f,z:%.0f",event,ch,int(j),(*endx)[i],(*endy)[i],(*endz)[i]));
              hwf->DrawCopy();
              std::cout<<"Target Opch: "<<ch<<"; wvf label: "<<j<<"; PDSt0: "<<(*pdt0)[j]<<"us; dt: "<<dt<<"us"<<std::endl;
            }

            //Shu: All opch with small (tpc-pds) timing will be kept---
            hwf->Write(Form("ch%d",ch));

          }

          //Shu: Total wvf---
          c1->cd(13);
          hwftot->DrawCopy();

        }
      }
    }

  }


  c1->Print("michel.ps]");

  hwftot->Write();
  file.Close();

  //Keep TPC & PDS time difference---
  TCanvas *c2 = new TCanvas("c2","c2",1000,600);
  hdt->Draw();
  c2->Print("dt.pdf");

  cout<<"\nTotal events saved: "<<nwfs<<endl;



}
