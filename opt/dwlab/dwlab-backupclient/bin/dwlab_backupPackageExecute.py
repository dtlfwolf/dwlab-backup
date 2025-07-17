#!/usr/bin/python3

import dwlab_backupClient
import sys
import os
import pwd
from pathlib import Path

import logging
from dwlabLoggerSetup import setup_logging
setup_logging()
logger=logging.getLogger(__name__)

def main():
    # Find the directory path of the running script
    script_path = Path(__file__).resolve()

    if len(sys.argv) > 1:
        backupPackageName=sys.argv[1]
    else:
        logger.error("Missing parameter")
        logger.error("Usage:")
        logger.error(str(script_path)+" <backupPackageName>")
        sys.exit(8)

    returnCode=0
    try:
        backupClient=dwlab_backupClient.backupClient()
        returnCode=backupClient.executePackage(packageName=backupPackageName)
    except PermissionError as e:
        logger.warning("Trying to switch user context to "+backupClient.backupUser)
        try:
            os.setuid(pwd.getpwnam(backupClient.backupUser).pw_uid)
            returnCode=backupClient.executePackage(packageName=backupPackageName)
        except Exception as e:
            logger.error("Cannot execute backup for package "+str(backupPackageName)+".") 
            logger.error(e)
            returnCode=8
    except Exception as e:
        logger.error("General Error while executing backup for package "+str(backupPackageName)+".")
        returnCode=8

    return returnCode

if __name__ == "__main__":
    returnCode=main()
    sys.exit(returnCode)
