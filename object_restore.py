import logging
import logging.config


import api_DIVA as api

logger = logging.getLogger(__name__)


def submit_restore_req(csv_row_list):
    submitted_csv_list = []

    for csv_row in csv_row_list:
        try:
            objectName = csv_row["objectName"]
            statusCode, collectionName, instance = api.get_obj_info(objectName)

            if statusCode == 200:
                (
                    restore_statusCode,
                    requestId,
                    statusDescription,
                ) = api.post_restore_request(objectName, collectionName, instance)
                csv_row.update(
                    {
                        "restore_StatusCode": restore_statusCode,
                        "requestId": requestId,
                        "statusDescription": statusDescription,
                        "statusCode": statusCode,
                        "collectionName": collectionName,
                        "instance": instance,
                    }
                )
                submitted_csv_list.append(csv_row)
                print(csv_row)

            else:
                logger.info(
                    f"statusCode: {statusCode} - unable to locate object in DIVA"
                )
                continue

        except Exception as e:
            logger.error(f"Error on object: {csv_row}")
            logger.error(e)
            return

    return submitted_csv_list


def evaluate_restore_status(jobStatus):

    (
        stateCode,
        progress,
        stateDescription,
        stateName,
        statusCode,
        statusDescription,
    ) = jobStatus.values()

    # print("="*30)
    # print(f"StateCode: {stateCode}")
    # print(f"Progress: {progress}")
    # print(f"State Description: {stateDescription}")
    # print(f"stateName: {stateName}")
    # print(f"statusCode: {statusCode}")
    # print(f"statusDescription: {statusDescription}")
    # print("="*30)

    if progress < 100 and statusCode == 1000 and statusDescription == "success":
        restore_complete = False
        return restore_complete

    if (
        progress == 100
        and stateDescription == "Completed"
        and stateName == "DIVA_COMPLETED"
        and statusCode == 1000
        and statusDescription == "success"
    ):
        restore_complete = True
        return restore_complete

    if stateDescription == "Cancelled" or progress < 0:
        logger.info("Restore job ended before the transfer completed.")
        restore_complete = False
        return restore_complete
