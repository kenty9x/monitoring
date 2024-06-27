import csv
import json
import requests
import sys
import urllib3

def write_output(output_file_path, host_name, link, service_description, http_or_https):   
    host_found = False
    with open(output_file_path) as output_file:
        if host_name in output_file.read():
            print('Found host')
            host_found = True
    if not host_found:
        with open(output_file_path, mode='r') as output_file:
            data = output_file.read()
        with open(output_file_path, mode='w') as output_file:        
            output_file.write(f"""
define host {{
    use                     linux-server            ; Name of service template to use
    host_name               {host_name}
    alias                   {host_name}
    address                 10.210.96.5
}}
            """)
            output_file.write(data)

    link_found = False
    with open(output_file_path) as output_file:
        if link in output_file.read():
            print('Found Link')
            host_found = True
    if not link_found:
        if http_or_https == "https":
            with open(output_file_path, mode='a') as output_file:        
                output_file.write(f"""
define service {{
    use                     generic-service            ; Name of service template to use
    host_name               {host_name}
    service_description     {service_description}
    check_command           check_https_direct_ssl!{link}
    contact_groups          support_team
    notes                   {link}
}}
        """)
        elif http_or_https == "http":
            with open(output_file_path, mode='a') as output_file:        
                output_file.write(f"""
define service {{
    use                     generic-service            ; Name of service template to use
    host_name               {host_name}
    service_description     {service_description}
    check_command           check_http_direct!{link}
    contact_groups          support_team
    notes                   {link}
}}
        """)

arguments = sys.argv[1:]
folder_path = r'' ### Add path

with open(arguments[0], newline='') as csvfile:
    csvreader = csv.DictReader(csvfile, delimiter=',')
    for row in csvreader:
        print(row)
        
        link = row['link']
        link_list = link.split("/")
        http_or_https = link_list[0][:-1]
        host = link_list[2]
        file_path = folder_path+row['env']+"/"+row['filename']+".cfg"
        write_output(file_path, host,link,row['servicedescription'], http_or_https)


print(f"Service definitions written!")
