#/bin/python3
import subprocess
import sys
import logging
from dwlabLoggerSetup import setup_logging
setup_logging()
logger=logging.getLogger(__name__)

def main():
    if len(sys.argv) < 2:
        logger.error("No parameters provided. Usage: dwlabbackup-tar.py <tar options>")
        sys.exit(1)

    # Build tar command dynamically
    tar_command = ["tar"] + sys.argv[1:]
    logger.info(f"Executing: {' '.join(tar_command)}")

    try:
        # Run tar command and capture output
        result = subprocess.run(
            tar_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,  # Ensures output is returned as a string
            check=True  # Raises exception if the command fails
        )

        # Log stdout and stderr
        if result.stdout:
            logger.info(f"tar stdout: {result.stdout.strip()}")
        if result.stderr:
            logger.warning(f"tar stderr: {result.stderr.strip()}")

    except subprocess.CalledProcessError as e:
        logger.error(f"tar failed with return code {e.returncode}")
        if e.stdout:
            logger.error(f"tar stdout: {e.stdout.strip()}")
        if e.stderr:
            logger.error(f"tar stderr: {e.stderr.strip()}")
        sys.exit(e.returncode)

    except FileNotFoundError:
        logger.critical("tar command not found. Ensure tar is installed and accessible.")
        sys.exit(127)

    except Exception as e:
        logger.exception(f"Unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
