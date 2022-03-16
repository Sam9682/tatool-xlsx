import requests, json, sys
import getpass
import os
import sys
import time
import logging
from time import sleep
from app_classes.get_bca import BCA

class k2workbench:

    USER_AGENT = {
        'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.89 Safari/537.36'}
    K2ENDPOINT = "https://k2.amazon.com/workbench/aws/resources/"
    COOKIE_DIR = os.path.expanduser("~/.midway")
    COOKIE_FILE = os.path.join(COOKIE_DIR, "cookie")
    HTTP_SUCCESS = [200]
    HTTP_Throttling = [429]
    HTTP_BAD_REQ_CODE = [400, 401]
    BCA_REQ_CODE = [403]
    HTTP_NOT_FOUND_CODE = [404]
    HTTP_SERVER_ERROR_CODE = [500, 501, 502, 503]

    # Wrapper to make calling k2 a little easier

    def check_midway_cookies(self):
        if os.path.isfile(k2workbench.COOKIE_FILE):
            filetime = os.path.getmtime(k2workbench.COOKIE_FILE)
            timenow = time.time()
            difference_in_seconds = timenow - filetime
            if difference_in_seconds > 86400:
                logging.error('mwinit token expired! Please run mwinit before to run the script!')
                sys.exit(1)
            if difference_in_seconds > 64800:
                logging.warning('mwinit token older than 18 hours, please be sure to have it refreshed for long time run tasks!')
            elif difference_in_seconds > 43200:
                logging.warning(
                    'mwinit token older than 12 hours, please be sure to have it refreshed for long time run tasks!')
        else:
            logging.error('Unable to find the mwinit cookie file! Please be sure to have mwinit installed and generate the cookie before to run the script!')
            sys.exit(1)

    def get_midway_cookies(self):
        f = open(k2workbench.COOKIE_FILE, 'r')
        for line in f:
            split = line.split('\t')
            if split[0] == '#HttpOnly_midway-auth.amazon.com':
                return split[6].replace('\n', '')

    def post(self,payload):
        payload["accessOverrideSession"] = os.environ["BCAaccessOverrideSession"]
        requests.packages.urllib3.disable_warnings()
        cookie = self.get_midway_cookies()
        s = requests.Session()
        jar = requests.cookies.RequestsCookieJar()

        jar.set('user_name', getpass.getuser(), domain='midway-auth.amazon.com')
        jar.set('session', cookie, domain='midway-auth.amazon.com')
        data = json.dumps(payload, separators=(',', ':'))

        count = 0
        error_connection = 0
        sleep_time = 15
        while count < 4:
            count +=1
            try:
                with requests.Session() as s:
                    response = s.post(k2workbench.K2ENDPOINT, headers=k2workbench.USER_AGENT, cookies=jar, verify=False,
                                  data=data)
                    if response.status_code in self.HTTP_SUCCESS:
                        return response
                    elif response.status_code in self.HTTP_Throttling:
                        if count != 6:
                            logging.warning('Detected K2 api call throttling, sleeping %s seconds, then retry...', str(sleep_time))
                            sleep(sleep_time)
                            sleep_time = sleep_time * 2
                            continue
                        else:
                            logging.error('Detected K2 api call throttling! Raising an exception!')
                            raise
                    elif response.status_code in self.BCA_REQ_CODE:
                        logging.error('Detected K2 BCA error! Trying to request a new Business Case Authorization according to the justification specified...')
                        bca=BCA("Renewing request")
                        bca.submit_bca_request()
                        continue
                    elif response.status_code in self.HTTP_BAD_REQ_CODE:
                        logging.error('Detected K2 api BAD HTTP Request! Raising an exception!')
                        raise
                    elif response.status_code in self.HTTP_SERVER_ERROR_CODE:
                        if count != 6:
                            logging.warning('Detected K2 api Server Error, sleeping %s seconds, then retry...', str(sleep_time))
                            sleep(sleep_time)
                            sleep_time = sleep_time * 2
                            continue
                        else:
                            logging.error('Detected K2 api Server Error! Raising an exception!')
                            raise
                    elif response.status_code in self.HTTP_NOT_FOUND_CODE:
                        logging.warning('Detected K2 Page Not Found...continuing...')
                        return response
                    else:
                        raise
            except requests.exceptions.ConnectionError:
                error_connection += 1
                if error_connection < 3:
                    count -= 1
                    logging.error('Connection Error! Retrying...')
                    continue
                else:
                    logging.error('Three Connection Errors detected! Exiting...')
                    raise
            except Exception as e:
                logging.error(e)
        return response
