#!/usr/bin/python3

import dwlab_backupClient
import sys
from pathlib import Path
import pprint

import logging
from dwlabLoggerSetup import setup_logging
setup_logging()
logger=logging.getLogger(__name__)

def main():
    # Find the directory path of the running script
    script_path = Path(__file__).resolve()

    returnCode=0
    try:
        backupClient=dwlab_backupClient.backupClient()
        packagesList=backupClient.listPackages(details=True)
    except Exception as e:
        logger.error("Cannot list backup packages.")
        returnCode=8

    pprint.pprint(packagesList,indent=4)
    return returnCode



if __name__ == "__main__":
    returnCode=main()
    sys.exit(returnCode)
