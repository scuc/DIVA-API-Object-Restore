import logging
import logging.config
import os

from pathlib import Path

import config


config = config.get_config()
restore_dir = config["paths"]["restore_dir"]
checkin_dir = config["paths"]["checkin_dir"]


logger = logging.getLogger(__name__)


def obj_rename(fileName, objectName, folderPath):
    """
    Move a restored object out of the sub-dir tree and rename  with a proper file extension.
    """

    rename_msg = f"Begin obj rename and move for: {fileName} / {objectName}"
    logger.info(rename_msg)

    file_split = os.path.splitext(fileName)
    file_extension = file_split[1]
    newFileName = objectName + file_extension
    logger.info(f"New file extension: {file_extension}")
    logger.info(f"New file name: {newFileName}")

    source_path = Path(restore_dir, folderPath)
    dest_path = Path(checkin_dir, newFileName)

    # permissions.chmod_chown()

    source_path.replace(dest_path)
    logger.info(f"{objectName} renamed and moved to {dest_path}")

    return


if __name__ == "__main__":
    obj_rename(
        # fileName="056957_WONDERFULLYWEIRD_SUPERFREAKS_EM_WAV_20170216093000.zip",
        # objectName="FC15B4F7AB88-8000FFFF-FFFF-ECE8-39D0",
        # folderPath="/Volumes/Quantum2/DaletStorage/Gorilla_DIVA_Restore/mnt/lun02/Gorilla/RuriStorage/69/42/FC15B4F7AB88-8000FFFF-FFFF-ED3C-6942"
    )
