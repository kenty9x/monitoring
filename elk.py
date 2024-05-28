import yaml
import csv
import os

# Function to extract the required fields from the YAML content
def extract_fields(subfolder_name, yaml_content):
    name = yaml_content.get('name')
    query_string = yaml_content['filter'][0]['query']['query_string']['query']
    emails = yaml_content['email']
    
    return {
        'folder_name': subfolder_name,
        'name': name,
        'query_string': query_string,
        'emails': emails
    }


# Folder containing the YAML files
base_folder_path = 'folder-path'

# Prepare to collect data from all YAML files
all_fields = []

# Process each subfolder and its YAML files
for subfolder_name in os.listdir(base_folder_path):
    subfolder_path = os.path.join(base_folder_path, subfolder_name)
    if os.path.isdir(subfolder_path):
        for filename in os.listdir(subfolder_path):
            if filename.endswith('.yaml'):
                file_path = os.path.join(subfolder_path, filename)
                with open(file_path, 'r') as file:
                    yaml_content = yaml.safe_load(file)
                    fields = extract_fields(subfolder_name, yaml_content)
                    all_fields.append(fields)

# Write to CSV file
csv_file_path = 'output.csv'
with open(csv_file_path, 'w', newline='') as csvfile:
    fieldnames = ['folder_name', 'name', 'query_string', 'email']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for fields in all_fields:
        writer.writerow({
                'folder_name': fields['folder_name'],
                'name': fields['name'],
                'query_string': fields['query_string'],
                'email': fields['emails']
            })    

print(f"Data has been written to {csv_file_path}")
