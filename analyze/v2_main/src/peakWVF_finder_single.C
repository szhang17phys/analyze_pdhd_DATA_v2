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
    // Vector to collect peak positions from "ch" waveforms for the merged histogram
    std::vector<double> allPeakPositions2;
    
    while ((obj = nextKey())) {
        std::string histName = obj->GetName();
        TH1D* hist = (TH1D*)inputFile->Get(histName.c_str());
        if (!hist || !hist->InheritsFrom("TH1D")) continue;
        
        hist->SetName(histName.c_str()); // Ensure the name remains correct
        std::vector<Peak> peaks = findPeaks(hist, heightThreshold);
        std::cout << "\nDetected " << peaks.size() << " peaks in " << histName << ":" << std::endl;
        
        std::vector<double> peakX, peakY;
        for (const auto& peak : peaks) {
            std::cout << "Peak at bin " << peak.binIndex << ", Left Height: " << peak.leftHeight << ", Right Height: " << peak.rightHeight << std::endl;
            double peakPos = hist->GetBinCenter(peak.binIndex);
            peakX.push_back(peakPos);
            peakY.push_back(hist->GetBinContent(peak.binIndex));
            // For "ch" waveforms, fill the original peak_statistics and also store the value for merged statistics.
            if (histName.rfind("ch", 0) == 0) {
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
    
    // Process the "hwftot" histogram if present
    if (inputFile->Get("hwftot")) {
        TH1D* hwftotHist = (TH1D*)inputFile->Get("hwftot");
        std::vector<Peak> hwftotPeaks = findPeaks(hwftotHist, 0.5);//threshold as 0.5---
        std::cout << "\n\n------Detected " << hwftotPeaks.size() << " peaks in hwftot:------" << std::endl;
        
        std::vector<double> hwftotPeakX, hwftotPeakY;
        for (const auto& peak : hwftotPeaks) {
            std::cout << "Peak at bin " << peak.binIndex << ", Left Height: " << peak.leftHeight << ", Right Height: " << peak.rightHeight << std::endl;
            hwftotPeakX.push_back(hwftotHist->GetBinCenter(peak.binIndex));
            hwftotPeakY.push_back(hwftotHist->GetBinContent(peak.binIndex));
        }
        
        TCanvas hwftotCanvas("hwftot_peakCanvas", "hwftot Peak Finding", 800, 600);
        hwftotHist->SetLineColor(kBlue);
        hwftotHist->Draw();
        
        TGraph* hwftotPeakMarkers = new TGraph(hwftotPeakX.size(), &hwftotPeakX[0], &hwftotPeakY[0]);
        hwftotPeakMarkers->SetMarkerStyle(20);
        hwftotPeakMarkers->SetMarkerSize(1.2);
        hwftotPeakMarkers->SetMarkerColor(kRed);
        hwftotPeakMarkers->Draw("P SAME");
        
        hwftotCanvas.Write();
    }
    
    // --- New code for peak_statistics_2 ---
    if (!allPeakPositions2.empty()) {
        // Sort the collected peak positions
        std::sort(allPeakPositions2.begin(), allPeakPositions2.end());
        std::vector<double> mergedPeakValues;
        std::vector<double> currentGroup;
        currentGroup.push_back(allPeakPositions2[0]);
        
        // Group adjacent values (difference between successive entries <= 1)
        for (size_t i = 1; i < allPeakPositions2.size(); ++i) {
            if (allPeakPositions2[i] - allPeakPositions2[i-1] <= 1.0) {
                currentGroup.push_back(allPeakPositions2[i]);
            } else {
                // Compute the mode (most frequent rounded value) for the current group
                std::map<int, int> freq;
                for (double val : currentGroup) {
                    int roundedVal = static_cast<int>(std::round(val));
                    freq[roundedVal]++;
                }
                int mode = static_cast<int>(std::round(currentGroup[0]));
                int maxCount = 0;
                for (auto& p : freq) {
                    if (p.second > maxCount) {
                        maxCount = p.second;
                        mode = p.first;
                    }
                }
                // For every element in the group, push the mode value
                for (size_t j = 0; j < currentGroup.size(); ++j) {
                    mergedPeakValues.push_back(mode);
                }
                currentGroup.clear();
                currentGroup.push_back(allPeakPositions2[i]);
            }
        }
        // Process the last group
        if (!currentGroup.empty()){
            std::map<int, int> freq;
            for (double val : currentGroup) {
                int roundedVal = static_cast<int>(std::round(val));
                freq[roundedVal]++;
            }
            int mode = static_cast<int>(std::round(currentGroup[0]));
            int maxCount = 0;
            for (auto& p : freq) {
                if (p.second > maxCount) {
                    maxCount = p.second;
                    mode = p.first;
                }
            }
            for (size_t j = 0; j < currentGroup.size(); ++j) {
                mergedPeakValues.push_back(mode);
            }
        }
        
        TH1D* peakStatistics2 = new TH1D("peak_statistics_2", "Merged Peak Locations Distribution", 1024, 0, 1024);
        for (auto val : mergedPeakValues) {
            peakStatistics2->Fill(val);
        }
        peakStatistics2->Write();
    }
    // --- End new code ---
    
    peakStatistics->Write();
    outputFile->Close();
    inputFile->Close();
    
    std::cout << "\n\nAll histograms processed and saved in " << outputFileName << std::endl;
}

void peakWVF_finder_single() {
    const char* inputFile = "../../../../t0_rootFiles/data/small_test/decon_wvfs/event92832_run28867.root";
    processAllHistograms(inputFile, 0.1);
};
