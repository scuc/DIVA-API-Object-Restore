import logging
import logging.config
import os
import shutil

from pathlib import Path

import config


config = config.get_config()
restore_dir = config["paths"]["restore_dir"]
checkin_dir = config["paths"]["checkin_dir"]


logger = logging.getLogger(__name__)


def rename_object(fileName, objectName, folderPath):
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


def move_object(source_path, dest_path):
    """
    Move and object into a '_DONE' subdirectory, if a object with the same name already exists in this location, 
    append the file name. 
    """
    count = 0
    while True:
        try:
            if not Path(dest_path, source_path.name).exists():
                shutil.move(source_path, dest_path)
            if Path(dest_path, source_path.name).exists() and count < 5:
                count += 1
                source_name = source_path.name
                name_check = source_name.split("_")

                if len(name_check) == 1: 
                    new_source_name = source_name + f"_{count}"
                else: 
                    new_source_name = source_name[:-1] + str(int(source_name[-1:]) + 1)
                
                source_path = source_path.rename(
                        Path(source_path.parent, new_source_name)
                    )
                continue
            else:
                logger.info(
                    f"Too many copies of {source_path.name} exist in _DONE location."
                )
            return

        except Exception as e:
            logger.error(f"Error moving object: {e}")
            return


if __name__ == "__main__":
    move_object(
        # Path("/Users/cucos001/Desktop/Gorilla_CSV_WatchFolder/FC15B4F7AB88-80001000-0000-257D-6F2A.csv "), 
        # Path("/Users/cucos001/Desktop/Gorilla_CSV_WatchFolder/_DONE")
        # fileName="056957_WONDERFULLYWEIRD_SUPERFREAKS_EM_WAV_20170216093000.zip",
        # objectName="FC15B4F7AB88-8000FFFF-FFFF-ECE8-39D0",
        # folderPath="/Volumes/Quantum2/DaletStorage/Gorilla_DIVA_Restore/mnt/lun02/Gorilla/RuriStorage/69/42/FC15B4F7AB88-8000FFFF-FFFF-ED3C-6942"
    )
