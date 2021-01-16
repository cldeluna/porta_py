#!/usr/bin/python -tt
# Project: dd_cisco_discovery
# Filename: txtfsm_ios_parsing
# claudia.deluna
# PyCharm
__author__ = "Claudia de Luna (claudia@indigowire.net)"
__version__ = ": 1.1 $"
__date__ = "1/11/2021"
__license__ = "Python"

import argparse
import datetime
import os
import sys
import csv
import re
import pandas as pd
import textfsm

# https://github.com/networktocode/ntc-templates/tree/master/templates


def filename_only(list_of_files):
    # Initialize empty list for filenames only
    fonly = []
    # for each file path in the list of files with full paths extract the filename only
    for fpath in list_of_files:
        head, tail = os.path.split(fpath)
        fonly.append(tail)
    # return the directory path and the list of filenames
    return head, fonly


def txtfsm_list_row_to_dict(row,table_header):

    return dict(zip(row, table_header))


def process_file(file, template):

    print("\tProcessing file with template {}".format(template))
    # open_file function returns a file handle
    fh = open_file(file, 'r')

    # Read the file contents into a variable for parsing
    file_contents = fh.read()
    # Close file
    fh.close()

    # Send TextFSM Template name and data to parse to text_fsm_parsing function
    # file_results returns the parsed results and table returns the header
    file_results, file_table = text_fsm_parse(template, file_contents)
    # print("file results of lenght {} from text_fsm_parse:\n{}".format(str(len(fil_results)),fil_results[1]))

    return file_results, file_table


def read_files_in_dir(dir, ext):

    valid_file_list = []

    try:
        dir_list = os.listdir(dir)
        # other code goes here, it iterates through the list of files in the directory

        for afile in dir_list:

            filename, file_ext = os.path.splitext(afile)
            #print filename, file_ext

            if file_ext.lower() in ext:
                afile_fullpath = os.path.join(dir,afile)
                valid_file_list.append(afile_fullpath)

    except WindowsError as winErr:

        print("Directory error: " + str((winErr)))
        print(sys.exit("Aborting Program Execution"))

    return valid_file_list, dir_list


def open_file(filename, mode):

    file_handle = ''
    # Mode = r | w | a | r+
    try:
        file_handle = open(filename, mode)

    except IOError:
        print("IOError" + str(IOError))
        print("Could not open file. Please make sure all result files are closed!")

    return file_handle


def text_fsm_parse(template_fn, data):

    # Run the text through the FSM.
    # The argument 'template' is a file handle and 'raw_text_data' is a
    # string with the content from the show_inventory.txt file
    template = open(template_fn)
    re_table = textfsm.TextFSM(template)
    fsm_results = re_table.ParseText(data)
    # print("in text_fsm_parse function")
    # print(type(fsm_results))
    # print(len(fsm_results))


    return fsm_results, re_table


def load_shcmd_lines(filepath):
    """
    Read file into list of lines
    :param filepath:
    :return:
    """

    with open(filepath, "r") as f:
        file_contents = f.readlines()
    # print(len(file_contents))
    # print(file_contents)
    return file_contents


def get_show_section(lines_of_text, start_string, end_string, debug=False):
    """
    Given a file of many show commands, extract out a specific section

    :param lines_of_text:
    :param start_string:
    :param end_string:
    :param debug:
    :return:
    """

    shrun_lines = []
    in_show = False
    for line in lines_of_text:

        if re.search(start_string, line):
            in_show = True
            # print(start_string)
            # print(line)

        if in_show:
            shrun_lines.append(line)
            # print(line)

        if re.search(end_string, line):
            # print(end_string)
            # print(line)
            in_show = False

    if len(shrun_lines) > 0:
        shrun_lines.pop()

    if debug:
        print(f"From get_show_section Function:")
        print(shrun_lines)
        print(len(shrun_lines))
    return list_to_str(shrun_lines)


def list_to_str(list_of_lines, debug=False):
    """
    Used when a file is read in via readlines() resulting in a list of lines
    and you need to put it back into a single string variable
    Typically used with CiscoConfParse

    Example:
    parsed = ciscoconfparse.CiscoConfParse(save_file("temp_text.txt", text_output))

    :param list_of_lines:
    :param debug:
    :return:
    """
    # ciscoconfparse wants a file so we have to rebuild the text in text_output and pass the parse command a file
    text_output = ""
    for line in list_of_lines:
        text_output = text_output + line
    if debug: print(text_output)

    return text_output


def search_string_dict(template_name):

    search_string = {
        "cisco_ios_show_interfaces" : {
            "start": r"sh(ow)? int(erfaces)?",
            "end": r" sh(ow)? int(erface)? status"
        },
        "cisco_ios_show_etherchannel_summary": {
            "start": r"sh(ow)? ether(channel)? sum(mary)?",
            "end": r" sh(ow)? vrf"
        }

    }

    ss_dict = {}
    if template_name in search_string.keys():
        ss_dict = search_string[template_name]
    else:
        print(f"WARNING: Start and End RegEx for {template_name} have not been set!")

    return ss_dict



def main():

    # Timestamp the start of the run so that a total run time can be calculated at the end
    start_time = datetime.datetime.now()

    # Keep a list of any files that did not have any output information
    no_output = []

    # Mandatory argument passed to script - either a filename or a directory of files to process
    path = arguments.filename_or_dir
    textfsm_template = arguments.fsm_template

    #Get the absolute path

    table = False

    # Get the template name without the file extension
    abs_templ_path = os.path.abspath(arguments.fsm_template)
    abs_templ_dir, abs_templ_filename = os.path.split(abs_templ_path)
    # print(f"absolute template dir {abs_templ_dir} and filename {abs_templ_filename}")

    textfsm_name, textfsm_ext = os.path.splitext(abs_templ_filename)
    # print(f"filename {textfsm_name} and ext {textfsm_ext}")

    start_end_dict = search_string_dict(textfsm_name)

    # Initialize list of all valid files
    # The script will always process a list. If a single filename was provided it will be a list with a single element
    file_list = []

    # Initialize list of valid parsing results
    fsm_all_results = []

    valid_file_extenstion = []
    if arguments.extension:
        extensions = arguments.extension
        extensions = re.sub(r'\s+', '', extensions)
        extensions = re.split(r'[;|,|\s]?', extensions)

        for ext in extensions:
            valid_file_extenstion.append(ext)
    else:
        valid_file_extenstion.append(".txt")
        valid_file_extenstion.append(".log")

    # Check to see if the path or file provided exists
    if os.path.exists(path):
        # Check to see if the argument is a directory
        if os.path.isdir(path):
            print("Processing Directory: " + path + " for all files with the following extensions: " + str(valid_file_extenstion))
            file_list, total_files = read_files_in_dir(path, valid_file_extenstion)
            print("\t Total files in directory: " + str(len(total_files)))
            print("\t Valid files in directory: " + str(len(file_list)))

            path_list = os.path.basename(path)
            results_fn = f"{path_list}_{textfsm_name}_results"
            abs_results_dir = path
            results_num_files = str(len(file_list))

        else:
            print("Processing File: " + path)
            file_list.append(path)
            fn, fext = os.path.splitext(path)
            results_fn = f"{fn}_{textfsm_name}_results"
            curr_dir = os.getcwd()
            abs_path = os.path.abspath(path)
            abs_dir, abs_filename = os.path.split(abs_path)
            abs_results_dir = abs_dir
            results_num_files = '1'

    else:
        print("Problem with path or filename! {}".format(path))
        sys.exit("Aborting Program Execution due to bad file or directory argument.")

    # Make sure we have files to process (at least 1)
    if len(file_list) > 0:

        # Open the CSV file to store results
        # csv_results_fh = open_file(results_dir, 'wb')
        # csv_writer = csv.writer(csv_results_fh, quoting=csv.QUOTE_MINIMAL)

        # Iterate through the valid file list. If the script was passed a filename it will be a file_list of 1
        # If the script was passed a directory it will be a list of files with a valid extension
        for fil in file_list:



            # Process entire file

            try:
                print(f"Processing unfiltered device file: {fil}")
                # Read the file contents into a variable for parsing
                with open(fil, "r") as f:
                    file_contents = f.read()

                # Send TextFSM Template name and data to parse to text_fsm_parsing function
                # file_results returns the parsed results and table returns the header
                fil_results, table = text_fsm_parse(textfsm_template, file_contents)
                # print("file results of length {} from text_fsm_parse:\n{}".format(str(len(fil_results)),fil_results[1]))

            except textfsm.parser.TextFSMError:
                print(f"Processing device file section: {fil}")
                # textfsm.parser.TextFSMError: State Error raised. Rule Line: 29. Input Line: !--- show vrf
                # Process section

                # Read the file contents into a list for section extraction
                all_file_contents = load_shcmd_lines(fil)

                file_contents = get_show_section(all_file_contents, start_end_dict['start'], start_end_dict['end'])

                # Send TextFSM Template name and data to parse to text_fsm_parsing function
                # file_results returns the parsed results and table returns the header
                fil_results, table = text_fsm_parse(textfsm_template, file_contents)
                # print("file results of length {} from text_fsm_parse:\n{}".format(str(len(fil_results)),fil_results[1]))

            print("Parsing Results")
            # print(fil_results)
            # print(type(fil_results))
            # print("Table headers")
            # print(table.header)
            # print(table._result)
            # print(dir(table))

            # Keep track of files without parser output in the no_output list so it can be printed later
            if len(fil_results) == 0:
                no_output.append(fil)
            else:
                # Append fil_results list of results to list of all results
                fsm_all_results.append(fil_results)

        df = pd.DataFrame.from_records(fsm_all_results[0], columns=table.header)

        print(df.head())
        # print(df['MEDIA_TYPE'])

        # media_df = df[['INTERFACE', 'LINK_STATUS', 'MEDIA_TYPE']]
        # print(media_df)

        # Summary Information
        print("\n")
        print("-" * 60)
        print("-" * 60)
        print(f"Number of files processed: {results_num_files}")

        if len(no_output) > 0:
            print(f"Number of files/devices without parser results: {str(len(no_output))}")
            print("List of files/devices without parser results: ")
            for file in no_output:
                print(f"\t{str(file)}")
        else:
            print(f"All {results_num_files} files/devices had parser results.")

        # Save results to CSV and JSON files
        res_csv = os.path.join(abs_results_dir,f"{results_fn}.csv")
        res_json = os.path.join(abs_results_dir,f"{results_fn}.json")
        df.to_csv(res_csv, index=False)
        df.to_json(res_json)
        print(f"\nCSV Results file created in:\n\t{res_csv}")
        print(f"\nJSON Results file created in:\n\t{res_json}")

        elapsed_time = datetime.datetime.now() - start_time
        msg = "Elapsed time: {}".format(elapsed_time)
        print("-" * 60)
        print(msg)
        print("-" * 60)

        # csv_results_fh.close()
    else:
        print("No valid files to process in directory.")


# Standard call to the main() function.
if __name__ == '__main__':
    # Standard call to the main() function.
    if __name__ == '__main__':
        parser = argparse.ArgumentParser(description='TextFSM parser script to parse a single file or a '
                                                     'directory of files with a given extension.',
                                         epilog='Usage: python txtfsm_ios_parsing.py '
                                                '<filename or directory of files to parse> '
                                                '<TextFSM Template file> (Optional -e ".fil")')

        parser.add_argument('filename_or_dir', help='filename or directory of files to parse')
        parser.add_argument('fsm_template', help='TextFSM template to use for parsing')

        parser.add_argument('-e', '--extension', action='store', default=False, help='Valid file extension in format '
                                                                                     '".xxx" or comma delimited '
                                                                                     '".txt, .fil" Default values if '
                                                                                     'option not give are .txt and .log')

        arguments = parser.parse_args()

        main()


