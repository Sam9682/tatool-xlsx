import os
import logging
import json
import csv
from time import sleep
from app_classes.k2helper import k2workbench
from multiprocessing.dummy import Pool as ThreadPool
from shutil import copyfile

logger = logging.getLogger(__name__)


class TrustedAdvisor:

    def __init__(self, input_args):
        self.k2 = k2workbench()
        self.input_args = input_args
        self.csv_full_list = []
        self.check_account_detail_tuple_list = []

    def refresh_ta_checks(self, check_account_detail_tuple_list):
        pool = ThreadPool(self.input_args.threads)
        results = pool.map(self.run_refresh_check, check_account_detail_tuple_list)
        pool.close()
        pool.join()
        logging.info("Waiting 300 seconds for refresh to complete on the platform...")
        sleep(300)

    def run_refresh_check(self, check_account_detail_tuple_list):
        account_display_name = check_account_detail_tuple_list[0]
        accountid = check_account_detail_tuple_list[1]
        check = check_account_detail_tuple_list[2]
        payload = {'apiName': 'trustedadvisor.refreshCheck',
                   'args': {'checkId': check, 'accountInfo': {'accountId': accountid}}}
        r = self.k2.post(payload)
        if r.status_code == 200:
            logging.info("Refreshing checkId:" + check + " for the account " + account_display_name)
        else:
            logging.warning("Unable to refresh checkId:" + check + " for the account " + account_display_name + '. Probably the check has been refreshed recently, TATool will collect the current check status.')

    def kick_parallel_Describe_Check(self, active_accounts_and_display_option_tuples_list):
        pool = ThreadPool(self.input_args.threads)
        results = pool.map(self.describe_trusted_advisor_checks, active_accounts_and_display_option_tuples_list)
        pool.close()
        pool.join()
        return self.check_account_detail_tuple_list

    def describe_trusted_advisor_checks(self, active_accounts_and_display_option_tuples_list):
        accountid = active_accounts_and_display_option_tuples_list[0]
        account_display_name = active_accounts_and_display_option_tuples_list[1]
        payload = {
            "region": "us-east-1",
            "apiName": "trustedadvisor.describeTrustedAdvisorChecks",
            "args": {'language': 'en', 'accountInfo': {'accountId': accountid}}
        }

        logging.info("Getting check-ids for the account:" + account_display_name)

        r = self.k2.post(payload)

        if r.status_code == 200:
            result = json.loads(r.text)

            account_dict_checks_list = result['checks']
        else:
            account_dict_checks_list = {}

        for check in account_dict_checks_list:
            self.check_account_detail_tuple_list.append(
                (account_display_name, accountid, check['id'], check['category'], check['name']))

    def kick_parallel_getCheckDetail(self, check_account_detail_tuple_list):
        pool = ThreadPool(self.input_args.threads)
        results = pool.map(self.get_ta_results_for_check, check_account_detail_tuple_list)
        pool.close()
        pool.join()
        return results

    def get_ta_results_for_check(self, check_account_detail_tuple_list):
        account_display_name = check_account_detail_tuple_list[0]
        account = check_account_detail_tuple_list[1]
        checkid = check_account_detail_tuple_list[2]
        check_category = check_account_detail_tuple_list[3]
        check_name = check_account_detail_tuple_list[4]

        payload = {
            "region": "us-east-1",
            "apiName": "trustedadvisor.describeTrustedAdvisorCheckResult",
            "args": {'language': 'en', 'accountInfo': {'accountId': account}, "checkId": checkid}
        }

        logging.info("Getting check-id " + checkid + " for the account " + account_display_name)

        r = self.k2.post(payload)

        if r.status_code == 200:
            result = json.loads(r.text)
            check_result = result['result']
            self.get_check_details(check_result, account, account_display_name, check_category, check_name)

    def get_check_details(self, check_result, account, account_display_name, check_category, check_name):
        try:
            if check_result['flaggedResources'] is not None:
                for resource in check_result['flaggedResources']:
                    item_result_list = []
                    item_result_list.append(check_result['checkId'])
                    item_result_list.append(account)
                    item_result_list.append(account_display_name)
                    item_result_list.append(check_category)
                    item_result_list.append(check_result['status'])
                    item_result_list.append(check_name)
                    item_result_list.append(resource['region'] if (resource['region'] is not None) else "None")
                    item_result_list.append("Yes" if (resource['isSuppressed'] is not False) else "No")
                    item_result_list.append("---")
                    for metadata_item in resource['metadata'] if (resource['metadata'] is not None) else " ":
                        item_result_list.append('\"' + metadata_item + '\"' if (metadata_item is not None) else "None")
                    self.csv_full_list.append(",".join(item_result_list))
            else:
                pass
        except(TypeError, KeyError):
            pass

    def write_unfiltered_output_file(self):
        logging.info("Writing the unfiltered full csv file...")
        file_data = "\n".join(self.csv_full_list).encode('utf-8').strip()
        try:
            with open(str(self.input_args.unfiltered_folder) + "full_report_with_resource-ids.csv", mode="wb") as f:
                f.write(
                    b"CheckId,Account-Id,Account Display Name,TA Category,Status External,TA Check Name,Region,isSuppressed,---,Resources_Metadata\n")
                f.write(file_data)
        except Exception as e:
            print ("EXCEPTION:" + str(e))

    def filter_ta_file(self):
        logging.info("Copying the filter file applied as reference...")
        copyfile(self.input_args.filter_file_ta, self.input_args.filtered_folder + 'filter_applied.txt')
        filter_account_resource_tuple_list = []
        new_file_list = []
        logging.info("Analyzing the filter to be applied...")
        with open(str(self.input_args.filter_file_ta), mode="r") as f:
            for line in f:
                accountid = line.split(',')[0].strip('\n')
                checkname = line.split(',')[1].strip('\n')
                resource = line.split(',')[2].strip('\n')
                filter_account_resource_tuple_list.append((accountid, checkname, resource))

        logging.info("Parsing the file to apply the filter...")
        with open(str(self.input_args.unfiltered_folder) + 'full_report_with_resource-ids.csv', mode="r") as f:
            for line in f:
                match_found = False
                for accountid_checkname_resource in filter_account_resource_tuple_list:
                    if accountid_checkname_resource[0] in line and accountid_checkname_resource[1] in line and \
                            accountid_checkname_resource[2] in line:
                        match_found = True
                        break
                if match_found == False:
                    new_file_list.append(line)

        file_data = "".join(new_file_list)
        logging.info("Writing the filtered csv file...")
        try:
            with open(self.input_args.filtered_folder + 'filtered_report_with_resource-ids.csv', mode="wb") as f:
                f.write(file_data)
        except Exception as e:
            print(e)

    def unfiltered_split_by_checkname(self):
        files_dict = {}
        logging.info("Parsing the unfiltered full csv file to split it by check name...")
        with open(self.input_args.unfiltered_folder + 'full_report_with_resource-ids.csv', mode="r") as f:
            lines = f.readlines()
            for line in lines[1:]:
                checkname = line.split(',')[5].strip('\n')
                if checkname in files_dict:
                    files_dict[checkname].append(line)
                else:
                    files_dict[checkname] = [line]

        for checkname, lines_list in files_dict.items():
            columns_line = self.get_unfiltered_split_by_checkname_file_columns(checkname)
            lines_list.insert(0, columns_line)

        if not os.path.exists(self.input_args.unfiltered_folder + 'unfiltered_split_by_checkname'):
            logging.info("Creating the directory unfiltered_split_by_checkname...")
            os.makedirs(self.input_args.unfiltered_folder + 'unfiltered_split_by_checkname')

        logging.info("Writing the files splitted by check name...")
        for check, lines in files_dict.items():
            file_data = "".join(lines)
            try:
                with open(str(self.input_args.unfiltered_folder) + "unfiltered_split_by_checkname/" + check + ".csv",
                          mode="w") as f:
                    f.write(file_data)
            except Exception as e:
                print("EXCEPTION Writing the files splitted by check name:" + str(e))

    def filtered_split_by_checkname(self):
        files_dict = {}
        logging.info("Parsing the filtered full csv file to split it by check name...")
        with open(str(self.input_args.filtered_folder) + 'filtered_report_with_resource-ids.csv', mode="r") as f:
            f.readline()
            for line in f:
                checkname = line.split(',')[5].strip('\n')
                if checkname in files_dict:
                    files_dict[checkname].append(line)
                else:
                    files_dict[checkname] = [line]

        for checkname, lines_list in files_dict.items():
            columns_line = self.get_unfiltered_split_by_checkname_file_columns(checkname)
            lines_list.insert(0, columns_line)

        if not os.path.exists(self.input_args.filtered_folder + 'filtered_split_by_checkname'):
            logging.info("Creating the directory filtered_split_by_checkname...")
            os.makedirs(self.input_args.filtered_folder + 'filtered_split_by_checkname')

        logging.info("Writing the filtered files splitted by check name...")
        for check, lines in files_dict.items():
            file_data = "".join(lines)
            try:
                with open(self.input_args.filtered_folder + 'filtered_split_by_checkname/' + check + '.csv',
                          mode="w") as f:
                    f.write(file_data)
            except Exception as e:
                print(e)

    def unfiltered_split_by_account(self):
        files_dict = {}

        with open(str(self.input_args.unfiltered_folder) + "full_report_with_resource-ids.csv", mode="r") as f:
            try:
                for line in f:
                    account = line.split(',')[2].strip('\n')
                    if account in files_dict:
                        files_dict[account].append(line)
                    else:
                        files_dict[account] = [line]
            except Exception as e:
                print(e)

        if not os.path.exists(self.input_args.unfiltered_folder + 'unfiltered_split_by_account'):
            logging.info("Creating the directory unfiltered_split_by_account...")
            os.makedirs(self.input_args.unfiltered_folder + 'unfiltered_split_by_account')

        for account, lines in files_dict.items():
            if not os.path.exists(self.input_args.unfiltered_folder + 'unfiltered_split_by_account/' + account):
                os.makedirs(self.input_args.unfiltered_folder + 'unfiltered_split_by_account/'  + account)

            account_dict = {}

            for line in lines:
                checkname = line.split(',')[5].strip('\n')
                if checkname in account_dict:
                    account_dict[checkname].append(line)
                else:
                    account_dict[checkname] = [line]

            for checkname, lines_list in account_dict.items():
                columns_line = self.get_unfiltered_split_by_checkname_file_columns(checkname)
                lines_list.insert(0, columns_line)

            for check, lines in account_dict.items():
                file_data = "".join(lines)
                try:
                    with open(self.input_args.unfiltered_folder + 'unfiltered_split_by_account/' + account + '/' + check + '.csv',
                              mode="w") as f:
                        f.write(file_data)
                except Exception as e:
                    print(e)

    def filtered_split_by_account(self):
        files_dict = {}

        logging.info("Parsing the filtered full csv file to split it by account...")
        with open(str(self.input_args.filtered_folder) + 'filtered_report_with_resource-ids.csv', mode="r") as f:
            f.readline()
            for line in f:
                account = line.split(',')[2].strip('\n')
                if account in files_dict:
                    files_dict[account].append(line)
                else:
                    files_dict[account] = [line]

        if not os.path.exists(self.input_args.filtered_folder + 'filtered_split_by_account'):
            logging.info("Creating the directory filtered_split_by_account...")
            os.makedirs(self.input_args.filtered_folder + 'filtered_split_by_account')

        logging.info("Writing the filtered files splitted by account...")
        for account, lines in files_dict.items():
            if not os.path.exists(self.input_args.filtered_folder + 'filtered_split_by_account/' + account):
                os.makedirs(self.input_args.filtered_folder + 'filtered_split_by_account/'  + account)

            account_dict = {}

            for line in lines:
                checkname = line.split(',')[5].strip('\n')
                if checkname in account_dict:
                    account_dict[checkname].append(line)
                else:
                    account_dict[checkname] = [line]

            for checkname, lines_list in account_dict.items():
                columns_line = self.get_unfiltered_split_by_checkname_file_columns(checkname)
                lines_list.insert(0, columns_line)

            for check, lines in account_dict.items():
                file_data = "".join(lines)
                try:
                    with open(self.input_args.filtered_folder + 'filtered_split_by_account/' + account + '/' + check + '.csv',
                              mode="w") as f:
                        f.write(file_data)
                except Exception as e:
                    print(e)

    def generate_isSuppressed(self):
        columns_line = "CheckId,Account-Id,Account Display Name,TA Category,Status External,TA Check Name,Region,isSuppressed,---,Resources_Metadata\n"
        suppressed_list = []
        not_suppressed_list = []
        logging.info("Parsing the file to apply the isSuppressed filter...")
        with open(str(self.input_args.unfiltered_folder) + 'full_report_with_resource-ids.csv', mode="r") as f:
            f.readline()
            for line in f:
                if line.split(",")[7] == 'Yes':
                    suppressed_list.append(line)
                else:
                    not_suppressed_list.append(line)

        if len(suppressed_list) < 1:
            logging.info("No suppressed checks found! Refer to the unfiltered folder.")
            try:
                with open(self.input_args.isSuppressed_folder + 'NOT_Suppressed_with_resource-ids.csv', mode="wb") as f:
                    f.write(b"No suppressed checks found! Refer to the unfiltered folder.")
            except Exception as e:
                print(e)
        else:
            not_suppressed_list.insert(0, columns_line)
            suppressed_list.insert(0, columns_line)
            not_suppressed_file_data = "".join(not_suppressed_list).encode('utf-8')
            suppressed_file_data = "".join(suppressed_list).encode('utf-8')
            logging.info("Writing the filtered csv file exluding the suppressed checks...")
            try:
                with open(str(self.input_args.isSuppressed_folder) + 'NOT_Suppressed_with_resource-ids.csv', mode="wb") as f:
                    f.write(not_suppressed_file_data)
            except Exception as e:
                print(e)

            logging.info("Writing the csv file containing only the suppressed checks...")
            try:
                with open(str(self.input_args.isSuppressed_folder) + 'isSuppressed_with_resource-ids.csv', mode="wb") as f:
                    f.write(suppressed_file_data)
            except Exception as e:
                print(e)

    def not_suppressed_split_by_account(self):
        files_dict = {}

        logging.info("Parsing the not suppressed csv file to split it by account...")
        with open(str(self.input_args.isSuppressed_folder) + "NOT_Suppressed_with_resource-ids.csv", mode="r") as f:
            f.readline()
            for line in f:
                account = line.split(',')[2].strip('\n')
                if account in files_dict:
                    files_dict[account].append(line)
                else:
                    files_dict[account] = [line]

        if not os.path.exists(self.input_args.isSuppressed_folder + 'NOT_Suppressed_split_by_account'):
            logging.info("Creating the directory NOT_Suppressed_split_by_account...")
            os.makedirs(self.input_args.isSuppressed_folder + 'NOT_Suppressed_split_by_account')

        logging.info("Writing the the not suppressed csv files splitted by account...")
        for account, lines in files_dict.items():
            if not os.path.exists(self.input_args.isSuppressed_folder + 'NOT_Suppressed_split_by_account/' + account):
                os.makedirs(self.input_args.isSuppressed_folder + 'NOT_Suppressed_split_by_account/'  + account)

            account_dict = {}

            for line in lines:
                checkname = line.split(',')[5].strip('\n')
                if checkname in account_dict:
                    account_dict[checkname].append(line)
                else:
                    account_dict[checkname] = [line]

            for checkname, lines_list in account_dict.items():
                columns_line = self.get_unfiltered_split_by_checkname_file_columns(checkname)
                lines_list.insert(0, columns_line)

            for check, lines in account_dict.items():
                file_data = "".join(lines)
                try:
                    with open(self.input_args.isSuppressed_folder + 'NOT_Suppressed_split_by_account/' + account + '/' + check + '.csv',
                              mode="w") as f:
                        f.write(file_data)
                except Exception as e:
                    print(e)

    def not_suppressed_split_by_check_name(self):
        files_dict = {}
        logging.info("Parsing the not suppressed csv file to split it by check name...")
        with open(str(self.input_args.isSuppressed_folder) + 'NOT_Suppressed_with_resource-ids.csv', mode="r") as f:
            f.readline()
            for line in f:
                checkname = line.split(',')[5].strip('\n')
                if checkname in files_dict:
                    files_dict[checkname].append(line)
                else:
                    files_dict[checkname] = [line]

        for checkname, lines_list in files_dict.items():
            columns_line = self.get_unfiltered_split_by_checkname_file_columns(checkname)
            lines_list.insert(0, columns_line)

        if not os.path.exists(self.input_args.isSuppressed_folder + 'NOT_Suppressed_split_by_checkname'):
            logging.info("Creating the directory NOT_Suppressed_split_by_checkname...")
            os.makedirs(self.input_args.isSuppressed_folder + 'NOT_Suppressed_split_by_checkname')

        logging.info("Writing the not suppressed csv files splitted by check name...")
        for check, lines in files_dict.items():
            file_data = "".join(lines)
            try:
                with open(self.input_args.isSuppressed_folder + 'NOT_Suppressed_split_by_checkname/' + check + '.csv',
                          mode="w") as f:
                    f.write(file_data)
            except Exception as e:
                print(e)

    def get_unfiltered_split_by_checkname_file_columns(self, checkname):
        ordered_colums = "CheckId,Account-Id,Account Display Name,TA Category,Status External,TA Check Name,Region,isSuppressed,---,"
        if checkname == 'Amazon Aurora DB Instance Accessibility':
            return ordered_colums + "Status,Region,ClusterName,publicCount,privateCount,Reason\n"
        elif checkname == 'Amazon EBS Provisioned IOPS (SSD) Volume Attachment Configuration':
            return ordered_colums + "Availability Zone,Volume-Id,VolumeName,Attachment,Instance-Id,Instance-Type,EBS Optimization Completed,Status\n"
        elif checkname == 'Amazon EBS Public Snapshots':
            return ordered_colums + "Status,Region,Volume-Id,Snapshot-Id\n"
        elif checkname == 'Amazon EBS Snapshots':
            return ordered_colums + "Region,Volume-Id,VolumeName,Snapshot-Id,Snapshot-Name,Snapshot-Days,Attachment,Status,Reason\n"
        elif checkname == 'Amazon EC2 Availability Zone Balance':
            return ordered_colums + "Region,ZoneA,ZoneB,ZoneC,ZoneD,ZoneE,ZoneF,Status,Reason\n"
        elif checkname == 'Amazon EC2 Reserved Instance Lease Expiration':
            return ordered_colums + "Status,Availability Zone,Instance-Type,Operating System,Current RI Count,Current Monthly Cost,Monthly Savings,Expiration Date/Time,Reservation-Id,Reason\n"
        elif checkname == 'Amazon EC2 Reserved Instances Optimization':
            return ordered_colums + "Availability Zone,Instance-Type,Operating System,One year Current RI Count,Instances Usage Stats MAX/AVG/MIN,Recommended One Year Buy count,Monthly Current Cost,One Year Partial Upfront Fee, Monthly Optimal Cost,Monthly Savings,Availability Zone,Instance-Type,Operating System,Three years Current RI Count,Instances Usage Stats MAX/AVG/MIN,Recommended Three Years Buy count,Monthly Current Cost,Three Years Partial Upfront Fee, Monthly Optimal Cost,Monthly Savings\n"
        elif checkname == 'Amazon EC2 to EBS Throughput Optimization':
            return ordered_colums + "Region,Instance-Id,Instance-Type,Time Near Maximum,Status\n"
        elif checkname == 'Amazon RDS Backups':
            return ordered_colums + "Availability Zone,RDS Instance-Id,VPC-Id,Retention Period,Status\n"
        elif checkname == 'Amazon RDS Idle DB Instances':
            return ordered_colums + "Region,RDS Instance-Name,Multi-AZ,RDS Instance-Type,Storage Size GB,Days Since Last Connection,Estimated Monthly Savings\n"
        elif checkname == 'Amazon RDS Multi-AZ':
            return ordered_colums + "Availability Zone,RDS Instance-Name,VPC-Id,Multi-AZ,Status\n"
        elif checkname == 'Amazon RDS Security Group Access Risk':
            return ordered_colums + "Region,Group Name,Ingress Rule,Status,Reason\n"
        elif checkname == 'Amazon Route 53 Alias Resource Record Sets':
            return ordered_colums + "hostedZoneName,hostedZoneId,resourceRecordSetName,resourceRecordSetType,resourceRecordSetIdentifier,aliasTarget,Status\n"
        elif checkname == 'Amazon Route 53 High TTL Resource Record Sets':
            return ordered_colums + "hostedZoneName,hostedZoneId,resourceRecordSetName,resourceRecordSetType,resourceRecordSetIdentifier,TTL,Status\n"
        elif checkname == 'Amazon Route 53 MX Resource Record Sets and Sender Policy Framework':
            return ordered_colums + "hostedZoneName,hostedZoneId,resourceRecordSetName\n"
        elif checkname == 'Amazon Route 53 Name Server Delegations':
            return ordered_colums + "hostedZoneName,hostedZoneId,configuredDelegationCount\n"
        elif checkname == 'Amazon S3 Bucket Logging':
            return ordered_colums + "Region,bucketName,targetBucket,targetExists,targetSameOwner,targetWriteEnabled,Status,Reason\n"
        elif checkname == 'Amazon S3 Bucket Permissions':
            return ordered_colums + "regionDisplayName,regionPrefix,bucketName,hasGlobalListAccess,hasGlobalUploadDeleteAccess,Status,vulnerable-policy,AdditionalInfo\n"
        elif checkname == 'Amazon S3 Bucket Versioning':
            return ordered_colums + "Region,bucketName,versioningStatus,mfaDeleteEnabled,Status\n"
        elif checkname == 'Auto Scaling Group Health Check':
            return ordered_colums + "Region,aSGName,ELB Active,healthCheckType,Status\n"
        elif checkname == 'Auto Scaling Group Resources':
            return ordered_colums + "Region,aSGName,lcName,resourceType,resourceName,Status,Reason\n"
        elif checkname == 'AWS CloudTrail Logging':
            return ordered_colums + "Region,trailName,Logging,s3BucketName,s3DeliveryError,Status\n"
        elif checkname == 'CloudFront Alternate Domain Names':
            return ordered_colums + "Status,distributionId,distributionDomainName,CNAME,Reason\n"
        elif checkname == 'CloudFront Content Delivery Optimization':
            return ordered_colums + "Region,bucketName,StorageSize,transferSize,Ratio,Status\n"
        elif checkname == 'CloudFront Custom SSL Certificates in the IAM Certificate Store':
            return ordered_colums + "Status,distributionId,distributionDomainName,certificateName,Reason\n"
        elif checkname == 'CloudFront Header Forwarding and Cache Hit Ratio':
            return ordered_colums + "Status,distributionId,distributionDomainName,cacheBehaviorPath,inefficientHeaders\n"
        elif checkname == 'ELB Connection Draining':
            return ordered_colums + "Region,ELBName,Status,Reason\n"
        elif checkname == 'ELB Cross-Zone Load Balancing':
            return ordered_colums + "Region,ELBName,Status,Reason\n"
        elif checkname == 'ELB Listener Security':
            return ordered_colums + "Region,ELBName,Port,Status,Reason\n"
        elif checkname == 'ELB Security Groups':
            return ordered_colums + "Region,ELBName,Status,SecurityGroup(s),Reason\n"
        elif checkname == 'IAM Access Key Rotation':
            return ordered_colums + "Status,iamUser,IAMAccessKey,lastRotatedTime,Reason\n"
        elif checkname == 'IAM Password Policy':
            return ordered_colums + "passwordPolicyEnabled,requireUppercase,requireLowercase,requireNumbers,requireSymbols,Status,Reason\n"
        elif checkname == 'IAM Use':
            return ordered_colums.strip(',') + "\n"
        elif checkname == 'Idle Load Balancers':
            return ordered_colums + "Region,ELBName,Reason,MonthlyCostSaving\n"
        elif checkname == 'Large Number of EC2 Security Group Rules Applied to an Instance':
            return ordered_colums + "Region,instanceId,Instance-Name,vpcId,inboundRuleCount,outboundRuleCount\n"
        elif checkname == 'Load Balancer Optimization ':
            return ordered_colums + "Region,ELBName,numberOfZones,ZoneA,ZoneB,ZoneC,ZoneD,ZoneE,ZoneF,Status,Reason\n"
        elif checkname == 'Low Utilization Amazon EC2 Instances':
            return ordered_colums + "Availability Zone,Instance-Id,InstanceName,Instance-Type,Average Monthly Cost,AvgCPUUtil%/NetUtilMB-Day1,AvgCPUUtil%/NetUtilMB-Day2,AvgCPUUtil%/NetUtilMB-Day3,AvgCPUUtil%/NetUtilMB-Day4,AvgCPUUtil%/NetUtilMB-Day5,AvgCPUUtil%/NetUtilMB-Day6,AvgCPUUtil%/NetUtilMB-Day7,AvgCPUUtil%/NetUtilMB-Day8,AvgCPUUtil%/NetUtilMB-Day9,AvgCPUUtil%/NetUtilMB-Day10,AvgCPUUtil%/NetUtilMB-Day11,AvgCPUUtil%/NetUtilMB-Day12,AvgCPUUtil%/NetUtilMB-Day13,AvgCPUUtil%/NetUtilMB-Day14,14DAvgCPUUtil%,14DNetUtilMB,daysUnderUtilized\n"
        elif checkname == 'MFA on Root Account':
            return ordered_colums.strip(',') + "\n"
        elif checkname == 'Overutilized Amazon EBS Magnetic Volumes':
            return ordered_colums + "Region,volumeId,Name,AvgIOPSsec/Usage%-Day1,AvgIOPSsec/Usage%-Day2,AvgIOPSsec/Usage%-Day3,AvgIOPSsec/Usage%-Day4,AvgIOPSsec/Usage%-Day5,AvgIOPSsec/Usage%-Day6,AvgIOPSsec/Usage%-Day7,AvgIOPSsec/Usage%-Day8,AvgIOPSsec/Usage%-Day9,AvgIOPSsec/Usage%-Day10,AvgIOPSsec/Usage%-Day11,AvgIOPSsec/Usage%-Day12,AvgIOPSsec/Usage%-Day13,AvgIOPSsec/Usage%-Day14,daysOverUtilized,MaxIOPS,Status\n"
        elif checkname == 'Security Groups - Specific Ports Unrestricted':
            return ordered_colums + "Region,SGName,sg-Id,Protocol,Status,Port\n"
        elif checkname == 'Security Groups - Unrestricted Access':
            return ordered_colums + "Region,SGName,sg-Id,Protocol,Port,Status,Addresses\n"
        elif checkname == 'Service Limits':
            return ordered_colums + "Region,Service,LimitName,Limit,Usage,Status\n"
        elif checkname == 'Unassociated Elastic IP Addresses':
            return ordered_colums + "Region,IPAddress\n"
        elif checkname == 'Underutilized Amazon EBS Volumes':
            return ordered_colums + "Region,volumeId,volumeName,volumeType,volumeSize,currentMonthlyCost,snapshotId,snapshotName,snapshotAge\n"
        elif checkname == 'Underutilized Amazon Redshift Clusters':
            return ordered_colums + "Status,Region,ClusterName,ClusterType,Reason,estimatedMonthlySavings\n"
        elif checkname == 'VPN Tunnel Redundancy':
            return ordered_colums + "Region,VPNId,VPCId,virtualPrivateGatewayID,customerGatewayID,tunnelCount,Status,Reason\n"
        elif checkname == 'Amazon Route 53 Failover Resource Record Sets':
            return ordered_colums + "hostedZoneName,hostedZoneId,resourceRecordSetName,resourceRecordSetType,improperFailoverType\n"
        elif checkname == 'Auto Scaling Groups':
            return ordered_colums + "Region,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'Auto Scaling Launch Configurations':
            return ordered_colums + "Region,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'CloudFormation Stacks':
            return ordered_colums + "Region,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'EBS Active Snapshots':
            return ordered_colums + "Region,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'EBS Active Volumes':
            return ordered_colums + "Region,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'EBS General Purpose SSD (gp2) Volume Storage':
            return ordered_colums + "Region,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'EBS Magnetic (standard) Volume Storage':
            return ordered_colums + "Region,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'EBS Provisioned IOPS (SSD) Volume Aggregate IOPS':
            return ordered_colums + "Region,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'EBS Provisioned IOPS SSD (io1) Volume Storage':
            return ordered_colums + "Region,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'EC2 Elastic IP Addresses':
            return ordered_colums + "Region,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'EC2 On-Demand Instances':
            return ordered_colums + "Region,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'EC2 Reserved Instance Leases':
            return ordered_colums + "Region,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'EC2Config Service for EC2 Windows Instances':
            return ordered_colums + "Status,Region,Timestamp,Instance-id,InstanceTag,ConfigStatus\n"
        elif checkname == 'ELB Active Load Balancers':
            return ordered_colums + "Region,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'IAM Group':
            return ordered_colums + "-,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'IAM Instance Profiles':
            return ordered_colums + "-,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'IAM Policies':
            return ordered_colums + "-,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'IAM Roles':
            return ordered_colums + "-,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'IAM Server Certificates':
            return ordered_colums + "-,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'IAM Users':
            return ordered_colums + "-,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'Kinesis Shards per Region':
            return ordered_colums + "Region,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'Large Number of Rules in an EC2 Security Group':
            return ordered_colums + "Region,GroupName,Group-Id,Description,InstancesCount,Vpc-Id,InboundRulesCount,OutboundRulesCount\n"
        elif checkname == 'PV Driver Version for EC2 Windows Instances':
            return ordered_colums + "Status,Region,Timestamp,Instance-id,ConfigStatus\n"
        elif checkname == 'RDS Cluster Parameter Groups':
            return ordered_colums + "Region,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'RDS Clusters':
            return ordered_colums + "Region,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'RDS DB Instances':
            return ordered_colums + "Region,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'RDS DB Parameter Groups':
            return ordered_colums + "Region,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'RDS DB Security Groups':
            return ordered_colums + "Region,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'RDS DB Snapshots Per User':
            return ordered_colums + "Region,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'RDS Max Auths per Security Group':
            return ordered_colums + "Region,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'RDS Option Groups':
            return ordered_colums + "Region,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'RDS Read Replicas per Master':
            return ordered_colums + "Region,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'RDS Reserved Instances':
            return ordered_colums + "Region,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'RDS Subnet Groups':
            return ordered_colums + "Region,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'RDS Subnets per Subnet Group':
            return ordered_colums + "Region,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'RDS Total Storage Quota':
            return ordered_colums + "Region,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'RDS Event Subscriptions':
            return ordered_colums + "Region,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'SES Daily Sending Quota':
            return ordered_colums + "Region,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'VPC Elastic IP Address':
            return ordered_colums + "Region,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'VPC Internet Gateways':
            return ordered_colums + "Region,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'VPC Network Interfaces':
            return ordered_colums + "Region,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'AWS Direct Connect Connection Redundancy':
            return ordered_colums + "Status,Region,Timestamp,Location,ConnectionId\n"
        elif checkname == 'AWS Direct Connect Location Redundancy':
            return ordered_colums + "Status,Region,Timestamp,Location,ConnectionSpeed\n"
        elif checkname == 'AWS Direct Connect Virtual Interface Redundancy':
            return ordered_colums + "Status,Region,Timestamp,vGateway,Location,ConnectionId\n"
        elif checkname == 'Amazon Route 53 Deleted Health Checks':
            return ordered_colums + "hostedZoneName,hostedZoneId,resourceRecordSetName,resourceRecordSetType,resourceRecordSetIdentifier\n"
        elif checkname == 'Amazon Route 53 Latency Resource Record Sets':
            return ordered_colums + "hostedZoneName,hostedZoneId,resourceRecordSetName,resourceRecordSetType\n"
        elif checkname == 'CloudFront SSL Certificate on the Origin Server':
            return ordered_colums + "Status,distributionId,distributionDomainName,originName,Reason\n"
        elif checkname == 'High Utilization Amazon EC2 Instances':
            return ordered_colums + "Availability Zone,Instance-Id,InstanceName,Instance-Type,AvgCPUUtil%-Day1,AvgCPUUtil%-Day2,AvgCPUUtil%-Day3,AvgCPUUtil%-Day4,AvgCPUUtil%-Day5,AvgCPUUtil%-Day6,AvgCPUUtil%-Day7,AvgCPUUtil%-Day8,AvgCPUUtil%-Day9,AvgCPUUtil%-Day10,AvgCPUUtil%-Day11,AvgCPUUtil%-Day12,AvgCPUUtil%-Day13,AvgCPUUtil%-Day14,14DAvgCPUUtil%,daysOverUtilized\n"
        elif checkname == 'EBS Throughput Optimized HDD (st1) Volume Storage':
            return ordered_colums + "Region,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'EBS Cold HDD (sc1) Volume Storage':
            return ordered_colums + "Region,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'VPC':
            return ordered_colums + "Region,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'RDS Cluster Roles':
            return ordered_colums + "Region,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'Exposed Access Keys':
            return ordered_colums + "accessKey,userName,fraudType,caseId,timeUpdated,location,deadline,usage\n"
        elif checkname == 'DynamoDB Read Capacity':
            return ordered_colums + "Region,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'DynamoDB Write Capacity':
            return ordered_colums + "Region,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'ENA Driver Version for EC2 Windows Instances':
            return ordered_colums + "Status,Region,Last_Time_Driver_Loaded,InstanceId,Reason\n"
        elif checkname == 'NVMe Driver Version for EC2 Windows Instances':
            return ordered_colums + "Status,Region,Last_Time_Driver_Loaded,InstanceId,Reason\n"
        elif checkname == 'Route 53 Hosted Zones':
            return ordered_colums + "Region,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'Route 53 Max Health Checks':
            return ordered_colums + "Region,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'Route 53 Reusable Delegation Sets':
            return ordered_colums + "Region,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'Route 53 Traffic Policies':
            return ordered_colums + "Region,Service,Limit_Checked,Limit,Usage,Status\n"
        elif checkname == 'Route 53 Traffic Policy Instances':
            return ordered_colums + "Region,Service,Limit_Checked,Limit,Usage,Status\n"
        else:
            return "Unable to identify the CheckName Columns!\n"

    def write_relevant_savings(self):
        datalist = []
        idle_ELB_dict = {}
        idle_RDS_dict = {}
        low_util_EC2_dict = {}
        low_util_EBS_dict = {}
        low_util_Redshift_dict = {}
        logging.info("Parsing the unfiltered full csv file to calculate relevant savings...")
        with open(self.input_args.unfiltered_folder + 'full_report_with_resource-ids.csv', mode="r") as f:
            next(f)
            reader = csv.reader(f)
            for line in reader:
                try:
                    checkname = line[5]
                    if checkname == 'Idle Load Balancers':
                        reason = line[11]
                        line_savings = float(line[12].strip('\n').replace("$", "").replace("\"", "").replace(",", ""))
                        if reason in idle_ELB_dict:
                            idle_ELB_dict[reason] = idle_ELB_dict.get(reason) + line_savings
                        else:
                            idle_ELB_dict[reason] = 0 + line_savings
                    elif checkname == 'Amazon RDS Idle DB Instances':
                        reason = "14+ Days Since Last Connection"
                        line_savings = float(line[15].strip('\n').replace("$", "").replace("\"", "").replace(",", ""))
                        if "14+" in line[14] and reason in idle_RDS_dict:
                            idle_RDS_dict[reason] = idle_RDS_dict.get(reason) + line_savings
                        elif "14+" in line[14] and reason not in idle_RDS_dict:
                            idle_RDS_dict[reason] = 0 + line_savings
                    elif checkname == 'Low Utilization Amazon EC2 Instances':
                        line_savings = float(line[13].strip('\n').replace("$", "").replace("\"", "").replace(",", ""))
                        if checkname in low_util_EC2_dict:
                            low_util_EC2_dict[checkname] = low_util_EC2_dict.get(checkname) + line_savings
                        else:
                            low_util_EC2_dict[checkname] = 0 + line_savings
                    elif checkname == 'Underutilized Amazon EBS Volumes':
                        line_savings = float(line[14].strip('\n').replace("$", "").replace("\"", "").replace(",", ""))
                        if checkname in low_util_EBS_dict:
                            low_util_EBS_dict[checkname] = low_util_EBS_dict.get(checkname) + line_savings
                        else:
                            low_util_EBS_dict[checkname] = 0 + line_savings
                    elif checkname == 'Underutilized Amazon Redshift Clusters':
                        line_savings = float(line[14].strip('\n').replace("$", "").replace("\"", "").replace(",", ""))
                        if checkname in low_util_Redshift_dict:
                            low_util_Redshift_dict[checkname] = low_util_Redshift_dict.get(checkname) + line_savings
                        else:
                            low_util_Redshift_dict[checkname] = 0 + line_savings
                except Exception as e:
                    logging.warning("Possible issue in the sum of the data calculating the relevant cost savings!")
                    logging.error(e)
                    continue


        datalist.append(
            'Low Utilization Amazon EC2 Instances,An instance had 10% or less daily average CPU utilization and 5 MB or less network I/O on at least 4 of the previous 14 days.,' + (str(
                low_util_EC2_dict.get('Low Utilization Amazon EC2 Instances')) if (low_util_EC2_dict.get('Low Utilization Amazon EC2 Instances') is not None) else str(0)))
        datalist.append('Underutilized Amazon EBS Volumes,A volume is unattached or had less than 1 IOPS per day for the past 7 days.,' + (str(low_util_EBS_dict.get('Underutilized Amazon EBS Volumes'))))
        datalist.append(
            'RDS Idle DB Instances,An active DB instance has not had a connection in the last 14 days.,' + (str(
                idle_RDS_dict.get('14+ Days Since Last Connection')) if (idle_RDS_dict.get('14+ Days Since Last Connection') is not None) else str(0)))
        datalist.append(
            'Idle Load Balancers:No active back-end instances,A load balancer has no active back-end instances.,' + (str(
                idle_ELB_dict.get('No active back-end instances')) if (idle_ELB_dict.get('No active back-end instances') is not None) else str(0)))
        datalist.append(
            'Idle Load Balancers:No healthy back-end instances,A load balancer has no healthy back-end instances.,' + (str(
                idle_ELB_dict.get('No healthy back-end instances')) if (idle_ELB_dict.get('No healthy back-end instances') is not None) else str(0)))
        datalist.append(
            'Idle Load Balancers:Low request count,A load balancer has had less than 100 requests per day for the last 7 days.,' + (str(
                idle_ELB_dict.get('Low request count')) if (idle_ELB_dict.get('Low request count') is not None) else str(0)))
        datalist.append(
            'Underutilized Amazon Redshift Clusters,A running cluster has not had a connection in the last 7 days or a running cluster had less than 5% cluster-wide average CPU utilization for 99% of the last 7 days.,' + (str(
                low_util_Redshift_dict.get('Underutilized Amazon Redshift Clusters'))))
        datalist.append("\n,Total Estimated Monthly Savings in $,=SUM(C2:C8)")

        file_data = "\n".join(datalist).encode('utf-8')
        logging.info("Writing the file containing the relevant savings from the Cost Optimization pillar...")
        try:
            with open(str(self.input_args.relevant_savings_folder) + "relevant_savings.csv",
                      mode="wb") as f:
                f.write(
                    b"Check,Description,Estimated Monthly Savings in $\n")
                f.write(file_data)
        except Exception as e:
            print("EXCEPTION Writing the file containing the relevant savings:" +str(e))
