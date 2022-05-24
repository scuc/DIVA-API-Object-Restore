import logging
import os
import subprocess

import config

config = config.get_config()
# script_root = config['paths']['script_root']
restore_path = config["paths"]["restore_dir"]

logger = logging.getLogger(__name__)


def chmod_chown():
    error = False
    start_msg = f"\n\n=========================== START PERMISSIONS FIX ==========================="
    logger.info(start_msg)

    try:
        # os.chdir(script_root)
        capturedoutput = subprocess.run(
            ["sudo", "./permissions_fix.sh", restore_path],
            shell=False,
            capture_output=True,
            universal_newlines=True,
            check=True,
            timeout=120,
            bufsize=100,
        )
        logger.info(f"\n\\ {capturedoutput} \n\\ ")

    except Exception as e:
        perm_err_msg = f"Error on file permissions subprocess: \n {e}"
        logger.error(perm_err_msg)
        error = True

    end_msg = f"\n=========================== END PERMISSIONS FIX ===========================\n"
    logger.info(end_msg)
    return


if __name__ == "__main__":
    chmod_chown()
