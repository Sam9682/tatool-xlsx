import logging
import json
import unicodedata
from app_classes.k2helper import k2workbench
from multiprocessing.dummy import Pool as ThreadPool

logger = logging.getLogger(__name__)

class aws_account:

    def __init__(self, input_args):
        self.k2 = k2workbench()
        self.input_args = input_args
        self.active_accounts_and_display_option_tuples_list = []

    def get_payer_accounts(self, payer_id, payer_type):
        payload = {
                "region": "us-east-1",
                "apiName": "kumoscp.searchCustomers",
                "args": {
                    "searchFilter": payer_type,
                    "searchFilterValue": payer_id
                    }
                }

        logging.info("Getting the payer account-id(s) for %s", payer_id)
        r = self.k2.post(payload)

        if r.status_code == 200:
            result = json.loads(r.text)
            if result['customerList']:
                return result['customerList'][0]['id']
            else:
                logging.error("KumoSCP returned no customers associated with the ID")
                raise Exception("KumoSCP returned no customers associated with the ID")
        else:
            logging.error("Unexpected error getting customer accounts from KumoSCP: %s", result)
            raise

    def get_customer_payer_accounts(self, payers_id, payer_type):
        list_payer_accounts = {}

        if payer_type == "WEB_DOMAIN":
            list_payer_accounts[payers_id] = self.get_payer_accounts(payers_id, payer_type)
        elif payer_type == "ACCOUNT_ID":
            for payer_id in payers_id:
                list_payer_accounts[payer_id] = self.get_payer_accounts(payer_id, payer_type)

        return list_payer_accounts

    def get_linked_accounts(self, payers_list, scope):
        linked_accounts_list = []

        for payer in payers_list:
            logging.info("Getting the all account-id(s) for " + payers_list[payer])

            paginationToken = "start"
            while paginationToken:
                payload = {
                        "region": "us-east-1",
                        "apiName": "kumoscp.getCustomerAccountFullList",
                        "args": {
                            "id": payers_list[payer]
                            }
                        }

                if paginationToken != "start":
                    payload['args']['paginationToken'] = paginationToken

                r = self.k2.post(payload)

                if r.status_code == 200:
                    try:
                        result = json.loads(r.text)
                        account_list = result['accounts']
                        for account in account_list:
                            if account['status'] == 'Active' and (scope == "WEB_DOMAIN" or account[scope] == payer):
                                logging.info("Adding " + account['supportLevel'] + " active account (" + account['accountId'] + ")" + account['name'])
                                linked_accounts_list.append(account['accountId'])
                        if 'paginationToken' in result:
                            paginationToken = result['paginationToken']
                        else:
                            break
                    except:
                        logging.warning("Unable to get any linked/active accounts related to account: %s", account['name'])
                        continue

        logging.info("Got " + str(len(linked_accounts_list)) + " related accounts!")

        return linked_accounts_list


    def get_active_accounts(self, accounts):

        active_accounts_list = []
        payload = {
            "region": "us-east-1",
            "apiName": "avs.getAccountStatus",
            "args": {"accountIds": accounts}
        }
        logging.info("Filtering only the active linked account-id(s)")
        r = self.k2.post(payload)

        if r.status_code == 200:
            result = json.loads(r.text)
            accounts_status_dict = dict(zip(accounts, result['accountStatus']))

            for k, v in accounts_status_dict.items():
                if v != 'Active':
                    continue
                else:
                    active_accounts_list.append(k)
        return active_accounts_list

    def get_email_address(self, accountid):
        payload = {
            "region": "us-east-1",
            "apiName": "awsadms.getAccountIdentifiersByAccountId",
            'accountId': accountid,
            "args": {"accountId": accountid}
        }

        r = self.k2.post(payload)
        try:
            result = json.loads(r.text)
            customer_id = result['identifiers']['CustomerIdType']
        except:
            logging.warning(
                "Unable to convert " + accountid + " to email address!!! Displaying the account-id. Continuing...")
            self.active_accounts_and_display_option_tuples_list.append((accountid, accountid))
            return

        # Legacy Marketplace api
        payload = {'apiName': 'iss.searchCustomers', 'args':
            {'query': {'terms': [{'field_': 'CustomerId', 'value_': customer_id,
                                  'prefix': 'false', 'phonetic': 'false'}]},
             'marketplaceId': 'ATVPDKIKX0DER', 'includeDeactivatedCustomers': 'false', 'pageSize': 10}}
        r = self.k2.post(payload)
        try:
            result = json.loads(r.text)
            email_address = result['items_'][0]['email_']
            logging.info(
                "Converted the account-id " + accountid + " to email address " + email_address + " to improve the readability of the data...")
            self.active_accounts_and_display_option_tuples_list.append((accountid, email_address))
        except:
            # New Marketplace api
            payload = {'apiName': 'iss.searchCustomers', 'args':
                {'query': {'terms': [
                    {'field_': 'CustomerAccountPoolId', 'value_': '5827011', 'prefix': 'false', 'phonetic': 'false'},
                    {'field_': 'CustomerId', 'value_': customer_id,
                     'prefix': 'false', 'phonetic': 'false'}]},
                    'includeDeactivatedCustomers': 'false', 'pageSize': 10}}

            r = self.k2.post(payload)
            try:
                result = json.loads(r.text)
                email_address = result['items_'][0]['email_']
                logging.info(
                    "Converted the account-id " + accountid + " to email address " + email_address + " to improve the readability of the data...")
                self.active_accounts_and_display_option_tuples_list.append((accountid, email_address))
            except:
                logging.warning(
                    "Unable to convert " + accountid + " to email address!!! Displaying the account-id. Continuing...")
                self.active_accounts_and_display_option_tuples_list.append((accountid, accountid))

    def kick_parallel_get_email(self, active_accounts_list):
        pool = ThreadPool(self.input_args.threads)
        pool.map(self.get_email_address, active_accounts_list)
        pool.close()
        pool.join()
        return self.active_accounts_and_display_option_tuples_list

    def get_name(self, accountid):
        payload = {
            "region": "us-east-1",
            "apiName": "awsadms.getAccountIdentifiersByAccountId",
            'accountId': accountid,
            "args": {"accountId": accountid}
        }

        r = self.k2.post(payload)
        try:
            result = json.loads(r.text)
            customer_id = result['identifiers']['CustomerIdType']
        except:
            logging.warning(
                "Unable to convert " + accountid + " to email address!!! Displaying the account-id. Continuing...")
            self.active_accounts_and_display_option_tuples_list.append((accountid, accountid))
            return

        # Legacy Marketplace api
        payload = {'apiName': 'iss.searchCustomers', 'args':
            {'query': {'terms': [{'field_': 'CustomerId', 'value_': customer_id,
                                  'prefix': 'false', 'phonetic': 'false'}]},
             'marketplaceId': 'ATVPDKIKX0DER', 'includeDeactivatedCustomers': 'false', 'pageSize': 10}}
        r = self.k2.post(payload)
        try:
            result = json.loads(r.text)
            name = result['items_'][0]['name_']
            #name = unicodedata.normalize('NFD', name).encode('ascii', 'ignore')
            name = name.replace('/', '').replace('\\', '').replace('\t', ' ').replace(':', ' ').replace(';', ' ').replace(',', ' ')
            logging.info(
                "Converted the account-id " + accountid + " to name " + name + " to improve the readability of the data...")
            self.active_accounts_and_display_option_tuples_list.append((accountid, name))
        except:
            # New Marketplace api
            payload = {'apiName': 'iss.searchCustomers', 'args':
                {'query': {'terms': [
                    {'field_': 'CustomerAccountPoolId', 'value_': '5827011', 'prefix': 'false', 'phonetic': 'false'},
                    {'field_': 'CustomerId', 'value_': customer_id,
                     'prefix': 'false', 'phonetic': 'false'}]},
                    'includeDeactivatedCustomers': 'false', 'pageSize': 10}}

            r = self.k2.post(payload)
            try:
                result = json.loads(r.text)
                name = result['items_'][0]['name_']
                name = unicodedata.normalize('NFD', name).encode('ascii', 'ignore')
                name = name.replace('/', '').replace('\\', '').replace('\t', ' ').replace(':', ' ').replace(';', ' ').replace(',', ' ')
                logging.info(
                    "Converted the account-id " + accountid + " to name " + name + " to improve the readability of the data...")
                self.active_accounts_and_display_option_tuples_list.append((accountid, name))
            except:
                logging.warning(
                    "Unable to convert " + accountid + " to name!!! Displaying the account-id. Continuing..." )
                self.active_accounts_and_display_option_tuples_list.append((accountid, accountid))

    def kick_parallel_get_name(self, active_accounts_list):
        pool = ThreadPool(self.input_args.threads)
        pool.map(self.get_name, active_accounts_list)
        pool.close()
        pool.join()
        return self.active_accounts_and_display_option_tuples_list

    def display_accountid(self, active_accounts_list):
        for accountid in active_accounts_list:
            self.active_accounts_and_display_option_tuples_list.append((accountid, accountid))
        return self.active_accounts_and_display_option_tuples_list

    def dump_list_to_file(self, active_accounts_and_display_option_tuples_list):
        if self.input_args.displayformat == 'name':
            string_to_dump = 'AccountId,Account_Name\n'
        elif self.input_args.displayformat == 'email':
            string_to_dump = 'AccountId,Account_Email\n'
        else: string_to_dump = 'AccountId,AccountId\n'
        for tupla in active_accounts_and_display_option_tuples_list:
            string_to_dump = string_to_dump + tupla[0] + ',' + tupla[1] + '\n'

        logger.info('Writing the accounts to the file ' + self.input_args.generateaccountslistonly + '...' )
        try:
            with open(self.input_args.generateaccountslistonly, mode="w") as f:
                f.write(string_to_dump)
            logger.info('Exiting from the script...')
        except: logger.error('Unable to dump the accounts to the file specified, please check the filename and the filesystem!')

    def check_duplicates(self, active_accounts_and_display_option_tuples_list):

        logging.info("Checking for duplicates in display option " + self.input_args.displayformat + "...")

        # using set
        visited = set()

        # Output list initialization
        clean_active_accounts_and_display_option_tuples_list = []

        # Iteration
        count = 1
        for a, b in active_accounts_and_display_option_tuples_list:
            if not b in visited:
                visited.add(b)
                clean_active_accounts_and_display_option_tuples_list.append((a, b))
            else:
                clean_active_accounts_and_display_option_tuples_list.append((a, b + "-DUPL_SEQNUM=" + str(count)))
                count = count + 1

        if count != 1:
            logging.warning("Found duplicates in " + self.input_args.displayformat + "!")

            for a, b in clean_active_accounts_and_display_option_tuples_list:
                if "DUPL_SEQNUM" in b:
                    logging.warning("The account-id " + a + " will be displayed as " + b + ".")

            logging.warning("The script will use the changed name to display the information for the account.")
            logging.warning("Please inform the customer that is not a best practice having duplicated names or emails for the accounts!")
        else:
            logging.info("No duplicates found in " + self.input_args.displayformat + ".")

        return clean_active_accounts_and_display_option_tuples_list