#!/bin/bash
#
#- Copyright:
#
# Company    = "DW-Lab GmbH"
# Department = "Central Services"
# Creation   = "04-Nov-2024"
# Version    = "1.0"
# Author     = "Detlef Wolf"
#
# Usage:  /etc/profile.d/dwlab_basicServices.sh
#
# Description:
#  makes the dwlab_basicservices available in the PATH environments
# Parameters  :
#  <none>
#
# References  :
#       Name      Type      Short description
#      ------------------------------------------------------------
#       <none>
#
# Changes :
# 04-Nov-2024  D. Wolf       - Creation
# 19-Nov-2024  D. Wolf       - Added dwlab_python_path
#
#

DWLAB_HOME="/opt/dwlab"
# shellcheck shell=sh
if [ ! -d "$DWLAB_HOME" ]; then
  echo "DW-Lab: The directory '$DWLAB_HOME' does not exist"
else
  export DWLAB_HOME
  # Expand $PATH to include the directory where DW-Lab application extensions go.
  dwlab_bin_path="$DWLAB_HOME/dwlab-backupclient/bin"

  if [ -d "$dwlab_bin_path" ]; then
    if [ -n "${PATH##*${dwlab_bin_path}}" ] && [ -n "${PATH##*${dwlab_bin_path}:*}" ]; then
        export PATH="$PATH:${dwlab_bin_path}"
    fi
  fi

  # Expand $PYTHONPATH to include the directory where DW-Lab application extensions go.
  dwlab_python_path="$DWLAB_HOME/dwlab-backupclient/src"
  if [ -d "$dwlab_python_path" ]; then
    if [ -n "${PYTHONPATH##*${dwlab_python_path}}" ] && [ -n "${PYTHONPATH##*${dwlab_python_path}:*}" ]; then
      export PYTHONPATH="$PYTHONPATH:${dwlab_python_path}"
    else
      if [ -z $PYTHONPATH ]; then
        export PYTHONPATH="${dwlab_python_path}"
      fi
    fi
  fi
fi

