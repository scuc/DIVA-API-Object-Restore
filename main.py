#! /usr/bin/env python3

import csv
import logging
import logging.config
import os
import shutil
import sys
import yaml

from datetime import date, datetime
from pathlib import Path
from time import localtime, strftime

import config
import api_DIVA as api
import object_rename as obj

config = config.get_config()


# script_root = config["paths"]["script_root"]
csv_watchfolder = config["paths"]["csv_watch_folder"]


logger = logging.getLogger(__name__)


def set_logger():
    """
    Setup logging configuration
    """
    path = "./logging.yaml"

    with open(path, "rt") as f:
        config = yaml.safe_load(f.read())

        # get the file name from the handlers, append the date to the filename.
        for i in config["handlers"].keys():
            local_datetime = str(strftime("%A, %d. %B %Y %I:%M%p", localtime()))

            if "filename" in config["handlers"][i]:
                log_filename = config["handlers"][i]["filename"]
                base, extension = os.path.splitext(log_filename)
                today = datetime.today()

                log_filename = "{}_{}{}".format(
                    base, today.strftime("%Y%m%d%H%M%S"), extension
                )
                config["handlers"][i]["filename"] = log_filename
            else:
                continue

        logger = logging.config.dictConfig(config)

    return logger


def main():

    """
    This script will restore object from DIVAArchive. The script is trigged from an external workflow from the Dalet Galazy BPM.
    The workflow from Dalet provides the ObjectName, FileName, and Folderpath information stored in DIVA. It uses DIVA's REST api to
    chedk the object info, and initiate a restore. Once the restore is started it will periodically check the status of the restore
    job until the object is completely restored. From there it moves the object to a watch folder, and adds the appropraite
    file extension.
    """

    date_start = str(strftime("%A, %d. %B %Y %I:%M%p", localtime()))

    csv_list = [
        x
        for x in os.listdir(csv_watchfolder)
        if x.endswith(".csv") and not x.startswith(".")
    ]

    if len(csv_list) != 0:

        for csvfile in csv_list:
            csvfile_path = Path(csv_watchfolder, csvfile)
            with open(csvfile_path) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    print(row)
                    objectName = row["objectName"]
                    fileName = row["fileName"]
                    folderPath = row["folderPath"]

                    start_msg = f"\n\
                    ================================================================\n\
                        ObjectName: {objectName}\n\
                        FileName: {fileName} \n\
                        FolderPath: {folderPath} \n\
                        StartTime: {date_start}\n\
                    ================================================================\n\
                    "

                    logger.info(start_msg)

            shutil.move(csvfile_path, Path(csv_watchfolder, "_DONE"))

    else:
        logger.info(date_start)
        return

    # except Exception as e:
    #     logger.error(f"Error - Missing required variables.")
    #     logger.error(e)
    #     complete_message(objectName, fileName)
    #     return

    statusCode, collectionName, instance = api.get_obj_info(objectName)

    if statusCode == 200:
        restore_statusCode, requestId, statusDescription = api.api_obj_restore(
            objectName, collectionName, instance
        )

        if restore_statusCode == 1000 and statusDescription == "success":

            jobStatus = api.api_status_request(objectName, requestId)

            if (
                jobStatus["progress"] == 100
                and jobStatus["statusDescription"] == "success"
            ):
                obj.obj_rename(fileName, objectName, folderPath)
            else:
                logger.info(f"Object restore incomplete.")

        else:
            restore_msg = f"Restore Status = {restore_statusCode}, RestoreDescription = {statusDescription}\n exiting restore"

    else:
        logger.info(f"statusCode: {statusCode} - unable to locate object in DIVA")

    complete_message(objectName, fileName)


def complete_message(objectName, fileName):
    date_end = str(strftime("%A, %d. %B %Y %I:%M%p", localtime()))

    complete_msg = f"\n\
    ================================================================\n\
                ObjectName: {objectName}\n\
                FileName: {fileName}\n\
                 EndTime: {date_end}\n\
    ================================================================\n\
    "
    logger.info(complete_msg)
    return


if __name__ == "__main__":
    set_logger()
    main()
    # main(args=[
    #             "FC15B4F7AB88-80001000-0000-4088-AD86",
    #             "059977_WICKEDTUNA7_THEFLEETSTRIKESBACK_PTS_20190314145000.zip",
    #             "mnt/lun02/Gorilla/RuriStorage/15/D8/FC15B4F7AB88-80001000-0000-40B5-15D8"
    #             ])
