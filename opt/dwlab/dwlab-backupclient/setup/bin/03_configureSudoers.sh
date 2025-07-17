#!/bin/bash
thisScript=$0

echo 'DW-Lab: ************************************************************************************************************'
echo 'DW-Lab: '$thisScript
scriptName=`basename $thisScript`
echo "DW-Lab: scriptName $scriptName"

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

# Read the client settings
create_variables "$DWLab_PackageHome/etc/dwlabBackupClientSettings.yaml"

# Exchange placeholder __backupUser in /etc/sudoers.d/dwlab-backup-user
sed -i "s/__backupUser/$backupUser/g" /etc/sudoers.d/dwlab-backup-user
if [ $? != 0 ]
then
  echo 'DW-Lab: *********************************************'
  echo 'DW-Lab: '$thisScript':'
  echo "DW-Lab: Cannot replace placeholder __backupUser in /etc/sudoers.d/dwlab-backup-user"
  echo 'DW-Lab: Aborting'
  echo 'DW-Lab: *********************************************'
  exit 8
fi
exit 0
