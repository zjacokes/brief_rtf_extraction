import re
import csv
import os
import argparse
from striprtf.striprtf import rtf_to_text

# This script is for the BRIEF Self-Report Youth version

# Function to process a single RTF file
def process_rtf_file(file_path):
    # Read the RTF file and extract the plain text
    with open(file_path) as infile:
        content = infile.read()

    rtf_text = rtf_to_text(content)

    ## First chunk (Client information)
    first_pattern = re.compile(
        r'Client\s*ID\s*:\s*\|(?P<client_id>[^\|]+)\|\s*'
        r'Gender\s*:\s*\|(?P<gender>[^\|]+)\|\s*'
        r'Age\s*:\s*\|(?P<age>[^\|]+)\|\s*'
        r'Grade\s*:\s*\|(?P<grade>[^\|]+)\|\s*'
        r'Test\sdate\s*:\s*\|(?P<test_date>[^\|]+)\|\s*'
        r'Language\sadministered\s*:\s*\|(?P<language>[^\|]+)\|\s*',
        re.IGNORECASE
    )

    first_match = first_pattern.search(rtf_text)

    if first_match:
        first_chunk = first_match.groupdict()
    else:
        print(f"No match found for the first chunk in {file_path}")
        return None  # If no match, skip this file
    
    ## Second chunk (Score data)
    second_pattern = re.compile(
        r'Index/Scale\|Raw score\|T score\|Percentile\|90% CI\|\n'  # Match the header
        r'(?P<scores>(?:[^\n]+\|\d+\|\d+\|\d+\|[^\|]+\|\n)+)',  # Match all rows
        re.IGNORECASE
    )

    second_match = second_pattern.search(rtf_text)

    if second_match:
        raw_scores = second_match.group('scores')
        scores_data = []
        for line in raw_scores.strip().split('\n'):
            parts = line.split('|')
            if len(parts) >= 5:
                score_info = {
                    'index_name': parts[0].strip(),
                    'raw_score': parts[1].strip(),
                    't_score': parts[2].strip(),
                    'percentile': parts[3].strip(),
                    'confidence_interval': parts[4].strip()
                }
                scores_data.append(score_info)
    else:
        print(f"No match found for the second chunk in {file_path}")
        return None  # If no match, skip this file

    ## Reformat for CSV export
    flattened_scores = {}
    for score in scores_data:
        index_name = score['index_name'].lower().replace(' ', '_').replace('(', '').replace(')', '')  # Clean up index name
        flattened_scores[f'{index_name}_raw_score'] = score['raw_score']
        flattened_scores[f'{index_name}_t_score'] = score['t_score']
        flattened_scores[f'{index_name}_percentile'] = score['percentile']
        flattened_scores[f'{index_name}_confidence_interval'] = score['confidence_interval']

    combined_data = {**first_chunk, **flattened_scores}
    return combined_data

# Function to write data to CSV
def write_to_csv(file_paths, output_csv):
    # Create an empty list to hold all data from all files
    all_data = []

    for file_path in file_paths:
        processed_data = process_rtf_file(file_path)
        if processed_data:
            all_data.append(processed_data)
    
    if all_data:
        # Get the header from the first processed file
        headers = all_data[0].keys()

        # Write the data to CSV
        with open(output_csv, mode='w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(all_data)

        print(f"Data successfully written to {output_csv}")
    else:
        print("No data to write to CSV.")

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Process RTF files and extract information to CSV.")
    parser.add_argument('rtf_directory', type=str, help="Path to the directory containing RTF files.")
    parser.add_argument('--output', type=str, default='processed_briefself_data.csv', help="Output CSV file name (default: 'processed_briefself_data.csv').")
    
    # Parse the command-line arguments
    args = parser.parse_args()

    # Get all RTF files from the directory
    rtf_files = [os.path.join(args.rtf_directory, file) for file in os.listdir(args.rtf_directory) if file.endswith('.rtf')]

    # Process all RTF files and write to CSV
    write_to_csv(rtf_files, args.output)
