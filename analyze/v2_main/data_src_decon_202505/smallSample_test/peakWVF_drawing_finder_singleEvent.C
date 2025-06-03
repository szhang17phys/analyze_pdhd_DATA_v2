#include <iostream>
#include <vector>
#include <string>
#include <map>
#include <algorithm>
#include <cmath>
#include "TFile.h"
#include "TH1D.h"
#include "TGraph.h"
#include "TCanvas.h"
#include "TStyle.h"
#include "TSystem.h"



//(Added on 20250528) Current bin merging strategy:----------------
// Phase 1:
// Strong seeds (count ≥ 2) absorb nearby > 0 bins within ±2
// Seed is always the representative

// Phase 2:
// Remaining count = 1 bins grouped if:
// Adjacent bins ≤ 2 apart
// Span ≤ 4

// mergedBins guarantees no double-counting



struct Peak {
    int binIndex;
    double leftHeight;
    double rightHeight;
};

std::vector<Peak> findPeaks(TH1D* hist, double heightThreshold) {
    std::vector<Peak> peaks;
    int numBins = hist->GetNbinsX();
    
    for (int i = 2; i < numBins; ++i) { // Avoid edges
        double centerVal = hist->GetBinContent(i);
        double leftVal = hist->GetBinContent(i - 1);
        double rightVal = hist->GetBinContent(i + 1);
        
        if (centerVal > leftVal && centerVal > rightVal) { // Local maximum
            int leftIndex = i - 1;
            while (leftIndex > 1 && hist->GetBinContent(leftIndex - 1) < hist->GetBinContent(leftIndex)) {
                leftIndex--;
            }
            
            int rightIndex = i + 1;
            while (rightIndex < numBins && hist->GetBinContent(rightIndex + 1) < hist->GetBinContent(rightIndex)) {
                rightIndex++;
            }
            
            double leftHeight = centerVal - hist->GetBinContent(leftIndex);
            double rightHeight = centerVal - hist->GetBinContent(rightIndex);
            
            if (leftHeight > heightThreshold && rightHeight > heightThreshold) {
                peaks.push_back({i, leftHeight, rightHeight});
            }
        }
    }
    return peaks;
}

std::string getOutputFileName(const std::string& inputFileName) {
    size_t lastSlash = inputFileName.find_last_of("/");
    std::string baseName = (lastSlash == std::string::npos) ? inputFileName : inputFileName.substr(lastSlash + 1);
    return "./singleTest_results/peakFind_" + baseName;
}

void processAllHistograms(const char* inputFileName, double heightThreshold) {
    std::string outputFileName = getOutputFileName(inputFileName);
    gSystem->mkdir("./singleTest_results", kTRUE); // Ensure the output directory exists
    
    TFile* inputFile = TFile::Open(inputFileName, "READ");
    if (!inputFile || inputFile->IsZombie()) {
        std::cerr << "Error: Could not open input file!" << std::endl;
        return;
    }
    
    TFile* outputFile = new TFile(outputFileName.c_str(), "RECREATE");
    TIter nextKey(inputFile->GetListOfKeys());
    TObject* obj;
    TCanvas canvas("batch_canvas", "Canvas for Saving", 800, 600);
    
    TH1D* peakStatistics = new TH1D("peak_statistics", "Peak Locations Distribution", 1024, 0, 1024);
    // Vector to collect peak positions from histograms containing "ch"
    std::vector<double> allPeakPositions2;
    


    while ((obj = nextKey())) {
        std::string histName = obj->GetName();
        TH1D* hist = (TH1D*)inputFile->Get(histName.c_str());
        if (!hist || !hist->InheritsFrom("TH1D")) continue;

        hist->SetName(histName.c_str()); // Ensure the name remains correct

        // Use fixed threshold for "total", otherwise use default--------------------------
        double thresholdToUse = (histName == "total") ? 0.5 : heightThreshold;

        std::vector<Peak> peaks = findPeaks(hist, thresholdToUse);
        std::cout << "\nDetected " << peaks.size() << " peaks in " << histName << ":" << std::endl;

        std::vector<double> peakX, peakY;
        for (const auto& peak : peaks) {
            std::cout << "Peak at bin " << peak.binIndex 
                      << ", Left Height: " << peak.leftHeight 
                      << ", Right Height: " << peak.rightHeight << std::endl;
            double peakPos = hist->GetBinCenter(peak.binIndex);
            peakX.push_back(peakPos);
            peakY.push_back(hist->GetBinContent(peak.binIndex));

            // For histograms whose name contains "ch", fill the peak_statistics histogram
            // and collect values for merged statistics.
            if (histName.find("ch") != std::string::npos) {
                peakStatistics->Fill(peakPos);
                allPeakPositions2.push_back(peakPos);
            }
        }

        hist->Write();

        canvas.cd();
        hist->SetLineColor(kBlue);
        hist->Draw();

        TGraph* peakMarkers = new TGraph(peakX.size(), &peakX[0], &peakY[0]);
        peakMarkers->SetMarkerStyle(20);
        peakMarkers->SetMarkerSize(1.2);
        peakMarkers->SetMarkerColor(kRed);
        peakMarkers->Draw("P SAME");

        canvas.Write(Form("%s_peakFinded", histName.c_str()));
    }



    
    // // Process the "hwftot" histogram if present
    // if (inputFile->Get("hwftot")) {
    //     TH1D* hwftotHist = (TH1D*)inputFile->Get("hwftot");
    //     std::vector<Peak> hwftotPeaks = findPeaks(hwftotHist, 0.5); // threshold as 0.5
    //     std::cout << "\n\n------Detected " << hwftotPeaks.size() << " peaks in 'total':------" << std::endl;
        
    //     std::vector<double> hwftotPeakX, hwftotPeakY;
    //     for (const auto& peak : hwftotPeaks) {
    //         std::cout << "Peak at bin " << peak.binIndex 
    //                   << ", Left Height: " << peak.leftHeight 
    //                   << ", Right Height: " << peak.rightHeight << std::endl;
    //         hwftotPeakX.push_back(hwftotHist->GetBinCenter(peak.binIndex));
    //         hwftotPeakY.push_back(hwftotHist->GetBinContent(peak.binIndex));
    //     }
        
    //     TCanvas hwftotCanvas("hwftot_peakCanvas", "hwftot Peak Finding", 800, 600);
    //     hwftotHist->SetLineColor(kBlue);
    //     hwftotHist->Draw();
        
    //     TGraph* hwftotPeakMarkers = new TGraph(hwftotPeakX.size(), &hwftotPeakX[0], &hwftotPeakY[0]);
    //     hwftotPeakMarkers->SetMarkerStyle(20);
    //     hwftotPeakMarkers->SetMarkerSize(1.2);
    //     hwftotPeakMarkers->SetMarkerColor(kRed);
    //     hwftotPeakMarkers->Draw("P SAME");
        
    //     hwftotCanvas.Write();
    // }
    


    //Bin merging (require SPAN of group <=4)---------20250528--------------------------
    if (!allPeakPositions2.empty()) {
        // Step 1: Round all peaks and count frequency by bin index
        std::map<int, int> binCounts;
        for (double val : allPeakPositions2) {
            int bin = static_cast<int>(std::round(val));
            binCounts[bin]++;
        }

        std::unordered_set<int> mergedBins;
        std::vector<std::pair<int, int>> mergedResults;

        // ===== Phase 1: Use count ≥ 2 as seeds; merge non-zero bins within ±2 =====
        for (const auto &p : binCounts) {
            int bin = p.first;
            int count = p.second;

            if (count < 2 || mergedBins.count(bin)) continue;

            int groupSum = count;
            mergedBins.insert(bin);

            for (int offset = -2; offset <= 2; ++offset) {
                if (offset == 0) continue;
                int neighborBin = bin + offset;
                if (binCounts.count(neighborBin) && binCounts[neighborBin] > 0 && !mergedBins.count(neighborBin)) {
                    groupSum += binCounts[neighborBin];
                    mergedBins.insert(neighborBin);
                }
            }

            mergedResults.push_back({bin, groupSum});
        }

        // ===== Phase 2: Group remaining bins with count = 1 (adjacent ≤2, span ≤4) =====
        std::vector<int> remainingOnes;
        for (const auto &p : binCounts) {
            if (p.second == 1 && !mergedBins.count(p.first)) {
                remainingOnes.push_back(p.first);
            }
        }

        std::sort(remainingOnes.begin(), remainingOnes.end());
        std::vector<int> currentGroup;

        for (size_t i = 0; i < remainingOnes.size(); ++i) {
            int curr = remainingOnes[i];
            if (currentGroup.empty()) {
                currentGroup.push_back(curr);
            } else {
                int last = currentGroup.back();
                int first = currentGroup.front();
                if ((curr - last <= 2) && (curr - first <= 4)) {
                    currentGroup.push_back(curr);
                } else {
                    if (currentGroup.size() > 1) {
                        int repBin = currentGroup[currentGroup.size() / 2];
                        mergedResults.push_back({repBin, static_cast<int>(currentGroup.size())});
                        for (int b : currentGroup) {
                            mergedBins.insert(b);
                        }
                    }
                    currentGroup.clear();
                    currentGroup.push_back(curr);
                }
            }
        }

        // Process last group of ones
        if (currentGroup.size() > 1) {
            int repBin = currentGroup[currentGroup.size() / 2];
            mergedResults.push_back({repBin, static_cast<int>(currentGroup.size())});
            for (int b : currentGroup) {
                mergedBins.insert(b);
            }
        }

        // ===== Write histogram =====
        TH1D* peakStatistics2 = new TH1D("peak_statistics_2", "Merged Peak Locations Distribution", 1024, 0, 1024);
        for (const auto &p : mergedResults) {
            int bin = p.first;
            int count = p.second;
            for (int i = 0; i < count; ++i) {
                peakStatistics2->Fill(bin);
            }
        }
        peakStatistics2->Write();
    }
    //----------------------------------------------------------------------------------
    



    peakStatistics->Write();
    outputFile->Close();
    inputFile->Close();
    
    std::cout << "\n\nAll histograms processed and saved in " << outputFileName << std::endl;
}

void peakWVF_drawing_finder_singleEvent() {
    const char* inputFile = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/t0_rootFiles/data_3k_new20250528/decon_wvf_coincidence_applyCut/wvfFind_event9848_trackID27_opNum9.root";

//    const char* inputFile = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/t0_rootFiles/data_3k_new20250528/decon_wvf_coincidence_applyCut/wvfFind_event95280_trackID24_opNum5.root";

//     const char* inputFile = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/t0_rootFiles/data_3k_new20250528/decon_wvf_coincidence_applyCut/wvfFind_event94961_trackID17_opNum5_merged.root";

//     const char* inputFile = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/t0_rootFiles/data_3k_new20250528/decon_wvf_coincidence_applyCut/wvfFind_event94325_trackID9_opNum4_merged.root";
    
//     const char* inputFile = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/t0_rootFiles/data_3k_new20250528/decon_wvf_coincidence_applyCut/wvfFind_event93261_trackID24_opNum8.root"; 
    
//    const char* inputFile = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/t0_rootFiles/data_3k_new20250528/decon_wvf_coincidence_applyCut/wvfFind_event9240_trackID0_opNum5.root";  

//    const char* inputFile = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/t0_rootFiles/data_3k_new20250528/decon_wvf_coincidence_applyCut/wvfFind_event88685_trackID11_opNum6.root";  

//    const char* inputFile = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/t0_rootFiles/data_3k_new20250528/decon_wvf_coincidence_applyCut/wvfFind_event88367_trackID2_opNum5_2.root";  

//    const char* inputFile = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/t0_rootFiles/data_3k_new20250528/decon_wvf_coincidence_applyCut/wvfFind_event87967_trackID8_opNum9.root";  

//    const char* inputFile = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/t0_rootFiles/data_3k_new20250528/decon_wvf_coincidence_applyCut/wvfFind_event80924_trackID5_opNum4_merged.root";  



    processAllHistograms(inputFile, 0.1);

}


