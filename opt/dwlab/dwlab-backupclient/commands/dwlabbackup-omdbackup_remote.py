#/bin/python3
import argparse
import subprocess
import sys
import logging
from dwlabLoggerSetup import setup_logging
setup_logging()
logger=logging.getLogger(__name__)

def main():
    # Create Argument Parser
    parser=argparse.ArgumentParser(description="Backup OMD Instance")

    # Define named arguments
    parser.add_argument("--omdRemoteHost", required=True, help="OMD Remote Host")
    parser.add_argument("--omdInstance", required=True, help="OMD Instance Name")
    parser.add_argument("--backupFile", required=True, help="Full qualified filename, the is written to")

    # Parse arguments
    args = parser.parse_args()
    try:
        backupCommand="'omd backup "+str(args.omdInstance)+" -'"
        subprocess.run(
            [
                "ssh", args.omdRemoteHost,
                backupCommand,
                "> "+args.backupFile
            ],
            capture_output=True,
            check=True
        )
        logger.info("OMD Backup successful for OMD Instance "+args.omdInstance+" on "+args.omdRemoteHost)
        returnCode=0
    except Exception as e:
        logger.error("OMD Backup failed for OMD Instance "+args.omdInstance+" on "+args.omdRemoteHost)  
        logger.error(e)
        returnCode=8
    
    sys.exit(returnCode)


