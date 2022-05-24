import logging
import pprint
import requests 
import time

import config as cfg
import get_authentication as auth
import api_logger as log

config = cfg.get_config()

url_core_manager = config['urls']['core_manager_api']
diva_source_dest = config['DIVA_Source_Dest']

logger = logging.getLogger(__name__)


def api_call(url, params):
    token = auth.get_auth()
    headers = {
            "Accept": "application/json",
            "Authorization": token,
        }
    r = requests.get(url, headers=headers, params=params, verify=False)

    return r


def get_obj_info(objectName):
    """
    Returns the info for a given object in DIVAArchive.
    Status Codes: 
    200 = sucessful
    400 = Invalid object supplied
    401 = Unauthorized
    403 = Forbidden
    404 = Object not found
    """

    try:
        token = auth.get_auth()
        url = f"https://{url_core_manager}/objects/info"

        params = {
            "objectName": objectName,
            "collectionName": "TACS-DIVA",
        }

        headers = {
            "Accept": "application/json",
            "Authorization": token,
        }

        db_check_msg = f"Checking DIVA DB for object name:  {objectName}"
        logger.info(db_check_msg)

        r = requests.get(url, headers=headers, params=params, verify=False)

        # print("="*25)
        # print(f"REQUEST URL: {r.request.url}")
        # print(f"REQUEST BODY: {r.request.body}")
        # print(f"REQUEST HEADERS: {r.request.headers}")
        # print("="*25)

        response = r.json()
        # print("="*25)
        # print("RESPONSE:")
        # pprint.pprint(response)
        # print("="*25)

        # print(r.status_code)

        statusCode = r.status_code
        diskInstances = response["diskInstances"]

        if statusCode == 404: 
            collectionName = None
            instance = None
            # pprint(response)

        elif statusCode == 200: 
            collectionName = response['collectionName']

            if diskInstances == None: 
                instance = None
            if len(diskInstances) >= 0:
                instance = response['tapeInstances'][0]['id']

        else:
            collectionName = None
            instance = None
            # pprint(response)
            
        # print("="*25)
        # print("STATUS CODE: " + str(statusCode))
        # print("COLLECTION NAME: " + str(collectionName))
        # print("INSTANCE: " + str(instance))
        # print("="*25)
        # print("RESPONSE:")
        # pprint.pprint(response)

        return statusCode, collectionName, instance


    except Exception as e:
        api_exception_msg = f"EXCEPTION: {e}"
        logger.error(api_exception_msg)
        collectionName=None
        instance=None
        return statusCode, collectionName, instance


def api_obj_restore(objectName, collectionName, instance):
    """
    Requests an object restore from DIVAArchive.
    """
    try:
        token = auth.get_auth()

        url = f"https://{url_core_manager}/requests/restore"

        data = {
            "collectionName": collectionName,
            "destinationServer": diva_source_dest,
            "filePathRoot": "/",
            "instance": instance,
            "objectName": objectName,
            "options": " ",
            "priority": 70,
            "qos": 0
        }

        headers = {
            "Accept": "application/json",
            "Authorization": token,
        }

        db_check_msg = f"Checking DIVA DB for object name:  {objectName}"
        logger.info(db_check_msg)

        r = requests.post(url, headers=headers, json=data, verify=False)

        # print("="*25)
        # print(f"REQUEST URL: {r.request.url}")
        # print(f"REQUEST BODY: {r.request.body}")
        # print(f"REQUEST HEADERS: {r.request.headers}")
        # print("="*25)

        response = r.json()
        response_str = pprint.pprint(response)
        # print(response_str)

        code = r.status_code

        logger.info(response)

        reponse_statusCode = response["statusCode"]
        requestId = response["requestId"]
        statusDescription = response["statusDescription"]

        return reponse_statusCode, requestId, statusDescription

    except Exception as e:
        api_exception_msg = f"EXCEPTION: {e}"
        logger.error(api_exception_msg)
        return "error"


def api_status_request(objectName, requestID):
    """
    Returns the restore status for the requested object, untitl the job completes or fails. 
    Status Codes:
    200 = Sucessful
    400 = Invalid ID supplied
    401 = Unauthorized
    403 = Forbidden
    404 = Request not found
    """

    count = 0

    while True: 
        try:
            token = auth.get_auth()
            url_object_byobjectName = f"https://{url_core_manager}/requests/{requestID}"

            params = {}

            headers = {
                "Accept": "application/json",
                "Authorization": token,
            }

            db_check_msg = f"Checking restore status for:  {objectName}"
            logger.info(db_check_msg)

            r = requests.get(url_object_byobjectName,
                            headers=headers, params=params, verify=False)

            response = r.json()
            code = r.status_code

            jobStatus = {
                    "stateCode":response['stateCode'],
                    "progress":response['progress'],
                    "stateDescription": response['stateDescription'],
                    "stateName": response['stateName'],
                    "statusCode": response['statusCode'],
                    "statusDescription": response['statusDescription'],
                    "progress": response['progress']
                    }

            # print(jobStatus)

            if code == 200: 
                # print("RESPONSE:")
                # pprint.pprint(response)

                stateCode, progress, stateDescription, stateName, statusCode, statusDescription = jobStatus.values()

                # print("="*30)
                # print(f"StateCode: {stateCode}")
                # print(f"Progress: {progress}")
                # print(f"State Description: {stateDescription}")
                # print(f"stateName: {stateName}")
                # print(f"statusCode: {statusCode}")
                # print(f"statusDescription: {statusDescription}")
                # print("="*30)

                if (
                    progress < 100 and
                    statusCode == 1000 and 
                    statusDescription == 'success' and
                    count <= 100
                    ):
                    log.request_status(**jobStatus)
                    logger.info("PAUSE script for 300sec and check again")
                    time.sleep(300)
                    count += 1   

                if (
                    progress == 100 and 
                    stateDescription == 'Completed' and
                    stateName == 'DIVA_COMPLETED' and
                    statusCode == 1000 and 
                    statusDescription == 'success'
                    ):
                    log.request_status(**jobStatus)
                    return jobStatus

                if (
                    stateDescription == 'Cancelled'
                    or progress < 0 
                    ):
                    logger.info("Restore job ended before the transfer completed.")
                    return jobStatus
                    
                if count > 100: 
                    logger.info("Restore object taking too long - over 8 hours - exiting script.")    
                    log.request_status(**jobStatus)
                    return jobStatus   


            else:
                logger.info("Job Status returned code that was not 200")  
                return jobStatus                 

        except Exception as e:
            api_exception_msg = f"EXCEPTION: {e}"
            logger.error(api_exception_msg)
            return



if __name__ == '__main__':
    get_obj_info(objectName="40A8F02A4440-8000FFFF-FFFF-B73F-D816")
    # api_status_request(objectName="40A8F02A4440-8000FFFF-FFFF-EF92-7898", requestID="255671")
    # api_obj_check(
        #     objectName="FC15B4F7AB88-8000FFFF-FFFF-F62C-5866")
        # api_obj_restore(
        #     objectName="FC15B4F7AB88-8000FFFF-FFFF-F62C-5866")
