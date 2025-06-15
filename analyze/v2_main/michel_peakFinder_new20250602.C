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
//   (a). Threshold set as 0.5; 
//   (b). save first three peaks (bin indices) (descending order)
//  
//2. Check single wvf coincidence   
//   (a). Record coincidence from single wvf; Apply new merging method
//   (b). record first-3 (>=3) candidates (indice and #coin)(Ex: 7, 4, 4, 4, 3)
//
//3. Matching between (summed wvf) and (single wvf coincidence)
//   (a). Strongest peak will be regarded as muon peak
//   (b). Check 2nd strongest peak, to see if it happens at wvf coincidence group
//   (e). For 3rd strongest peak: TBD
//   (f). If there is no 2nd strongest peak, record michelTime as 0, michelCoin as 0
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



// Process a single ROOT file: build a local frequency map from histograms containing "ms_ch",
// merge bins within ±2, sort by frequency, and record the top two results.
// return a dictionary, key is peak location, value is #(peak coincidence)
void processSingleFile(const char* inputFileName, double heightThreshold) {  

    // Process input root file ---------------------------------------------------------
    TFile* inputFile = TFile::Open(inputFileName, "READ");
    if (!inputFile || inputFile->IsZombie()) {
        std::cerr << "Error: Could not open input file!" << std::endl;
        return;
    }

    TIter nextKey(inputFile->GetListOfKeys());
    TObject* obj;

    // Frequency map: key is the peak bin index, value is the count.
    std::map<int, int> freqMap;

    // To store top 3 peak bin indices from "total" histogram
    std::vector<int> topTotalPeaks;

    while ((obj = nextKey())) { // process TH1D one by one ----------
        std::string histName = obj->GetName();
        TH1D* hist = dynamic_cast<TH1D*>(inputFile->Get(histName.c_str()));
        if (!hist) continue;

        // Set height threshold for total waveform=======================
        double thresholdToUse = heightThreshold;
        if (histName == "total") {
            thresholdToUse = 0.5;
        }

        // Find peaks
        std::vector<Peak> peaks = findPeaks(hist, thresholdToUse);

        std::cout << "Histogram: " << histName << std::endl;
        for (const auto& peak : peaks) {
            std::cout << "  Peak at bin " << peak.binIndex 
                      << ", Left Height: " << peak.leftHeight 
                      << ", Right Height: " << peak.rightHeight 
                      << std::endl;
        }
        std::cout << std::endl;

        // Count frequency for ms_ch histograms only
        if (histName.find("ms_ch") != std::string::npos) {
            for (const auto& peak : peaks) {
                freqMap[peak.binIndex]++;
            }
        }

        // Special handling for "total" histogram: sort and record top 3 peaks
        if (histName == "total") {
            // Sort by min(leftHeight, rightHeight), descending
            std::sort(peaks.begin(), peaks.end(), [](const Peak& a, const Peak& b) {
                double heightA = std::min(a.leftHeight, a.rightHeight);
                double heightB = std::min(b.leftHeight, b.rightHeight);
                return heightA > heightB;
            });

            // Record the first 3 bin locations (or fewer if not enough)
            for (size_t i = 0; i < std::min<size_t>(3, peaks.size()); ++i) {
                topTotalPeaks.push_back(peaks[i].binIndex);
            }

            // Pad with 0 if only one peak found
            if (topTotalPeaks.size() == 1) {
                topTotalPeaks.push_back(0);
            }
        }

    }

    // Example debug print for topTotalPeaks
    std::cout << "Top total peaks (by true height): ";
    for (int bin : topTotalPeaks) {
        std::cout << bin << " ";
    }
    std::cout << std::endl;

    inputFile->Close();
    //---------------------------------------------------------------------------------    



    //----------Peak Merging-----------------------------------------------------------
    // Convert the frequency map to a sorted vector by bin index
    std::vector<std::pair<int, int>> freqVector(freqMap.begin(), freqMap.end());
    std::sort(freqVector.begin(), freqVector.end(), [](const auto &a, const auto &b) {
        return a.first < b.first;
    });

    std::unordered_set<int> mergedBins;
    std::vector<std::pair<int, int>> mergedFrequencies;

    // ===== Phase 1: Use count ≥ 2 as seed, merge all non-zero neighbors within ±2 =====
    for (const auto &p : freqVector) {
        int bin = p.first;
        int count = p.second;

        // Skip if already merged or not a strong seed
        if (count < 2 || mergedBins.count(bin)) continue;

        int groupSum = count;
        mergedBins.insert(bin);

        // Check neighbors within ±2
        for (int offset = -2; offset <= 2; ++offset) {
            if (offset == 0) continue;
            int neighborBin = bin + offset;

            auto it = freqMap.find(neighborBin);
            if (it != freqMap.end() && it->second > 0 && !mergedBins.count(neighborBin)) {
                groupSum += it->second;
                mergedBins.insert(neighborBin);
            }
        }

        mergedFrequencies.push_back({bin, groupSum});
    }

    // ===== Phase 2: Merge unmerged count = 1 bins into tight clusters (span ≤ 4, gap ≤ 2) =====
    std::vector<std::pair<int, int>> remainingOnes;
    for (const auto &p : freqVector) {
        if (p.second == 1 && !mergedBins.count(p.first)) {
            remainingOnes.push_back(p);
        }
    }

    std::vector<std::pair<int, int>> currentGroup;
    for (size_t i = 0; i < remainingOnes.size(); ++i) {
        const auto &p = remainingOnes[i];

        if (currentGroup.empty()) {
            currentGroup.push_back(p);
        } else {
            int lastBin = currentGroup.back().first;
            int firstBin = currentGroup.front().first;
            int currentBin = p.first;

            // Check adjacency and span
            if ((currentBin - lastBin <= 2) && (currentBin - firstBin <= 4)) {
                currentGroup.push_back(p);
            } else {
                if (currentGroup.size() > 1) {
                    int groupSum = currentGroup.size();
                    int representativeBin = currentGroup[currentGroup.size() / 2].first;
                    for (const auto &entry : currentGroup) {
                        mergedBins.insert(entry.first);
                    }
                    mergedFrequencies.push_back({representativeBin, groupSum});
                }
                currentGroup.clear();
                currentGroup.push_back(p);
            }
        }
    }

    // Final group from phase 2
    if (currentGroup.size() > 1) {
        int groupSum = currentGroup.size();
        int representativeBin = currentGroup[currentGroup.size() / 2].first;
        for (const auto &entry : currentGroup) {
            mergedBins.insert(entry.first);
        }
        mergedFrequencies.push_back({representativeBin, groupSum});
    }

    // ===== Final sort by frequency descending =====
    std::sort(mergedFrequencies.begin(), mergedFrequencies.end(), [](const auto &a, const auto &b) {
        return a.second > b.second;
    });
    //---------------------------------------------------------------------------------

    

    



    //Store first three pairs of "mergedFrequencies"-----------------------------------
    //Print only those merged frequencies with occurrences >= 2.
    std::cout << "\nMerged Peak bin frequency (for file " << inputFileName 
              << " and histograms containing \"ms_ch\"):" << std::endl;
    for (const auto &p : mergedFrequencies) {
        if (p.second >= 2)
            std::cout << "  Bin " << p.first << ": " << p.second << " occurrences (merged)" << std::endl;
    }

    std::map<int, int> topMergedMap;
    size_t nMerged = mergedFrequencies.size();
    if (nMerged == 0) {
        topMergedMap[0] = 0;
        topMergedMap[-1] = 0;
        topMergedMap[-2] = 0;
    }
    if (nMerged == 1) {
        topMergedMap[mergedFrequencies[0].first] = mergedFrequencies[0].second;
        topMergedMap[0] = 0;
        topMergedMap[-1] = 0;
    }
    if (nMerged == 2) {
        topMergedMap[mergedFrequencies[0].first] = mergedFrequencies[0].second;
        topMergedMap[mergedFrequencies[1].first] = mergedFrequencies[1].second;
        topMergedMap[0] = 0;
    }
    // nMerged >= 3: Include top entries with ties at 3rd highest value
    size_t limit = 3;
    int threshold = mergedFrequencies[limit - 1].second;

    for (const auto& [bin, count] : mergedFrequencies) {
        if (count < threshold) break;
        topMergedMap[bin] = count;
    }
    //---------------------------------------------------------------------------------






    //Matching between topTotalPeaks and topMergeMap-----------------------------------
    std::cout << "\n---- Matching topTotalPeaks with topMergedMap ----" << std::endl;

    for (size_t i = 0; i < topTotalPeaks.size(); ++i) {
        int totalBin = topTotalPeaks[i];
        bool foundMatch = false;

        for (const auto& [mergedBin, count] : topMergedMap) {
            if (std::abs(totalBin - mergedBin) <= 2) {
                std::cout << "topTotalPeaks[" << i << "] = " << totalBin
                          << " matched with mergedBin = " << mergedBin
                          << ", Coinc count = " << count << std::endl;
                foundMatch = true;
            }
        }
        if (!foundMatch) {
            std::cout << "topTotalPeaks[" << i << "] = " << totalBin << " has no matching mergedBin." << std::endl;
        }
    }


    std::ofstream muonFile("peakFinder_muonTime_new20250602.txt", std::ios::app);
    std::ofstream michelTimeFile("peakFinder_michelTime_new20250602.txt", std::ios::app);
    std::ofstream michelCoincidenceFile("peakFinder_michelCoincidence_new20250602.txt", std::ios::app);

    // Save first peak (muon time) unconditionally
    if (!topTotalPeaks.empty()) {
        muonFile << inputFileName << ": " << topTotalPeaks[0] << "\n";
        std::cout << "[Saved] Muon time peak: " << topTotalPeaks[0] << std::endl;
    }

    // Save second peak (michel time + coincidence)
    if (topTotalPeaks.size() >= 2) {
        int secondPeak = topTotalPeaks[1];
        bool matched = false;
        int matchedCoincidence = 0;

        for (const auto& [mergedBin, count] : topMergedMap) {
            if (std::abs(secondPeak - mergedBin) <= 2) {
                matched = true;
                matchedCoincidence = count;
                break;
            }
        }

        michelTimeFile << inputFileName << ": " << secondPeak << "\n";
        michelCoincidenceFile << inputFileName << ": " << (matched ? matchedCoincidence : 0) << "\n";

        std::cout << "[Saved] Michel time peak: " << secondPeak
                  << ", Coincidence count: " << (matched ? matchedCoincidence : 0) << std::endl;
    }

    muonFile.close();
    michelTimeFile.close();
    michelCoincidenceFile.close();

    //---------------------------------------------------------------------------------

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
        std::cout << "\n\n\nProcessing file: " << fullPath << std::endl;
        std::cout << "\nThreshold for ms_ch is 0.1, for total is 0.5!" << std::endl;
        processSingleFile(fullPath.Data(), heightThreshold);
    }
}






//Main function========================================================
// Main entry point: process all ROOT files in the directory one by one.
void michel_peakFinder_new20250602() {
    // Clear output files before starting (20250529): Necessary!!!
    std::ofstream clear1("peakFinder_muonTime_new20250602.txt");
    std::ofstream clear2("peakFinder_michelTime_new20250602.txt");
    std::ofstream clear3("peakFinder_michelCoincidence_new20250602.txt");
    clear1.close();
    clear2.close();
    clear3.close();

    const char* inputDirectory = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/t0_rootFiles/data_28891_FullRun/decon_wvf_coincidence_applyCut_3";
    processDirectory(inputDirectory, 0.1);
}
