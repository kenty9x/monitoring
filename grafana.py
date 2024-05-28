import json
import requests
import sys
import urllib3
import csv

# Disable SSL warnings
urllib3.disable_warnings()

def import_rule(grafana_url, headers, auth, json_file, folder):
    with open(json_file, 'r') as file:
        data = json.load(file)

    print("File data:")
    print(data)
    print(f"ensuring folder {folder} exists")
    r = requests.post(f"{grafana_url}/api/folders", data=f'{{"title": "{folder}"}}'.encode('utf-8'), headers=headers, verify=False, auth=auth)
    print(f"{r.status_code} - {r.content}")

    print(f"uploading AlertGroup to folder {folder}")
    for idx in range(len(data)):
        print(data[idx])
        r = requests.post(f"{grafana_url}/api/ruler/grafana/api/v1/rules/{folder}", data=json.dumps(data[idx]).encode('utf-8'), headers=headers, verify=False, auth=auth)
        # TODO: add error handling
        print(f"{r.status_code} - {r.content}")


arguments = sys.argv[1:]
# arguments[0]: help/import/export
# arguments[1]: domain, eg: ms-prod-wf-app.cccis.com
# arguments[2]: username eg: admin
# arguments[3]: password
# arguments[4]: rule-folder
# arguments[5]: json_file

if arguments[0] == "help":
    print("usage: <> import-rule domain username password rule-folder json_file")
    print("       <> export-rule domain username password rule-folder output_file")
    print("       <> import-contact domain username password json_file")
    print("       <> export-contact domain username password output_file")

    sys.exit()

grafana_url = "https://"+arguments[1]+"/monitoring/grafana"
username = ""
password = ""
folder = ""

if arguments[0] != "import-file":
    username = arguments[2]
    password = arguments[3]

if len(arguments) > 4:
    folder = arguments[4]

json_file = ""

if len(arguments) > 5:
    json_file = arguments[5]

auth = (username, password)
headers = {"Content-Type": "application/json"}

if arguments[0] == "export-rule":
    alert_rule_url = f"{grafana_url}/api/ruler/grafana/api/v1/rules/{folder}"
    print("URL: ", alert_rule_url)
    alert_rule_response = requests.get(alert_rule_url, auth=auth)
    # TODO: add error handling
    print(f"{alert_rule_response.status_code}")
    data = json.loads(alert_rule_response.text)

    # delete uid
    for idx in range(len(data[folder])):
        for idx_rules in range(len(data[folder][idx]["rules"])):
            del data[folder][idx]["rules"][idx_rules]["grafana_alert"]["uid"]
            if "runbook_url" in data[folder][idx]["rules"][idx_rules]["annotations"]:
                del data[folder][idx]["rules"][idx_rules]["annotations"]["runbook_url"]
        print(data[folder][0])

    file_name = arguments[1]+"-"+folder+".json"
    if json_file != "":
        file_name = json_file

    with open(file_name, 'w') as file:
        json.dump(data[folder], file, indent=4)  # Use indent to make the JSON file more readable
elif arguments[0] == "import-rule":
    import_rule(grafana_url, headers, auth, json_file, folder)

elif arguments[0] == "export-contact":
    contact_url = f"{grafana_url}/api/alertmanager/grafana/config/api/v1/alerts"
    print("URL: ", contact_url)
    contact_response = requests.get(contact_url, auth=auth)
    # TODO: add error handling
    print(f"{contact_response.status_code}")
    data = json.loads(contact_response.text)

    # delete uid
    for idx in range(len(data["alertmanager_config"]["receivers"])):
        if "grafana_managed_receiver_configs" in data["alertmanager_config"]["receivers"][idx]:
            for idx2 in range(len(data["alertmanager_config"]["receivers"][idx]["grafana_managed_receiver_configs"])):
                if "uid" in data["alertmanager_config"]["receivers"][idx]["grafana_managed_receiver_configs"][idx2]:
                    del data["alertmanager_config"]["receivers"][idx]["grafana_managed_receiver_configs"][idx2]["uid"]
    print(data)

    file_name = arguments[1]+"-contact-points.json"
    if json_file != "":
        file_name = json_file

    with open(file_name, 'w') as file:
        json.dump(data, file, indent=4)  # Use indent to make the JSON file more readable

elif arguments[0] == "import-contact":
    json_file = arguments[-1]
    contact_url = f"{grafana_url}/api/alertmanager/grafana/config/api/v1/alerts"
    with open(json_file, 'r') as file:
        data = json.load(file)

    print("File data:")
    print(data)
    print(f"uploading Contact Points")
    r = requests.post(contact_url, data=json.dumps(data).encode('utf-8'), headers=headers, verify=False, auth=auth)
    print(f"{r.status_code} - {r.content}")

elif arguments[0] == "import-file":
    with open(arguments[1], newline='') as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter=',')
        for row in csvreader:
            print(row)
            auth = (row["username"], row["password"])
            grafana_url = "https://"+row["domain"]+"/monitoring/grafana"
            import_rule(grafana_url,headers, auth, row["file_json"], row["folder"])
