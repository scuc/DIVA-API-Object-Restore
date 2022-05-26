import logging
import pprint
import requests
import time

import config as cfg
import get_authentication as auth
import api_logger as log

config = cfg.get_config()

url_core_manager = config["urls"]["core_manager_api"]
diva_source_dest = config["DIVA_Source_Dest"]

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
            collectionName = response["collectionName"]

            if diskInstances == None:
                instance = None
            if len(diskInstances) >= 0:
                instance = response["tapeInstances"][0]["id"]

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
        collectionName = None
        instance = None
        return statusCode, collectionName, instance


def post_restore_request(objectName, collectionName, instance):
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
            "qos": 0,
        }

        headers = {
            "Accept": "application/json",
            "Authorization": token,
        }

        r = requests.post(url, headers=headers, json=data, verify=False)

        # print("="*25)
        # print(f"REQUEST URL: {r.request.url}")
        # print(f"REQUEST BODY: {r.request.body}")
        # print(f"REQUEST HEADERS: {r.request.headers}")
        # print("="*25)

        response = r.json()

        # response_str = pprint.pprint(response)
        # print(response_str)
        # code = r.status_code

        logger.info(response)

        reponse_statusCode = response["statusCode"]
        requestId = response["requestId"]
        statusDescription = response["statusDescription"]

        return reponse_statusCode, requestId, statusDescription

    except Exception as e:
        api_exception_msg = f"EXCEPTION: {e}"
        logger.error(api_exception_msg)
        return "error"


def get_restore_status(objectName, requestID):
    """
    Returns the restore status for the requested object, untitl the job completes or fails.
    Status Codes:
    200 = Sucessful
    400 = Invalid ID supplied
    401 = Unauthorized
    403 = Forbidden
    404 = Request not found
    """

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

        r = requests.get(
            url_object_byobjectName, headers=headers, params=params, verify=False
        )

        response = r.json()
        code = r.status_code

        if code == 200:

            jobStatus = {
                "stateCode": response["stateCode"],
                "progress": response["progress"],
                "stateDescription": response["stateDescription"],
                "stateName": response["stateName"],
                "statusCode": response["statusCode"],
                "statusDescription": response["statusDescription"],
                "progress": response["progress"],
            }

            logger.info(jobStatus)
            return jobStatus

        else:
            logger.error(f"unable to obtain jobstatus - status_code = {code}")
            jobStatus = None
            return jobStatus

    except Exception as e:
        logger.error(f"Exception on RequestId:{requestID} \n {e}")
        return


if __name__ == "__main__":
    get_obj_info(objectName="40A8F02A4440-8000FFFF-FFFF-B73F-D816")
    # get_restore_status(objectName="40A8F02A4440-8000FFFF-FFFF-EF92-7898", requestID="255671")
    # api_obj_check(
    #     objectName="FC15B4F7AB88-8000FFFF-FFFF-F62C-5866")
    # post_restore_request(
    #     objectName="FC15B4F7AB88-8000FFFF-FFFF-F62C-5866")
 