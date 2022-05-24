import logging

logger = logging.getLogger(__name__)


def object_getinfo(stateCode,collectionName,instance):
    """
    Records the info for a given object in DIVA.
    """
    logger.info("="*25)
    logger.info(f"StatusCode: {statusCode}")
    logger.info(f"CollectionName: {collectionName}")
    logger.info(f"InstanceMessage: {instance_msg}")
    logger.info("="*25)

    return


def request_status(stateCode, progress, stateDescription, stateName, statusCode, statusDescription): 
    """ 
    Records the status of the restore job in DIVA.
    """
    logger.info("="*25)
    logger.info(f"StatusCode: {statusCode}")
    logger.info(f"StateDescription: {stateDescription}")
    logger.info(f"StateName: {stateName}")
    logger.info(f"StatusDescription: {statusDescription}")
    logger.info(f"Job Progress: {progress}")
    logger.info("="*25)
    return 