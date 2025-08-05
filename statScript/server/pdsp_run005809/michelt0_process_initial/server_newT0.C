{
  TChain *anatree = new TChain("t0/anatree");

  //Added by Shu, 20250228---
  //This script should be put at: dunegpvm server
  // '/exp/dune/data/users/szh2/running_results/PDHD_keepupData_list/beamRun_28867/newT0_extract'



  //Shu: Do not forget to modify kMaxWF correspondingly---
//  anatree->Add("/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/analyze_DATA_pdhd/result_server/michelt0_28059_1633.root");
//  anatree->Add("/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/analyze_DATA_pdhd/result_server/michelt0_28867_0351.root");



  //----------------------------------------------
  const char* directory = "/pnfs/dune/scratch/users/szh2/pdsp_data/run005809/stage1_20250728/";




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




  int nwfs = 0;

  //iEntry: event---
  for(int iEntry = 0; anatree->LoadTree(iEntry) >=0; ++iEntry){

    anatree->GetEntry(iEntry);

    //Shu: Test------
    std::cout<<"\n\n\niEntry (EVENT COUNT)===============================: "<<iEntry<<std::endl;

    //Test---
    std::cout<<"#pdt0 of the event: "<<pdt0->size()<<"\n"<<std::endl;



    //Shu: loop over tracks with t0 tagging---
    for(size_t i = 0; i<pandorat0->size(); ++i){
      std::cout<<"\npandorat0 (T0 TRACK COUNT)-------------------: "<<i<<std::endl;

      //Shu: track contains Michel e candidate---
      if ((*michelscore)[i]>0.001){

        //Shu:---
        std::cout<<"======Michel e CAND! (score>0.001) COUNT (RAW)======"<<std::endl;

        cout<<"Michel score: "<<(*michelscore)[i]<<",  Michel hits: "<<(*michelhits)[i]<<endl;
        cout<<"Run: "<<run<<",  Event: "<<event<<",  TrackID: "<<(*trkid)[i]<<endl;
        cout<<"Vertex(x, y, z) = ("<<(*vtxx)[i]<<", "<<(*vtxy)[i]<<", "<<(*vtxz)[i]<<")"<<endl;//starting point!---
        cout<<"End(x, y, z) = ("<<(*endx)[i]<<", "<<(*endy)[i]<<", "<<(*endz)[i]<<")"<<endl;
        cout<<"Pandora t0: "<<((*pandorat0)[i] * 1e-3)<<"\n\n"<<endl;

      }
    }

  }



  cout<<"\nTotal events saved: "<<nwfs<<endl;



}
