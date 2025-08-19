#include <iostream>
#include <vector>
#include <string>
#include <map>
#include <algorithm>
#include <cmath>
#include <fstream>    // For file output
#include "TFile.h"
#include "TH1D.h"
#include "TIterator.h"
#include "TSystem.h"
#include "TSystemDirectory.h"
#include "TList.h"
#include "TSystemFile.h"


//Commented by Shu, 20250602----------------------------------------------------
//Compared with previous script, we have some new properties:
//1. Peak finding at summed wvf
//   (a). Threshold set as 0.3; 
//   (b). save first three peaks (bin indices) (descending order)
//  
//------------------------------------------------------------------------------


// Structure to hold peak information
struct Peak {
    int binIndex;
    double leftHeight;
    double rightHeight;
};


// Function to find peaks in a histogram with a given height threshold
std::vector<Peak> findPeaks(TH1D* hist, double heightThreshold) {
    std::vector<Peak> peaks;
    int numBins = hist->GetNbinsX();

    // Loop over bins, avoiding the extreme edges
    for (int i = 2; i < numBins; ++i) {
        double centerVal = hist->GetBinContent(i);
        double leftVal = hist->GetBinContent(i - 1);
        double rightVal = hist->GetBinContent(i + 1);

        // Check if current bin is a local maximum
        if (centerVal > leftVal && centerVal > rightVal) {
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





void processSingleFile(const char* inputFileName, const double thre_summed) {  

    // Process input root file ---------------------------------------------------------
    TFile* inputFile = TFile::Open(inputFileName, "READ");
    if (!inputFile || inputFile->IsZombie()) {
        std::cerr << "Error: Could not open input file!" << std::endl;
        return;
    }


    // Retrieve the "total" histogram
    TH1D* hist = dynamic_cast<TH1D*>(inputFile->Get("total"));
    if (!hist) {
        std::cerr << "Cannot find histogram 'total'" << std::endl;
        inputFile->Close();
        return;
    }
    hist->SetDirectory(0);  // Disconnect from file


    // Set threshold for total histogram===========================
    double thresholdToUse = thre_summed;
    //=============================================================


    // Find peaks
    std::vector<Peak> peaks = findPeaks(hist, thresholdToUse);

    // Print peaks
    std::cout << "Histogram: total" << std::endl;
    for (const auto& peak : peaks) {
        std::cout << "    Peak at bin " << peak.binIndex 
                  << ", Left Height: " << peak.leftHeight 
                  << ", Right Height: " << peak.rightHeight 
                  << std::endl;
    }
    std::cout << std::endl;

    // Sort peaks by minimum side height
    std::sort(peaks.begin(), peaks.end(), [](const Peak& a, const Peak& b) {
        double heightA = std::min(a.leftHeight, a.rightHeight);
        double heightB = std::min(b.leftHeight, b.rightHeight);
        return heightA > heightB;
    });

    // Record top 3 peak bin indices
    std::vector<int> topTotalPeaks_index;
    std::vector<double> topTotalPeaks_intensity;
    for (size_t i = 0; i < std::min<size_t>(3, peaks.size()); ++i) {
        topTotalPeaks_index.push_back(peaks[i].binIndex);
        topTotalPeaks_intensity.push_back(std::min(peaks[i].leftHeight, peaks[i].rightHeight));        
    }

    // Handle special case if only one peak
    if (topTotalPeaks_index.size() == 1) {
        topTotalPeaks_index.push_back(0);
        topTotalPeaks_intensity.push_back(0);
    }


    // Example debug print for topTotalPeaks_index
    std::cout << "Top total peaks (by true height): ";
    for (int bin : topTotalPeaks_index) {
        std::cout << bin << " ";
    }
    std::cout << std::endl;

    inputFile->Close();
    delete inputFile;
    //------------------------------------------------    

    //Store muon and Michel candidates-------------------------------------------------
    std::cout << "\n---- Saving Time info of muon and Michel candidates ----" << std::endl;

    std::ofstream muonFile("peakFinder_muonTime_index.txt", std::ios::app);
    std::ofstream michelFile("peakFinder_michelTime_index.txt", std::ios::app);
    std::ofstream muonFile_2("peakFinder_muonTime_intensity.txt", std::ios::app);
    std::ofstream michelFile_2("peakFinder_michelTime_intensity.txt", std::ios::app);    

    // Save first peak (muon time) unconditionally
    if (!topTotalPeaks_index.empty()) {
        muonFile << inputFileName << ": " << topTotalPeaks_index[0] << "\n";
        muonFile_2 << inputFileName << ": " << topTotalPeaks_intensity[0] << "\n";
        std::cout << "[Saved] Muon time peak index: " << topTotalPeaks_index[0] << std::endl;
        std::cout << "        Intensity: " << topTotalPeaks_intensity[0] << std::endl;        
    }

    // Save second peak (Michel time)
    if (topTotalPeaks_index.size() >= 2) {
        michelFile << inputFileName << ": " << topTotalPeaks_index[1] << "\n";
        michelFile_2 << inputFileName << ": " << topTotalPeaks_intensity[1] << "\n";        
        std::cout << "[Saved] Michel time peak: " << topTotalPeaks_index[1] << std::endl;
        std::cout << "        Intensity: " << topTotalPeaks_intensity[1] << std::endl;
    }


    muonFile.close();
    michelFile.close();
    muonFile_2.close();
    michelFile_2.close();    
    // --------------------------------------------------------------------------------

}






// Process each ROOT file in the specified directory individually.
void processDirectory(const char* directoryName, const double thre) {
    TSystemDirectory dir(directoryName, directoryName);
    TList* files = dir.GetListOfFiles();
    if (!files) {
        std::cerr << "No files found in directory: " << directoryName << std::endl;
        return;
    }

    TSystemFile* file;
    TIter next(files);

    std::vector<TString> fileList;

    // Collect all valid ROOT files
    while ((file = (TSystemFile*)next())) {
        TString fname = file->GetName();
        if (file->IsDirectory()) continue;
        if (!fname.EndsWith(".root")) continue;

        TString fullPath = TString(directoryName) + "/" + fname;
        fileList.push_back(fullPath);
    }

    // Sort the file paths alphabetically
    std::sort(fileList.begin(), fileList.end());

    // Loop through sorted files
    for (size_t counter = 0; counter < fileList.size(); ++counter) {
        const TString& fullPath = fileList[counter];

        std::cout << "\n\n[" << counter << "] Processing file: " << fullPath << std::endl;
        std::cout << "\nThreshold for summed wvf: "<< thre << std::endl;

        processSingleFile(fullPath.Data(), thre);
    }
}







//Main function========================================================
// Main entry point: process all ROOT files in the directory one by one.

//"Part I"----------------------------
void intensity_thre() {

    //Suggested by ChatGPT; 20250614; Avoid storing histograms in memory by default
    gROOT->cd(); 

    // Clear output files before starting (20250529): Necessary!!!
    std::ofstream clear1("peakFinder_muonTime_index.txt");
    std::ofstream clear2("peakFinder_michelTime_index.txt");
    std::ofstream clear3("peakFinder_muonTime_intensity.txt");
    std::ofstream clear4("peakFinder_michelTime_intensity.txt");    
    clear1.close();
    clear2.close();
    clear3.close();
    clear4.close();    

    const char* inputDirectory = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/t0_rootFiles/new20250808_MC/wvf_merged_applyCut_20250809";
    processDirectory(inputDirectory, 0.3);//Threshold for summed wvf---
}

