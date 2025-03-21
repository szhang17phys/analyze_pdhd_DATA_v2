{
  TChain *anatree = new TChain("t0/anatree");


  //Shu: Do not forget to modify kMaxWF correspondingly---
  anatree->Add("/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/t0_rootFiles/small_test/run028867_0016_dataflow2_datawriter_0_20240822T193107_michelt0.root");


  int run;
  int event;
  vector<float> *pandorat0=0;
  vector<int> *trkid=0;
  vector<float> *endx=0;
  vector<float> *endy=0;
  vector<float> *endz=0;
  vector<float> *michelscore=0;//to do cross check------
  vector<short> *pdchannel=0;
  vector<float> *pdt0=0;

  int nWF;
  constexpr int kMaxWF =4000;
  int waveform[kMaxWF][1024];

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


  //For ALL events---
  TH1D *hdt = new TH1D("hdt",";(t_{Pandora}-t_{PDS})ms",1100,-6,5);




  //loop over event--------------------------------------------
  for(int iEntry = 0; anatree->LoadTree(iEntry) >=0; ++iEntry){

    anatree->GetEntry(iEntry);

    //Shu: Test------
    std::cout<<"\niEntry=====================================: "<<iEntry<<std::endl;

    //loop over pandorat0, several in one event----------------
    for(size_t i = 0; i<pandorat0->size(); ++i){
      std::cout<<"pandorat0 i-----------------------: "<<i<<std::endl;

      for (size_t j = 0; j<pdt0->size(); ++j){
        hdt->Fill((*pandorat0)[i]*1e-3 - (*pdt0)[j]*1e-3);
      }
    }



    //======select certain event==============================
    if(event == 4042){

      //Shu: loop over different pandora t0s-------
      for(size_t i = 0; i<pandorat0->size(); ++i){

        //======select certain track==========================
        if ((*trkid)[i]==2){

          //Only when event & trkid cuts both satisfied, start plotting---
          TString outputFileName = Form("event%d_trackID%d.root", event, (*trkid)[i]);
          TFile file(outputFileName, "RECREATE");



          TCanvas *c1 = new TCanvas("c1","c1",1200,1200);
          c1->Divide(4,4);
          c1->Print("michel.ps[");
          TH1D *hwf = new TH1D("hwf","hwf",1024,0,1024);
          TH1D *hwftot = new TH1D("hwftot","hwftot",1024,0,1024);
          int nwfs = 0;


          //Cross check (this will appear after ALL pandora t0 of event printed)---
          std::cout<<"======Michel electron candidate!======"<<std::endl;
          cout<<"Michel score: "<<(*michelscore)[i]<<endl;
          cout<<"Run: "<<run<<",  Event: "<<event<<",  TrackID: "<<(*trkid)[i]<<endl;
          cout<<"End(x, y, z) = ("<<(*endx)[i]<<", "<<(*endy)[i]<<", "<<(*endz)[i]<<")\n"<<endl;

          //Shu: initialize wvfs---
          for(int t = 1; t<=1024; ++t){
            hwftot->SetBinContent(t,0);//Shu: total wvfs---
          } 

          bool firstwf = true;


          //loop over pds t0, many for one pandora t0-------------------------
          for(size_t j = 0; j<pdt0->size(); ++j){
            float dt = (*pandorat0)[i]*1e-3 - (*pdt0)[j]*1e-3;

            //timing matching constraint------
            if(dt>-0.12 && dt < 0.02){

              int ch = (*pdchannel)[j];

              if(ch==7){
                c1->cd(1);
                for(int k = 1; k<=1024; ++k){//copy waveform------
                  hwf->SetBinContent(k, waveform[j][k-1]);
                  hwftot->SetBinContent(k, hwftot->GetBinContent(k)+waveform[j][k-1]);
                }
                hwf->SetTitle(Form("evt:%d,ch:%d,%d,x:%.0f,y:%.0f,z:%.0f",event,ch,int(j),(*endx)[i],(*endy)[i],(*endz)[i]));
                hwf->DrawCopy();
                std::cout<<"Target Opch: "<<ch<<"; wvf label: "<<j<<"; PDSt0: "<<(*pdt0)[j]<<"us; dt: "<<dt<<"us"<<std::endl;
                hwf->Write(Form("ch%d",ch));
              }
              if(ch==8){
                c1->cd(2);
                for(int k = 1; k<=1024; ++k){
                  hwf->SetBinContent(k, waveform[j][k-1]);
                  hwftot->SetBinContent(k, hwftot->GetBinContent(k)+waveform[j][k-1]);
                }
                hwf->SetTitle(Form("evt:%d,ch:%d,%d,x:%.0f,y:%.0f,z:%.0f",event,ch,int(j),(*endx)[i],(*endy)[i],(*endz)[i]));
                hwf->DrawCopy();
                std::cout<<"Target Opch: "<<ch<<"; wvf label: "<<j<<"; PDSt0: "<<(*pdt0)[j]<<"us; dt: "<<dt<<"us"<<std::endl;
                hwf->Write(Form("ch%d",ch));
              }
              if(ch==9){
                c1->cd(3);
                for(int k = 1; k<=1024; ++k){
                  hwf->SetBinContent(k, waveform[j][k-1]);
                  hwftot->SetBinContent(k, hwftot->GetBinContent(k)+waveform[j][k-1]);
                }
                hwf->SetTitle(Form("evt:%d,ch:%d,%d,x:%.0f,y:%.0f,z:%.0f",event,ch,int(j),(*endx)[i],(*endy)[i],(*endz)[i]));
                hwf->DrawCopy();
                std::cout<<"Target Opch: "<<ch<<"; wvf label: "<<j<<"; PDSt0: "<<(*pdt0)[j]<<"us; dt: "<<dt<<"us"<<std::endl;
                hwf->Write(Form("ch%d",ch));
              }


              if(ch==17){
                c1->cd(5);
                for(int k = 1; k<=1024; ++k){
                  hwf->SetBinContent(k, waveform[j][k-1]);
                  hwftot->SetBinContent(k, hwftot->GetBinContent(k)+waveform[j][k-1]);
                }
                hwf->SetTitle(Form("evt:%d,ch:%d,%d,x:%.0f,y:%.0f,z:%.0f",event,ch,int(j),(*endx)[i],(*endy)[i],(*endz)[i]));
                hwf->DrawCopy();
                std::cout<<"Target Opch: "<<ch<<"; wvf label: "<<j<<"; PDSt0: "<<(*pdt0)[j]<<"us; dt: "<<dt<<"us"<<std::endl;
                hwf->Write(Form("ch%d",ch));
              }
              if(ch==18){
                c1->cd(6);
                for(int k = 1; k<=1024; ++k){
                  hwf->SetBinContent(k, waveform[j][k-1]);
                  hwftot->SetBinContent(k, hwftot->GetBinContent(k)+waveform[j][k-1]);
                }
                hwf->SetTitle(Form("evt:%d,ch:%d,%d,x:%.0f,y:%.0f,z:%.0f",event,ch,int(j),(*endx)[i],(*endy)[i],(*endz)[i]));
                hwf->DrawCopy();
                std::cout<<"Target Opch: "<<ch<<"; wvf label: "<<j<<"; PDSt0: "<<(*pdt0)[j]<<"us; dt: "<<dt<<"us"<<std::endl;
                hwf->Write(Form("ch%d",ch));
              }
              if(ch==19){
                c1->cd(7);
                for(int k = 1; k<=1024; ++k){
                  hwf->SetBinContent(k, waveform[j][k-1]);
                  hwftot->SetBinContent(k, hwftot->GetBinContent(k)+waveform[j][k-1]);
                }
                hwf->SetTitle(Form("evt:%d,ch:%d,%d,x:%.0f,y:%.0f,z:%.0f",event,ch,int(j),(*endx)[i],(*endy)[i],(*endz)[i]));
                hwf->DrawCopy();
                std::cout<<"Target Opch: "<<ch<<"; wvf label: "<<j<<"; PDSt0: "<<(*pdt0)[j]<<"us; dt: "<<dt<<"us"<<std::endl;
                hwf->Write(Form("ch%d",ch));
              }


              if(ch==27){
                c1->cd(9);
                for(int k = 1; k<=1024; ++k){
                  hwf->SetBinContent(k, waveform[j][k-1]);
                  hwftot->SetBinContent(k, hwftot->GetBinContent(k)+waveform[j][k-1]);
                }
                hwf->SetTitle(Form("evt:%d,ch:%d,%d,x:%.0f,y:%.0f,z:%.0f",event,ch,int(j),(*endx)[i],(*endy)[i],(*endz)[i]));
                hwf->DrawCopy();
                std::cout<<"Target Opch: "<<ch<<"; wvf label: "<<j<<"; PDSt0: "<<(*pdt0)[j]<<"us; dt: "<<dt<<"us"<<std::endl;
                hwf->Write(Form("ch%d",ch));
              }
              if(ch==28){
                c1->cd(10);
                for(int k = 1; k<=1024; ++k){
                  hwf->SetBinContent(k, waveform[j][k-1]);
                  hwftot->SetBinContent(k, hwftot->GetBinContent(k)+waveform[j][k-1]);
                }
                hwf->SetTitle(Form("evt:%d,ch:%d,%d,x:%.0f,y:%.0f,z:%.0f",event,ch,int(j),(*endx)[i],(*endy)[i],(*endz)[i]));
                hwf->DrawCopy();
                std::cout<<"Target Opch: "<<ch<<"; wvf label: "<<j<<"; PDSt0: "<<(*pdt0)[j]<<"us; dt: "<<dt<<"us"<<std::endl;
                hwf->Write(Form("ch%d",ch));
              }
              if(ch==29){
                c1->cd(11);
                for(int k = 1; k<=1024; ++k){
                  hwf->SetBinContent(k, waveform[j][k-1]);
                  hwftot->SetBinContent(k, hwftot->GetBinContent(k)+waveform[j][k-1]);
                }
                hwf->SetTitle(Form("evt:%d,ch:%d,%d,x:%.0f,y:%.0f,z:%.0f",event,ch,int(j),(*endx)[i],(*endy)[i],(*endz)[i]));
                hwf->DrawCopy();
                std::cout<<"Target Opch: "<<ch<<"; wvf label: "<<j<<"; PDSt0: "<<(*pdt0)[j]<<"us; dt: "<<dt<<"us"<<std::endl;
                hwf->Write(Form("ch%d",ch));
              }
              
            }//timing matching constraint------

            //Shu: Total wvf---
            c1->cd(13);
            hwftot->DrawCopy();

          }//loop over pds t0------

          c1->Print("michel.ps]");
          c1->Write();
          hwftot->Write();
          file.Close();
          std::cout<<"\nTotal events saved: "<<nwfs<<std::endl;

        }//select certain track------

      }//loop over pandora t0s-------

    }//select certain event------

  }//loop over event------



  //Keep TPC & PDS time difference---
  TCanvas *cALLdt = new TCanvas("cALLdt","cALLdt",1000,600);
  hdt->Draw();
  cALLdt->Print("dt.pdf");


}
