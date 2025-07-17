#!/bin/bash
thisScript=$0

echo 'DW-Lab: ************************************************************************************************************'
echo 'DW-Lab: '$thisScript
scriptName=`basename $thisScript`
echo "DW-Lab: scriptName $scriptName"

source dwlab_installOSPackages.sh

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

# Check if the group exists
existing_group=$(getent group "$backupUserGroup")
existing_gid=$(getent group | awk -F: -v gid="$backupUserGID" '$3 == gid {print $1}')

if [[ -n "$existing_group" && -n "$existing_gid" ]]; then
    # Group name and GID both exist, check if they match
    existing_group_name=$(echo "$existing_group" | awk -F: '{print $1}')
    existing_group_gid=$(echo "$existing_group" | awk -F: '{print $3}')

    if [[ "$existing_group_name" == "$backupUserGroup" && "$existing_group_gid" == "$backupUserGID" ]]; then
        echo "DW-Lab: Group $backupUserGroup with GID $backupUserGID already exists, continuing."
    else
        echo "DW-Lab: Conflict -- Group name or GID mismatch."
        exit 8
    fi
elif [[ -z "$existing_group" && -z "$existing_gid" ]]; then
    # Neither group name nor GID exists, create the group
    echo "Creating group $backupUserGroup with GID $backupUserGID."
    sudo groupadd -g "$backupUserGID" "$backupUserGroup"
else
    # Conflict if either name or GID is already in use
    echo "Conflict: Either the group name or GID is already in use with different parameters."
    exit 8
fi

# Implement User definitions
dwlab_idInfo.sh --id $backupUser --format yaml >/tmp/"$scriptName.output.yaml" 2>>/dev/null
returnCode=$?
echo "DW-Lab: returnCode=$returnCode"
case "$returnCode" in
  "0") 
    echo "DW-Lab: The backup client user $backupUser already exists."
    create_variables /tmp/"$scriptName.output.yaml"
    if [ "$backupUserID" != "$user_id" ]
    then 
      echo "DW-Lab: The existing user does not have the correct ID number"
      echo "DW-Lab: Please verify."
      exit 8
    fi
    if [ "$backupUserGroup" != "$group_name" ]
    then 
      echo "DW-Lab: The existing user does not have the correct primary group"
      echo "DW-Lab: Please verify."
      exit 8
    fi
    if [ "$backupUserGID" != "$group_id" ]
    then 
      echo "DW-Lab: The existing $backupUserGroup does not have the correct GID"
      echo "DW-Lab: Please verify."
      exit 8
    fi
    ;;
  "4")
    echo "DW-Lab: Create Users Primary Group, if it dos not exist"
    # Check if the group exists
    existing_group=$(getent group "$backupUserGroup")
    existing_gid=$(getent group | awk -F: -v gid="$backupUserGID" '$3 == gid {print $1}')

    if [[ -n "$existing_group" && -n "$existing_gid" ]]; then
        # Group name and GID both exist, check if they match
        existing_group_name=$(echo "$existing_group" | awk -F: '{print $1}')
        existing_group_gid=$(echo "$existing_group" | awk -F: '{print $3}')

        if [[ "$existing_group_name" == "$backupUserGroup" && "$existing_group_gid" == "$backupUserGID" ]]; then
            echo "DW-Lab: Group $backupUserGroup with GID $backupUserGID already exists, continuing."
        else
            echo "DW-Lab: Conflict: Group name or GID mismatch."
            exit 8
        fi
    elif [[ -z "$existing_group" && -z "$existing_gid" ]]; then
        # Neither group name nor GID exists, create the group
        echo "DW-Lab: Creating group $backupUserGroup with GID $backupUserGID."
        sudo groupadd -g "$backupUserGID" "$backupUserGroup"
    else
        # Conflict if either name or GID is already in use
        echo "DW-Lab: Conflict: Either the group name or GID is already in use with different parameters."
        exit 8
    fi
    # Create user with home directory
    echo "DW-Lab: Creating user $backupUser"
    adduser --uid $backupUserID --gid $backupUserGID --system --shell /bin/bash --quiet --home /home/$backupUser $backupUser
    echo "DW-Lab: Adding ssh passkey"
    if [ "$backupUserLoginAuthorizedKey" != "" ]
    then
      sudo mkdir -p "/home/$backupUser/.ssh" &2>/dev/null
      if grep -qF "$backupUserLoginAuthorizedKey" /home/$backupUser/.ssh/authorized_keys
      then
        echo "DW-Lab: The entry for $backupUserLoginAuthorizedKey already exists in /etc/fstab."
      else
        echo "DW-Lab: Adding authorized ssh key to /home/$backupUser/.ssh/authorized_keys"
        echo "$backupUserLoginAuthorizedKey" | sudo tee -a "/home/$backupUser/.ssh/authorized_keys"
      fi
    else
      echo "DW-Lab: No authentication method for ssh login has been defined."
      echo "DW-Lab:   -- backupUserLoginAuthorizedKey : Please proved a authorized key."
    fi
    ;;
  "8")
    echo "DW-Lab: Programming is a tough job. Please try again..."
    $DWLab_Home/dwlab-basicServices/bin/dwlab_idInfo.sh --help
    exit 8
    ;;
  *)  
    echo "DW-Lab: Unknown return code from $DWLab_Home/dwlab-basicservices/bin/dwlab_idInfo.sh" >&2
    exit 8
    ;;
esac
# Adding user to sudo group
if id -nG "$backupUser" | grep -qw "sudo"
then
  echo "DW-Lab: $backupUser is already member of the group 'sudo'."
else
  echo "DW-Lab: Adding user '$backupUser'to sudo group"
  sudo usermod -aG sudo "$backupUser"
fi
# Adding user to syslog group
if id -nG "$backupUser" | grep -qw "syslog"
then
  echo "DW-Lab: $backupUser is already member of the group 'syslog'."
else
  echo "DW-Lab: Adding user '$backupUser'to syslog group"
  sudo usermod -aG syslog "$backupUser"
fi

exit 0
