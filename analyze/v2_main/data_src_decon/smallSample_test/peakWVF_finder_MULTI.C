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

// Process a single ROOT file: build a local frequency map from histograms containing "ms_ch",
// merge bins within ±2, sort by frequency, and record the top two results.
void processSingleFile(const char* inputFileName, double heightThreshold) {
    std::map<int, int> freqMap;
    
    TFile* inputFile = TFile::Open(inputFileName, "READ");
    if (!inputFile || inputFile->IsZombie()) {
        std::cerr << "Error: Could not open file " << inputFileName << std::endl;
        return;
    }
    
    TIter nextKey(inputFile->GetListOfKeys());
    TObject* obj;
    
    while ((obj = nextKey())) {
        std::string histName = obj->GetName();
        // Retrieve the object as a TH1D histogram
        TH1D* hist = dynamic_cast<TH1D*>(inputFile->Get(histName.c_str()));
        if (!hist) continue;
        
        // Find peaks in the histogram
        std::vector<Peak> peaks = findPeaks(hist, heightThreshold);
        std::cout << "File: " << inputFileName << " | Histogram: " << histName << std::endl;
        for (const auto& peak : peaks) {
            std::cout << "  Peak at bin " << peak.binIndex 
                      << ", Left Height: " << peak.leftHeight 
                      << ", Right Height: " << peak.rightHeight 
                      << std::endl;
        }
        std::cout << std::endl;
        
        // For histograms containing "ms_ch", update the local frequency map.
        if (histName.find("ms_ch") != std::string::npos) {
            for (const auto& peak : peaks) {
                freqMap[peak.binIndex]++;
            }
        }
    }
    
    inputFile->Close();
    
    // Convert the frequency map to a vector sorted by bin index.
    std::vector<std::pair<int,int>> freqVector(freqMap.begin(), freqMap.end());
    std::sort(freqVector.begin(), freqVector.end(), [](const auto &a, const auto &b) {
        return a.first < b.first;
    });
    
    // Merge frequencies for bins that are within ±2.
    std::vector<std::pair<int,int>> mergedFrequencies;
    std::vector<std::pair<int,int>> currentGroup;
    
    for (const auto &p : freqVector) {
        if (currentGroup.empty()) {
            currentGroup.push_back(p);
        } else {
            int lastBin = currentGroup.back().first;
            if (p.first - lastBin <= 2) {
                currentGroup.push_back(p);
            } else {
                int groupSum = 0;
                int representativeBin = currentGroup[0].first;
                int maxCount = currentGroup[0].second;
                for (auto &entry : currentGroup) {
                    groupSum += entry.second;
                    if (entry.second > maxCount) {
                        maxCount = entry.second;
                        representativeBin = entry.first;
                    }
                }
                mergedFrequencies.push_back({representativeBin, groupSum});
                currentGroup.clear();
                currentGroup.push_back(p);
            }
        }
    }
    // Process any remaining group.
    if (!currentGroup.empty()) {
        int groupSum = 0;
        int representativeBin = currentGroup[0].first;
        int maxCount = currentGroup[0].second;
        for (auto &entry : currentGroup) {
            groupSum += entry.second;
            if (entry.second > maxCount) {
                maxCount = entry.second;
                representativeBin = entry.first;
            }
        }
        mergedFrequencies.push_back({representativeBin, groupSum});
    }
    
    // Sort the merged frequencies by descending occurrence.
    std::sort(mergedFrequencies.begin(), mergedFrequencies.end(), [](const auto &a, const auto &b) {
        return a.second > b.second;
    });
    
    // Print only those merged frequencies with occurrences >= 2.
    std::cout << "Merged Peak bin frequency (for file " << inputFileName 
              << " and histograms containing \"ms_ch\"):" << std::endl;
    for (const auto &p : mergedFrequencies) {
        if (p.second >= 2)
            std::cout << "  Bin " << p.first << ": " << p.second << " occurrences (merged)" << std::endl;
    }
    
    // Write the results to text files (appending one line per file).
    std::ofstream muonFile("muonTime.txt", std::ios::app);
    std::ofstream michelTimeFile("michelTime.txt", std::ios::app);
    std::ofstream michelCoincidenceFile("michelCoincidence.txt", std::ios::app);
    
    if (!mergedFrequencies.empty()) {
        muonFile << inputFileName << ": " << mergedFrequencies[0].first << "\n";
        if (mergedFrequencies.size() > 1) {
            michelTimeFile << inputFileName << ": " << mergedFrequencies[1].first << "\n";
            michelCoincidenceFile << inputFileName << ": " << mergedFrequencies[1].second << "\n";
        } else {
            michelTimeFile << inputFileName << ": N/A\n";
            michelCoincidenceFile << inputFileName << ": N/A\n";
        }
    } else {
        muonFile << inputFileName << ": N/A\n";
        michelTimeFile << inputFileName << ": N/A\n";
        michelCoincidenceFile << inputFileName << ": N/A\n";
    }
    
    muonFile.close();
    michelTimeFile.close();
    michelCoincidenceFile.close();
}

// Process each ROOT file in the specified directory individually.
void processDirectory(const char* directoryName, double heightThreshold) {
    TSystemDirectory dir(directoryName, directoryName);
    TList* files = dir.GetListOfFiles();
    if (!files) {
        std::cerr << "No files found in directory: " << directoryName << std::endl;
        return;
    }
    
    TSystemFile* file;
    TIter next(files);
    while ((file = (TSystemFile*)next())) {
        TString fname = file->GetName();
        if (file->IsDirectory()) continue;
        if (!fname.EndsWith(".root")) continue;
        
        TString fullPath = TString(directoryName) + "/" + fname;
        std::cout << "Processing file: " << fullPath << std::endl;
        processSingleFile(fullPath.Data(), heightThreshold);
    }
}

// Main entry point: process all ROOT files in the directory one by one.
void peakWVF_finder_MULTI() {
    const char* inputDirectory = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/t0_rootFiles/data/Decon_wvfNumCut5_merged";
    processDirectory(inputDirectory, 0.1);
}
