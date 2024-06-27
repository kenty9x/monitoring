import json
import requests
import sys
import urllib3
import csv
import subprocess


def run_kubectl_command(command):
    """
    Run a kubectl command using subprocess and return the output.

    :param command: List of command arguments for kubectl
    :return: Output of the command
    """
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"


# Define the function to read, replace, and write text
def replace_strings_in_file(input_file_path, output_file_path, replacements):
    """
    Read text from input_file_path, replace specified strings, and save to output_file_path.

    :param input_file_path: Path to the input file
    :param output_file_path: Path to the output file
    :param replacements: Dictionary of strings to replace {old_string: new_string}
    """
    # Read text from the input file
    with open(input_file_path, 'r') as file:
        text = file.read()

    # Replace specified strings
    for old_string, new_string in replacements.items():
        text = text.replace(old_string, new_string)

    # Write the modified text to the output file
    with open(output_file_path, 'w') as file:
        file.write(text)

# Specify the input and output file paths
input_file_path = r'/GitHub/ELK-Alert/sample.yaml'

arguments = sys.argv[1:]

with open(arguments[0], newline='') as csvfile:
    csvreader = csv.DictReader(csvfile, delimiter=',')
    for row in csvreader:
        print(row)
        
        # Define the strings to replace
        replacements = {
            'LOG_IDENTIFIER_ABC_XYZ': row['logidentifier'],
            'CLUSTER_ABC_XYZ': row['cluster'],
            'QUERY_ABC_XYY': row['query'],
            'NAMESPACE_QUERY_ABC': row['query_namespace']
            # Add more replacements as needed
        }
        output_file_path = '/GitHub/ELK-Alert/ms-'+row['cluster']+'/'+row['logidentifier']+'.yaml'
        
        # Call the function to replace strings and save to a new file
        replace_strings_in_file(input_file_path, output_file_path, replacements)

        # Define the kubectl command
        kubectl_command = ['kubectl', '--kubeconfig', '/mnt/c/kubeconfig/eks-'+row['cluster']+'.yaml','cp', '-n', 'logging', output_file_path, 'elastalert-0:/opt/elastalert/rules/']

        # Run the command and get the output
        output = run_kubectl_command(kubectl_command)

        print(output)
