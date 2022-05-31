import logging
import os
import re
import zipfile

from datetime import datetime, timedelta
from pathlib import Path
from time import localtime, strftime

import config as cfg


logger = logging.getLogger(__name__)

config = cfg.get_config()

csv_done_dir = config["paths"]["csv_done_dir"]
log_dir = config["paths"]["log_dir"]


def csv_cleanup():
    """
    Only list the log files with a datestamp that contains the previous month.
    Pass the list of log files to the 'zip_logs' function and create a zip archive.
    """

    os.chdir(csv_done_dir)

    csv_list = get_csv()

    if csv_list == []:
        return
    else:
        try:
            logger.info(f"CSV files for archive: {csv_list}")
            compression = zipfile.ZIP_DEFLATED
            yesterday = datetime.today() - timedelta(1)

            csv_zip_filename = f"{strftime('%Y-%m', yesterday.timetuple())}_csv.zip"

            zippath = Path(csv_done_dir, csv_zip_filename)

            for csvfile in csv_list:
                with zipfile.ZipFile(
                    zippath, mode="a", compression=compression
                ) as zipObj:

                    archive_source = Path(csv_done_dir, csvfile)

                    zipObj.write(archive_source.name)
                    zipObj.close()

                    logger.info(f"{csvfile} written to zip:  {csv_zip_filename}")

                    archive = zipfile.ZipFile(zippath, mode="r")
                    test_result = archive.testzip()

                    if test_result == None:
                        logger.info(f"Zip test sucessful")
                        logger.info(f"CSV Archived")
                        delete_csv(csvfile)
                    else:
                        zip_fail_msg = f"Failed to zip {csvfile} in archive: {csv_zip_filename}. \n test results: {test_result}"
                        logger.info(zip_fail_msg)

            return

        except zipfile.BadZipfile as error:
            logger.error(error)
            return


def get_csv():
    """
    Get a list of the CSV files needed for ZIP archive. CSV file ext may be appended with numbers,
    so list comp can't just check for files that endwith(".csv")
    """

    if not os.path.isdir(csv_done_dir):
        logger.info(f"dir does not exist at path: {csv_done_dir}")
    else:
        csv_list = [
            x
            for x in os.listdir(csv_done_dir)
            if os.path.isfile(os.path.join(csv_done_dir, x))
            and not x.endswith(".zip")
            and not x.startswith(".")
        ]

    return csv_list


def delete_csv(csvfile):
    """
    Delete a given csv file.
    """

    logpath = Path(csv_done_dir, csvfile)
    logpath.unlink()
    logger.info(f"CSV deleted: {csvfile}")

    return


if __name__ == "__main__":
    csv_cleanup()
