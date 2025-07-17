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

echo "DW-Lab: Define Mount point -- if required and not used in any other way (have to be an empty directory)"
if [ -d "$backupMountPoint" ]
then
  # Check if directory is a mount point
  if mountpoint -q "$backupMountPoint" 
  then
    echo "DW-Lab: $backupMountPoint is an active mount point."
  else
    # Check if the directory is empty
    if [ -z "$(ls -A "$backupMountPoint")" ]
    then
        echo "DW-Lab: $backupMountPoint is empty."
    else
      echo "DW-Lab: $backupMountPoint is not empty."
      if [ $backupMountType != "local" ]
      then
        echo "DW-Lab: Please review the content of this directory befor adding new data."
        exit 8
      fi
    fi
  fi
else
  sudo mkdir -p "$backupMountPoint"
fi
case "$backupMountType" in
  "local")
    echo "DW-Lab: You defined a backup type "local" (backupMountPoint=local)"
    echo "DW-Lab: Your machine backup data will remain on the local system."
    echo "DW-Lab: In an event of a local desaster all data might be lost."
    echo "DW-Lab: Implement additional mechanisms (from outside) to avoid data loss."
    ;;
  "nfs")
    # Define the entry line for the NFS mount in /etc/fstab
    fstab_entry="$backupRemoteHost:$backupRemoteDir $backupMountPoint nfs defaults 0 0"
    # Check if the entry already exists in /etc/fstab
    if grep -qF "$fstab_entry" /etc/fstab
    then
      echo "The entry for $backupRemoteHost:$backupRemoteDir already exists in /etc/fstab."
    else
      # Append the NFS mount entry to /etc/fstab
      echo "Adding NFS entry to /etc/fstab."
      echo "$fstab_entry" | sudo tee -a /etc/fstab
      # Optional: mount the directory immediately
      sudo mount -a
      if [ $? == "0" ]
      then
        echo "DW-Lab: Mount completed."
      else
        echo "DW-Lab: Cannot mount $fstab_entry"
        exit 8
      fi
    fi    
    ;;
  "smb")
    credentialsFile="$DWLab_PackageHome/etc/backup-credentials.smb"

    # Define the entry line for the SMB mount in /etc/fstab
    fstab_entry="//$backupRemoteHost/$backupRemoteDir $backupMountPoint cifs credentials=$credentialsFile,iocharset=utf8,vers=3.0 0 0"

    # Check if the entry already exists in /etc/fstab
    if grep -qF "$fstab_entry" /etc/fstab
    then
      echo "DW-Lab: The entry for //$backupRemoteHost/$backupRemoteDir already exists in /etc/fstab."
    else
      # Create credentials file if it doesn't exist
      if [ ! -f "$credentialsFile" ]
      then
        echo "DW-Lab: Creating credentials file at $credentialsFile."
        sudo bash -c "echo 'username=$backupFileServerUser' > $credentialsFile"
        sudo bash -c "echo 'password=$backupFileServerPassword' >> $credentialsFile"
        sudo chmod 600 "$credentialsFile" # Restrict permissions to protect credentials
      fi
      # Append the SMB mount entry to /etc/fstab
      echo "Adding SMB entry to /etc/fstab."
      echo "$fstab_entry" | sudo tee -a /etc/fstab
      # Optional: mount the directory immediately
      sudo mount -a
      if [ $? == "0"]
      then
        echo "DW-Lab: Mount completed."
      else
        echo "DW-Lab: Cannot mount $fstab_entry"
        exit 8
      fi
    fi
    ;;
  "nfs4")
    echo "DW-Lab: This DW-Lab backup client does not support a mount type nfs4. Work is in progress ..."
    ;;
  *)
    echo "DW-Lab: This kind of mount type for the DW-Lab backup client is not supported"
    ;;
esac
exit 0
