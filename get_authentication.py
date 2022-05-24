#!/usr/bin/env python3
import logging
import requests

import config as cfg

config = cfg.get_config()

creds_name = config['creds']['name']
creds_pw = config['creds']['password']
url_core_data = config['urls']['core_data_api']
url_core_manager = config['urls']['core_manager_api']

logger = logging.getLogger(__name__)


def get_auth():
    """
    POST request to users/login, returns auth token
    """

    try:
        url_user_login = f"https://{url_core_data}/users/login"

        json = {
                "username": creds_name,
                "password": creds_pw
                }
        headers = {
                "Accept": "application/json"
                }
        r = requests.post(url_user_login, headers=headers, json=json, verify=False)
        response = r.json()
        code = r.status_code
        token = response["token"]
        print(f"RESPONSE: {response}")
        print(f"STATUS_CODE: {code}")
        print(f"TOKEN:  {token}")

        return token
    
    except Exception as e: 
        auth_err_msg = f"Error authenticating with the DIVA API: \n\
                        {e}"
        logger.error(auth_err_msg)

if __name__ == '__main__':
    get_auth()