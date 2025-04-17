#include <iostream>
#include <vector>
#include <string>
#include <map>
#include <algorithm>
#include <cmath>
#include <fstream>  // for file output
#include "TFile.h"
#include "TH1D.h"
#include "TIterator.h"

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

// Process all TH1D histograms in the file, print peak info,
// count the frequency of peak bin indices for histograms containing "ms_ch",
// and merge frequencies for bins that are within ±2.
void processHistograms(const char* inputFileName, double heightThreshold) {
    TFile* inputFile = TFile::Open(inputFileName, "READ");
    if (!inputFile || inputFile->IsZombie()) {
        std::cerr << "Error: Could not open input file!" << std::endl;
        return;
    }
    
    TIter nextKey(inputFile->GetListOfKeys());
    TObject* obj;
    
    // Frequency map: key is the peak bin index, value is the count.
    std::map<int, int> freqMap;
    
    while ((obj = nextKey())) {
        std::string histName = obj->GetName();
        // Retrieve the object as a TH1D histogram
        TH1D* hist = dynamic_cast<TH1D*>(inputFile->Get(histName.c_str()));
        if (!hist) continue;
        
        // Find peaks in the histogram
        std::vector<Peak> peaks = findPeaks(hist, heightThreshold);
        std::cout << "Histogram: " << histName << std::endl;
        for (const auto& peak : peaks) {
            std::cout << "  Peak at bin " << peak.binIndex 
                      << ", Left Height: " << peak.leftHeight 
                      << ", Right Height: " << peak.rightHeight 
                      << std::endl;
        }
        std::cout << std::endl;
        
        // For histograms containing "ms_ch", count the frequency of each peak's bin index.
        if (histName.find("ms_ch") != std::string::npos) {
            for (const auto& peak : peaks) {
                freqMap[peak.binIndex]++;
            }
        }
    }
    
    inputFile->Close();
    
    // Convert the frequency map to a sorted vector (sorted by bin index)
    std::vector<std::pair<int, int>> freqVector(freqMap.begin(), freqMap.end());
    std::sort(freqVector.begin(), freqVector.end(), [](const auto &a, const auto &b) {
        return a.first < b.first;
    });
    
    // Merge frequencies for bins within ±2.
    std::vector<std::pair<int, int>> mergedFrequencies;
    std::vector<std::pair<int, int>> currentGroup;
    
    for (const auto &p : freqVector) {
        if (currentGroup.empty()) {
            currentGroup.push_back(p);
        } else {
            int lastBin = currentGroup.back().first;
            if (p.first - lastBin <= 2) {
                currentGroup.push_back(p);
            } else {
                // Process current group: choose representative bin (max frequency)
                // and sum all counts.
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
    // Process the last group if any
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
    
    // Sort merged frequencies by total frequency in descending order.
    std::sort(mergedFrequencies.begin(), mergedFrequencies.end(), [](const auto &a, const auto &b) {
        return a.second > b.second;
    });
    
    // Extract the file name from the input file path.
    std::string filePath(inputFileName);
    size_t pos = filePath.find_last_of("/\\");
    std::string fileName = (pos != std::string::npos) ? filePath.substr(pos+1) : filePath;
    std::cout << "File: " << fileName << std::endl;
    
    // Print the merged frequency results (only those with occurrences >=2).
    std::cout << "Merged Peak bin frequency (for histograms containing \"ms_ch\"):" << std::endl;
    for (const auto &p : mergedFrequencies) {
        if (p.second >= 2) {
            std::cout << "  Bin " << p.first << ": " << p.second << " occurrences (merged)" << std::endl;
        }
    }
}

// Main function to run the peak finder on a single file
void peakWVF_finder_singleEvent() {
    const char* inputFile = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/t0_rootFiles/data/Decon_wvfNumCut5_merged/wvfFind_event94849_trackID1_opNum9.root"; // Change this to your ROOT file
    processHistograms(inputFile, 0.1);
}
