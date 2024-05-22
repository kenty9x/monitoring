import json
import requests
import sys
import urllib3

# Disable SSL warnings
urllib3.disable_warnings()

arguments = sys.argv[1:]
# arguments[0]: help/import/export
# arguments[1]: domain, eg: abc.com
# arguments[2]: username eg: admin
# arguments[3]: password
# arguments[4]: rule-folder
# arguments[5]: json_file

if arguments[0] == "help":
    print("usage: <> import domain username password rule-folder json_file")
    print("       <> export domain username password rule-folder output_file")
    sys.exit()

grafana_url = "https://"+arguments[1]+"/monitoring/grafana"
username = arguments[2]
password = arguments[3]
folder = arguments[4]
json_file = ""

if len(arguments) > 5:
    json_file = arguments[5]

auth = (username, password)
alert_rule_url = f"{grafana_url}/api/ruler/grafana/api/v1/rules/{folder}"

if arguments[0] == "export":
    print("URL: ", alert_rule_url)
    alert_rule_response = requests.get(alert_rule_url, auth=auth)
    # TODO: add error handling
    print(f"{alert_rule_response.status_code}")
    data = json.loads(alert_rule_response.text)

    # delete uid
    for idx in range(len(data[folder])):
        for idx_rules in range(len(data[folder][idx]["rules"])):
            del data[folder][idx]["rules"][idx_rules]["grafana_alert"]["uid"]
        print(data[folder][0])

    file_name = arguments[1]+"-"+folder+".json"
    if json_file != "":
        file_name = json_file

    with open(file_name, 'w') as file:
        json.dump(data[folder], file, indent=4)  # Use indent to make the JSON file more readable
else:
    headers = {"Content-Type": "application/json"}

    with open(json_file, 'r') as file:
        data = json.load(file)

    print(headers)
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
