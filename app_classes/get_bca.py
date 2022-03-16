import json
import sys
import os
import datetime
from app_classes.bca_k2helper import bca_k2workbench
import logging

logger = logging.getLogger(__name__)

class BCA(object):
    def __init__(self,bcareason):
        self.accessOverrideSession = None
        self.expirationTime = None
        self.bcareason = bcareason

    def renew():
        logging.error("Renewing BCA")    

    
    def work_bca_reason(self):
        if ( not self.bcareason):
            justification = input("Please provide the business case authorization (BCA) reason why you need to run tatool on the accounts: ")
        else:
            justification = self.bcareason

        if justification:
            os.environ["BCAjustification"] = str(justification)
        else:
            logging.error('ERROR: Insert the justification to access the resources!')
            sys.exit(1)

    def submit_bca_request(self):
        json_justification = {"justificationType": "notListed", "justificationMetadata": {"justification": os.environ["BCAjustification"]}}
        bcak2 = bca_k2workbench()
        r = bcak2.post(json_justification)
        if r.status_code == 200:
            rj = json.loads(r.text)
            self.accessOverrideSession = rj['accessOverrideSession']
            self.expirationTime = datetime.datetime.fromtimestamp(rj['expirationTime']).strftime('%c')
            os.environ["BCAaccessOverrideSession"] = self.accessOverrideSession
            os.environ["BCAexpirationTime"] = self.expirationTime
        else:
            logger.error('Unable to complete the Access Override Session! Retry or contact the developer.')
            sys.exit(1)
