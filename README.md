This repo contains a series of python scripts that can be used to extract the summary score information from the Behavior Rating Inventory of Executive Function (BRIEF) data exports in .rtf format. These scripts encompass the following four BRIEF versions:

1. BRIEF-2 Self-Report (Youth version)
2. BRIEF-A Self-Report (Adult version)
3. BRIEF-2 Informant-Report (Youth version)
4. BRIEF-A Informant-Report (Adult version)

From a command line, usage of each of these scripts is as follows: 

`python {script_name}.py {/path/to/rtf_directory} {output_file}.csv`

Where `{script_name}` corresponds to one of these four scripts, `{/path/to/rtf_directory}` is the absolute file path to a directory with a list of BRIEF .rtf score reports, and `{output_file}` is whatever you want to name the resulting output.

I used these scripts to generate .csv files to upload to our data repository. My .rtf data existed in two separate directory locations: one that had a list of the self-report .rtfs, and one with a list of the informant-report .rtfs. The self-report youth script will miss all the adult versions of the self-report, but then you can just run the adult version of the script on the same directory and it'll miss all the youth versions and you'll end up with 2 outputs separated by age. I'm sure there's an elegant way to combine these into one or two scripts but I did not bother for this simple implementation. 
