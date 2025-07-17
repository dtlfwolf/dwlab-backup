#!/bin/bash
#
#- Copyright:
#
# Company    = "DW-Lab GmbH"
# Department = "Central Services"
# Creation   = "01-Mar-2023"
# Version    = "1.0"
# Author     = "Detlef Wolf"
#
# Usage: bin/executeAllSteps.sh
#
# Description: Executes all numbered steps in this directory
#
# Parameters  :
#  <none>
#
# References  :
#       Name      Type      Short description
#      ------------------------------------------------------------
#       <none>
#
# Changes :
# 14-Feb-2024  D. Wolf       - Creation
#


thisScript=$0

echo 'DW-Lab: ************************************************************************************************************'
echo 'DW-Lab: '$thisScript

source dwlab_promptUser.sh

## Find out the directory path of the running script
## We expect the Images directory in relative path ./../../Images from the executed script
###############################################################################################################################
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

export DWLab_CONTROL_HOME=$DIR
echo "DW-Lab: DWLab_CONTROL_HOME=$DWLab_CONTROL_HOME"

SOURCE="$DWLab_CONTROL_HOME/../."
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

export DWLab_PackageHome=$DIR
echo "DWLab_PackageHome=$DWLab_PackageHome"


SOURCE="$DWLab_PackageHome/../."
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

export DWLab_EnvironmentHome=$DIR
echo "DWLab_EnvironmentHome=$DWLab_EnvironmentHome"
#


echo "DW-Lab: Read YAML file, containing runtime settings"
#
# Read YAML file, containing runtime settings
#
source "dwlab_bash_yaml.sh"
if [ $? != 0 ]
then
  echo "DW-Lab: *********************************************"
  echo "DW-Lab: $thisScript:"
  echo "DW-Lab: Cannot source file dwlab_bash_yaml.sh"
  echo "DW-Lab: Aborting"
  echo "DW-Lab: *********************************************"
  exit 1
fi
# create_variables "$DWLab_PackageHome/etc/dw-lab_InstallationSettings.yaml"
create_variables "$DWLab_PackageHome/etc/dw-lab_InstallationSettings.yaml"


echo "DW-Lab: ************************************************************************************"
echo "DW-Lab: ************************************************************************************"
echo "DW-Lab: ************************************************************************************"
echo "DW-Lab: $thisScript:"
echo "DW-Lab: We will now execute the following steps:"

# Check if the directory exists
if [ ! -d "$DWLab_CONTROL_HOME" ]; then
    echo "Directory not found: $DWLab_CONTROL_HOME"
    echo "DW-Lab: Aborting ...."
    exit 1
fi

# Step 1: Read all files in the directory into an array filtered by two digits at the beginning
filtered_files=()

while IFS= read -r -d '' file; do
    filename=$(basename "$file")
    if [[ $filename =~ ^[0-9]{2} ]]; then
        filtered_files+=("$filename")
    fi
done < <(find "$DWLab_CONTROL_HOME" -type f -print0)

# Step 2: List filtered files ordered by filename
sorted_files=($(printf '%s\n' "${filtered_files[@]}" | sort))

echo "DW-Lab: Do you really want to execute all of these steps?"
echo "DW-Lab: The following paramters have been read:"
echo "DW-Lab: dnsZone: $dnsZone"
echo "DW-Lab: dnsHostIP: $dnsHostIP"
echo "DW-Lab: dnsHostName: $dnsHostName"

for file in "${sorted_files[@]}"; do
    echo "DW-Lab: Steps to go - $file"
done
prompt_user
if [ $? != 0 ]
then
  echo "DW-Lab: *********************************************"
  echo "DW-Lab: $thisScript:"
  echo "DW-Lab: Terminating script execution on user request."
  echo "DW-Lab: *********************************************"
  exit 1
fi



# Step 3: Execute files again ordered by their name
echo "Executing files:"
for file in "${sorted_files[@]}"; do
    echo "DW-Lab: Executing $DWLab_CONTROL_HOME/$file:"
    $DWLab_CONTROL_HOME/$file
    if [ $? != 0 ]
    then
      echo "DW-Lab: *********************************************"
      echo "DW-Lab: $thisScript:"
      echo "DW-Lab: Cannot execute $file"
      echo "DW-Lab: Aborting"
      echo "DW-Lab: *********************************************"
      exit 1
    fi
done
exit 0
