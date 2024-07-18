#!/bin/bash
CLUSTER=cluster-test
# Directory containing the YAML files
directory="DIRECTORY"
echo $directory
pager_email="PAGERDUTY@EMAIL.COM"
sre_email="SRE@EMAIL.COM"
# Loop through all YAML files in the directory
for file_path in "$directory"/*; 
do 
	# Check if the sre email exists in the email field
	sre_email_exists=$(yq eval '.email[]' "$file_path" | grep -iFx "$sre_email")
	if [ -z "$sre_email_exists" ]; then
		echo "The email '$sre_email' does not exist in the YAML file. No action taken."
	else
		# Check if the email already exists in the email field
		pager_email_exists=$(yq eval '.email[]' "$file_path" | grep -iFx "$pager_email")
		if [ -n "$pager_email_exists" ]; then
			echo "The email '$pager_email' already exists in the YAML file."
		else
			# Add the email to the email field
			yq eval '.email += ['\"$pager_email\"']' -i "$file_path" 
			sed -i 's/'$pager_email'/\"'$pager_email'\"/g' "$file_path"
			echo "The email '$pager_email' has been added to the YAML file."
		fi
	fi
done


### DELETE line containing old email
#sed -i '/OOOOLLLLDDDDD-EMAIL/d' *

