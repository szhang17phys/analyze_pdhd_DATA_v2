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


// Define Peak struct with turning points included
struct Peak {
    int binCenter;
    double leftHeight;
    double rightHeight;
    int leftTurn;   // new
    int rightTurn;  // new
};

// Function to find peaks in a histogram with a given height threshold
std::vector<Peak> findPeaks(TH1D* hist, double heightThreshold) {
    std::vector<Peak> peaks;
    int numBins = hist->GetNbinsX();

    // Loop over bins, avoiding the extreme edges
    for (int i = 2; i < numBins; ++i) {
        double centerVal = hist->GetBinContent(i);
        double leftVal   = hist->GetBinContent(i - 1);
        double rightVal  = hist->GetBinContent(i + 1);

        // Check if current bin is a local maximum
        if (centerVal > leftVal && centerVal > rightVal) {
            int leftIndex = i - 1;
            while (leftIndex > 1 &&
                   hist->GetBinContent(leftIndex - 1) < hist->GetBinContent(leftIndex)) {
                leftIndex--;
            }
            int rightIndex = i + 1;
            while (rightIndex < numBins &&
                   hist->GetBinContent(rightIndex + 1) < hist->GetBinContent(rightIndex)) {
                rightIndex++;
            }

            double leftHeight  = centerVal - hist->GetBinContent(leftIndex);
            double rightHeight = centerVal - hist->GetBinContent(rightIndex);

            if (leftHeight > heightThreshold && rightHeight > heightThreshold) {
                peaks.push_back({i, leftHeight, rightHeight, leftIndex, rightIndex});
            }
        }
    }
    return peaks;
};




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

    // Set threshold
    double thresholdToUse = thre_summed;

    // Find peaks
    std::vector<Peak> peaks = findPeaks(hist, thresholdToUse);

    // Print peaks
    std::cout << "Histogram: total" << std::endl;
    for (const auto& peak : peaks) {
        std::cout << "    Peak at bin " << peak.binCenter 
                  << ", Left turn bin (height): " << peak.leftTurn << "(" << peak.leftHeight 
                  << "), Right turn: " << peak.rightTurn <<"(" << peak.rightHeight 
                  << ")" << std::endl;
    }
    std::cout << std::endl;

    // Sort peaks by minimum side height
    std::sort(peaks.begin(), peaks.end(), [](const Peak& a, const Peak& b) {
        double heightA = std::min(a.leftHeight, a.rightHeight);
        double heightB = std::min(b.leftHeight, b.rightHeight);
        return heightA > heightB;
    });

    inputFile->Close();
    delete inputFile;
    //------------------------------------------------    

    // Store muon and Michel candidates ------------------------------------------------
    std::cout << "\n---- Saving Time info of muon, Michel and 3rd candidates ----" << std::endl;

    std::ofstream muonFile("muon_total_20251015.txt", std::ios::app);
    std::ofstream michelFile("michel_total_20251015.txt", std::ios::app);
    std::ofstream thirdFile("third_total_20251015.txt", std::ios::app);

    // --- Save first peak (muon) ---
    if (peaks.size() >= 1) {
        const auto& muonPeak = peaks[0];
        double finalIntensity = std::min(muonPeak.leftHeight, muonPeak.rightHeight);

        muonFile << inputFileName << ": "
                 << muonPeak.binCenter << ", "
                 << finalIntensity << ", "
                 << muonPeak.leftTurn << ", " << muonPeak.leftHeight << ", "
                 << muonPeak.rightTurn << ", " << muonPeak.rightHeight << "\n";

        std::cout << "[Saved] Muon time peak: " << muonPeak.binCenter << std::endl;
        std::cout << "        Final intensity (min side): " << finalIntensity << std::endl;
        std::cout << "        Left turn: " << muonPeak.leftTurn
                  << " (height=" << muonPeak.leftHeight << ")" << std::endl;
        std::cout << "        Right turn: " << muonPeak.rightTurn
                  << " (height=" << muonPeak.rightHeight << ")" << std::endl;
    } else {
        muonFile << inputFileName << ": 0, 0, 0, 0, 0, 0\n";
        std::cout << "[Saved] Muon peak missing → filled with zeros" << std::endl;     
    }

    // --- Save second peak (Michel) ---
    if (peaks.size() >= 2) {
        const auto& michelPeak = peaks[1];
        double finalIntensity = std::min(michelPeak.leftHeight, michelPeak.rightHeight);

        michelFile << inputFileName << ": "
                   << michelPeak.binCenter << ", "
                   << finalIntensity << ", "
                   << michelPeak.leftTurn << ", " << michelPeak.leftHeight << ", "
                   << michelPeak.rightTurn << ", " << michelPeak.rightHeight << "\n";

        std::cout << "[Saved] Michel time peak: " << michelPeak.binCenter << std::endl;
        std::cout << "        Final intensity (min side): " << finalIntensity << std::endl;
        std::cout << "        Left turn: " << michelPeak.leftTurn
                  << " (height=" << michelPeak.leftHeight << ")" << std::endl;
        std::cout << "        Right turn: " << michelPeak.rightTurn
                  << " (height=" << michelPeak.rightHeight << ")" << std::endl;
    } else {
        michelFile << inputFileName << ": 0, 0, 0, 0, 0, 0\n";
        std::cout << "[Saved] Michel peak missing → filled with zeros" << std::endl;
    }

    // --- Save third peak ---
    if (peaks.size() >= 3) {
        const auto& thirdPeak = peaks[2];
        double finalIntensity = std::min(thirdPeak.leftHeight, thirdPeak.rightHeight);

        thirdFile << inputFileName << ": "
                  << thirdPeak.binCenter << ", "
                  << finalIntensity << ", "
                  << thirdPeak.leftTurn << ", " << thirdPeak.leftHeight << ", "
                  << thirdPeak.rightTurn << ", " << thirdPeak.rightHeight << "\n";

        std::cout << "[Saved] Third time peak: " << thirdPeak.binCenter << std::endl;
        std::cout << "        Final intensity (min side): " << finalIntensity << std::endl;
        std::cout << "        Left turn: " << thirdPeak.leftTurn
                  << " (height=" << thirdPeak.leftHeight << ")" << std::endl;
        std::cout << "        Right turn: " << thirdPeak.rightTurn
                  << " (height=" << thirdPeak.rightHeight << ")" << std::endl;
    } else {
        thirdFile << inputFileName << ": 0, 0, 0, 0, 0, 0\n";
        std::cout << "[Saved] Third peak missing → filled with zeros" << std::endl;
    }


    muonFile.close();
    michelFile.close();
    thirdFile.close();
    // --------------------------------------------------------------------------------

};





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
    std::ofstream clear1("muon_total_20251015.txt");
    std::ofstream clear2("michel_total_20251015.txt");
    std::ofstream clear3("third_total_20251015.txt");  // NEW
    clear1.close();
    clear2.close();   
    clear3.close();

    const char* inputDirectory = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/t0_rootFiles/new202510_MC/wvf_merged_applyCut_20251015";
    processDirectory(inputDirectory, 0.3);//Threshold for summed wvf---
}



