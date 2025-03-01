import re

def extract_michel_blocks(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        lines = infile.readlines()
        
        # Regex patterns to extract required information
        michel_block_pattern = re.compile(r"======Michel e CAND! \(score>0.03\) COUNT======")
        score_pattern = re.compile(r"Michel score: ([\d\.]+)")
        hits_pattern = re.compile(r"Michel hits: (\d+)")
        end_pattern = re.compile(r"End\(x, y, z\) = \((-?\d*\.?\d*), (-?\d*\.?\d*), (-?\d*\.?\d*)\)")
        
        keep_block = False
        current_block = []
        
        for line in lines:
            if michel_block_pattern.search(line):
                if current_block and keep_block:
                    outfile.writelines(current_block)
                    outfile.write("\n")
                current_block = [line]
                keep_block = False
                continue
            
            current_block.append(line)
            
            score_match = score_pattern.search(line)
            if score_match:
                score = float(score_match.group(1))
            
            hits_match = hits_pattern.search(line)
            if hits_match:
                hits = int(hits_match.group(1))
            
            end_match = end_pattern.search(line)
            if end_match:
                end_x = float(end_match.group(1))
                end_y = float(end_match.group(2))
                end_z = float(end_match.group(3))
                
                #---Selection cut---------------------------------------------
                if (score > 0.4 and hits > 5 and 
                    -356 < end_x < 356 and
                    30 < end_y < 580 and
                    30 < end_z < 435):
                    keep_block = True
        
        # Write the last block if valid
        if current_block and keep_block:
            outfile.writelines(current_block)
            outfile.write("\n")

# Usage
extract_michel_blocks("../../../server/beamRun28867_1000Files/print_1000Files.txt", "./filtered_print.txt")
