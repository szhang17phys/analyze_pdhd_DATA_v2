# Combine two large text files into one
def combine_text_files(file1, file2, output_file):
    with open(output_file, 'w') as outfile:
        # Write contents of the first file
        with open(file1, 'r') as f1:
            for line in f1:
                outfile.write(line)
        # Write contents of the second file
        with open(file2, 'r') as f2:
            for line in f2:
                outfile.write(line)

# Usage
combine_text_files('print_group1_initial.txt', 'print_group2_initial.txt', 'combined_output.txt')
