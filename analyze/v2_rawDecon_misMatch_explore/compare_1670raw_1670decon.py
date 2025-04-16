import ROOT
import os

# Define the directories containing the ROOT files
input_directory_raw = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/t0_rootFiles/data/event_wvf_extract"
input_directory_decon = "/Users/shuaixiangzhang/Work/current/FNAL_Work2024/michel_e/t0_tagging/pdhd_DATA_v2/t0_rootFiles/data/Decon_event_wvf_extract"

# Define the output text files
output_txt_file_raw = "1670raw_extract.txt"
output_txt_file_decon = "1670decon_extract.txt"

# Function to process ROOT files and extract channel numbers into a text file
def process_files(input_directory, output_txt_file):
    with open(output_txt_file, "w") as txt_file:
        # Loop over all ROOT files in the input directory
        for root_file_name in os.listdir(input_directory):
            # Check if the file is a ROOT file
            if root_file_name.endswith(".root"):
                root_file_path = os.path.join(input_directory, root_file_name)
                
                # Open the ROOT file
                root_file = ROOT.TFile.Open(root_file_path)
                
                # Loop over all keys in the ROOT file (looking for TH1D objects)
                for key in root_file.GetListOfKeys():
                    # Check if the key refers to a TH1D object
                    if isinstance(key.ReadObj(), ROOT.TH1D):
                        hist_name = key.GetName()
                        
                        # Extract the value after "ms_ch" in the histogram name
                        if "ms_ch" in hist_name:
                            # Extract the channel number (after "ms_ch")
                            channel_number = int(hist_name.split("ms_ch")[1])
                            
                            # Write the channel number to the text file
                            txt_file.write(f"{channel_number}\n")
                
                # Close the current ROOT file
                root_file.Close()

# Process ROOT files from both directories and write to respective text files
process_files(input_directory_raw, output_txt_file_raw)
process_files(input_directory_decon, output_txt_file_decon)

print(f"Processing complete. Channel numbers written to: {output_txt_file_raw} and {output_txt_file_decon}")
