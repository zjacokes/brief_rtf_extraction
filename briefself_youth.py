import re
import csv
import os
import argparse
from striprtf.striprtf import rtf_to_text

# Function to process necessary info from .rtf files
def process_rtf_file(file_path):
    with open(file_path) as infile:
        content = infile.read()

    rtf_text = rtf_to_text(content)

    # First regex chunk: patient info
    first_pattern = re.compile(
        r'Client\s*ID\s*:\s*\|(?P<client_id>[^\|]+)\|\s*'
        r'Gender\s*:\s*\|(?P<gender>[^\|]+)\|\s*'
        r'Age\s*:\s*\|(?P<age>[^\|]+)\|\s*'
        r'Grade\s*:\s*\|(?P<grade>[^\|]+)\|\s*'
        r'Test\s*date\s*:\s*\|(?P<test_date>[^\|]+)\|\s*'
        r'Language\s*administered\s*:\s*\|(?P<language>[^\|]+)\|\s*',
        re.IGNORECASE
    )

    first_match = first_pattern.search(rtf_text)

    if first_match:
        first_chunk = first_match.groupdict()
    else:
        print(f"No match found for the first chunk in {file_path}")
        return None  # skip if no match found
    
    # Second regex chunk: score info
    second_pattern = re.compile(
        r'Index/Scale\|Raw score\|T score\|Percentile\|90% CI\|\n'  # header
        r'(?P<scores>(?:[^\n]+\|\d+\|\d+\|\>? ?[\d]+\|[^\|]+\|\n)+)',  # match the rows; captures '>' and '> '
        re.IGNORECASE
    )

    second_match = second_pattern.search(rtf_text)

    if second_match:
        raw_scores = second_match.group('scores')
        scores_data = []
        for line in raw_scores.strip().split('\n'):
            parts = line.split('|')
            if len(parts) >= 5:
                percentile_value = parts[3].strip().replace('> ', '>').lstrip('>')  # removes '>' and handles any spaces
                score_info = {
                    'index_name': parts[0].strip(),
                    'raw_score': parts[1].strip(),
                    't_score': parts[2].strip(),
                    'percentile': percentile_value,
                    'confidence_interval': parts[4].strip()
                }
                scores_data.append(score_info)
    else:
        print(f"No match found for the second chunk in {file_path}")
        return None  # skip if no match found

    # Reformat for .csv file generation
    flattened_scores = {}
    for score in scores_data:
        index_name = score['index_name'].lower().replace(' ', '_').replace('(', '').replace(')', '')
        flattened_scores[f'{index_name}_raw_score'] = score['raw_score']
        flattened_scores[f'{index_name}_t_score'] = score['t_score']
        flattened_scores[f'{index_name}_percentile'] = score['percentile']
        flattened_scores[f'{index_name}_confidence_interval'] = score['confidence_interval']

    combined_data = {**first_chunk, **flattened_scores}
    return combined_data

# Write the extracted info to .csv
def write_to_csv(file_paths, output_csv):
    all_data = []

    for file_path in file_paths:
        processed_data = process_rtf_file(file_path)
        if processed_data:
            all_data.append(processed_data)
    
    if all_data:
        headers = all_data[0].keys()

        with open(output_csv, mode='w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(all_data)

        print(f"Data successfully written to {output_csv}")
    else:
        print("No data to write to csv.")

# argument parser
def main():
    parser = argparse.ArgumentParser(description="Process BRIEF Youth Self-Report .rtf files and extract data.")
    parser.add_argument('input_directory', help="Directory containing the .rtf files")
    parser.add_argument('output_csv', help="Name of the output .csv file")

    args = parser.parse_args()

    rtf_files = [os.path.join(args.input_directory, file) for file in os.listdir(args.input_directory) if file.endswith('.rtf')]

    write_to_csv(rtf_files, args.output_csv)

if __name__ == '__main__':
    main()
