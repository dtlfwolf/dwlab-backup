#!/bin/bash

thisScript=$0

echo 'DW-Lab: ************************************************************************************************************'
echo 'DW-Lab: '$thisScript


###############################################################################################################################
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
#

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
  echo 'DW-Lab: *********************************************'
  echo 'DW-Lab: '$thisScript':'
  echo "DW-Lab: Cannot source file dwlab_bash_yaml.sh"
  echo 'DW-Lab: Aborting'
  echo 'DW-Lab: *********************************************'
  exit 8
fi
create_variables "$DWLab_PackageHome/etc/dwlabBackupClientSettings.yaml"


# Copy the installation settings
cp $DWLab_PackageHome/etc/dwlabBackupClientSettings.yaml $DWLab_EnvironmentHome/etc/dwlabBackupClientSettings.yaml
if [ $? != 0 ]
then
  echo 'DW-Lab: *********************************************'
  echo 'DW-Lab: '$thisScript':'
  echo "DW-Lab: Cannot copy installationm settings to runtime environment."
  echo 'DW-Lab: Aborting'
  echo 'DW-Lab: *********************************************'
  exit 8
fi

find $DWLab_EnvironmentHome -type f -exec chmod 750 {} \;

find $DWLab_EnvironmentHome -type f -name '*.sh' -exec chmod +x {} \;
find $DWLab_EnvironmentHome -type f -name '*.py' -exec chmod +x {} \;


echo "DW-Lab: Success "$DWLab_PackageHome
echo "DW-Lab: Backup Client is now fully implemented"
exit 0
