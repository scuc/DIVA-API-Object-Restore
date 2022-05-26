#! /usr/bin/env python3

import csv
import logging
import logging.config
import os
import shutil

import time
import yaml

from datetime import datetime
from pathlib import Path
from time import localtime, strftime

import config
import api_DIVA as api
import rename_object as rename
import object_restore as restore

config = config.get_config()


# script_root = config["paths"]["script_root"]
csv_watchfolder = config["paths"]["csv_watch_folder"]


logger = logging.getLogger(__name__)


def set_logger():
    """
    Setup logging configuration
    """
    path = "/Users/admin/Scripts/DIVA-API-Object-Restore-WF/logging.yaml"

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
    This script will restore object from DIVAArchive. The script is trigged from an external workflow from the Dalet Galazy BPM. The workflow from Dalet provides the ObjectName, FileName, and Folderpath information stored in DIVA. It uses DIVA's REST api to chedk the object info, and initiate a restore. Once the restore is started it will periodically check the status of the restore job until the object is completely restored. From there it moves the object to a watch folder, and adds the appropraite
    file extension.
    """

    date_start = str(strftime("%A, %d. %B %Y %I:%M%p", localtime()))

    csv_list = [
        x
        for x in os.listdir(csv_watchfolder)
        if x.endswith(".csv") and not x.startswith(".")
    ]

    if len(csv_list) != 0:
        set_logger()
        csv_row_list = []

        for csvfile in csv_list:
            csvfile_path = Path(csv_watchfolder, csvfile)
            with open(csvfile_path) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:

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
            csv_row_list.append(row)

            source_path = csvfile_path
            dest_path = Path(csv_watchfolder, "_DONE")
            rename.move_object(source_path, dest_path)

            return

    else:
        return

    # for row in csv_row_list:
    #     for key, value in row.items():
    #         print(key, value)

    submitted_csv_list = restore.submit_restore_req(csv_row_list)

    count = 0

    while count < 50:

        for object in submitted_csv_list:
            objectName = object["objectName"]
            requestId = object["requestId"]
            jobStatus = api.get_restore_status(objectName, requestId)

            if jobStatus is not None:
                job_complete = restore.evaluate_restore_status(jobStatus)

                if job_complete is True:
                    rename.rename_object(
                        object["fileName"], object["objectName"], object["folderPath"]
                    )
                    complete_message(objectName, fileName)
                    submitted_csv_list.remove(object)
                    if len(submitted_csv_list) == 0:
                        complete_msg = f"\n\
                         ==============================================\n\
                                        Script Complete\n\
                         ==============================================\n"
                        logger.info(complete_msg)

                else:
                    logger.info(f"Restore still processing for: {fileName}")
                    logger.info(f"Checking restore status again in 5min")
                    time.sleep(300)
            else:
                logger.error(
                    f"jobStatus for {objectName} returned None. removing from list"
                )
                submitted_csv_list.remove(object)

        count += 1

    if count > 50:
        logger.info(
            "Restore taking too long (over 4 hours), exiting script. \n Remaining objects: {submitted_csv_list}"
        )
        return


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
    main()
    # main(args=[
    #             "FC15B4F7AB88-80001000-0000-4088-AD86",
    #             "059977_WICKEDTUNA7_THEFLEETSTRIKESBACK_PTS_20190314145000.zip",
    #             "mnt/lun02/Gorilla/RuriStorage/15/D8/FC15B4F7AB88-80001000-0000-40B5-15D8"
    #             ])
