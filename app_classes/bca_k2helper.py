import requests, json
import getpass
import os
import sys
import time
import logging


class bca_k2workbench:
    USER_AGENT = {
        'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.89 Safari/537.36',
        'Content-Type': 'application/json'}
    K2ENDPOINT = "https://k2.amazon.com/access_override/"
    COOKIE_DIR = os.path.expanduser("~/.midway")
    COOKIE_FILE = os.path.join(COOKIE_DIR, "cookie")

    # Wrapper to make calling k2 a little easier

    def check_midway_cookies(self):
        if os.path.isfile(bca_k2workbench.COOKIE_FILE):
            filetime = os.path.getmtime(bca_k2workbench.COOKIE_FILE)
            timenow = time.time()
            difference_in_seconds = timenow - filetime
            if difference_in_seconds > 86400:
                logging.error('mwinit token expired! Please run mwinit before to run the script!')
                sys.exit(1)
            if difference_in_seconds > 64800:
                logging.warning(
                    'mwinit token older than 18 hours, please be sure to have it refreshed for long time run tasks!')
            elif difference_in_seconds > 43200:
                logging.warning(
                    'mwinit token older than 12 hours, please be sure to have it refreshed for long time run tasks!')
        else:
            logging.error(
                'Unable to find the mwinit cookie file! Please be sure to have mwinit installed and generate the cookie before to run the script!')
            sys.exit(1)

    def get_midway_cookies(self):
        f = open(bca_k2workbench.COOKIE_FILE, 'r')
        for line in f:
            split = line.split('\t')
            if split[0] == '#HttpOnly_midway-auth.amazon.com':
                return split[6].replace('\n', '')

    def post(self, payload):
        requests.packages.urllib3.disable_warnings()
        cookie = self.get_midway_cookies()
        s = requests.Session()
        jar = requests.cookies.RequestsCookieJar()

        jar.set('user_name', getpass.getuser(), domain='midway-auth.amazon.com')
        jar.set('session', cookie, domain='midway-auth.amazon.com')
        data = json.dumps(payload, separators=(',', ':'))

        with requests.Session() as s:
            response = s.post(bca_k2workbench.K2ENDPOINT, headers=bca_k2workbench.USER_AGENT, cookies=jar, verify=False,
                              data=data)
        return response
