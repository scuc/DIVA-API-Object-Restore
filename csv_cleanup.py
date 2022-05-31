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

    logger.info(f"Begin CSV cleanup, checking for csv files in:  {csv_done_dir}")
    os.chdir(csv_done_dir)

    csv_list = get_csv()
    
    
    if csv_list == []:
        return
    else:
        try:
            compression = zipfile.ZIP_DEFLATED
            yesterday = datetime.today() - timedelta(1)

            csv_zip_filename = f"{strftime("%Y-%m", yesterday.timetuple())}_csv.zip"
            logger.info(f"zip filename: {csv_zip_filename}")
            
            for csvfile in csv_list:
        
                zippath = Path(csv_done_dir, csv_zip_filename)


                with zipfile.ZipFile(zippath, mode='a', compression=compression) as zipObj:

                    zipObj.write(Path(csv_done_dir, csvfile))
                    zipObj.close()
                    
                    logger.info(f"{csvfile} was written to zip:  {csv_zip_filename}")

                    
                    archive = zipfile.ZipFile(zippath, mode='r')
                    test_result = archive.testzip()

                    if test_result == None: 
                        logger.info(f"{csv_zip_filename} test sucessful.")
                        logger.info(f"Archived csv: {csvfile}")
                        delete_csv(csvfile)
                        return
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
    Delete a give csv file. 
    """

    logpath = Path(csv_done_dir, csvfile)
    logpath.unlink()
    logger.info(f"CSV deleted: {csvfile}")

    return 

if __name__ == '__main__':
    csv_cleanup()
