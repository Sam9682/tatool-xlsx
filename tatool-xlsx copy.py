import pdb
from tkinter.font import names
import xlsxwriter, csv, glob2, os, sys, re, string, boto3, subprocess, logging, datetime, argparse, dateparser, datetime
from datetime import date
import pandas as pd
from pathlib import Path
from zipfile import ZipFile
from colorama import init
from datetime import datetime, timedelta
import tatool
import glob2
import pick
from pick import pick
import pathlib
import tabulate as tabulate

v_NAME = "name"
v_THREAD = "20"
v_DIR_ACCOUNT= "."
v_LIST_ACCOUNTS_FILE = v_DIR_ACCOUNT + "/accounts.csv"
v_S3_BUCKET = "sam-bucket-production-tatool"
v_TODAY_DATETIME = date.today().strftime("%Y-%m-%d") 
v_MONTH_DATETIME = date.today().strftime("%b-%Y") 
v_FULL_DATETIME = datetime.today().strftime("%Y-%m-%d-%H-%M-%S") 
v_SECURITY_CSV = "/unfiltered/sc_rpt"
v_FAULT_TOLERANCE_CSV = "/unfiltered/ft_rpt"
v_COST_OPTIM_CSV = "/unfiltered/co_rpt"
v_COST_OPTIM_FULL = "/unfiltered/co_full"
v_SPECIFIC_SOCGEN = False
v_RIGHT_SIZING = False
v_COST_EIP_UNUSED = 3.72

CONST_DOMAIN = 'DOMAIN'
CONST_PAYERID = 'PAYERID'
CONST_ACCOUNTID = 'ACCOUNTID'
CONST_ACCOUNTS_LIST_FILENAME = './accounts.csv'
CONST_ACCOUNTS_LIST_FILENAME_JSON = './accounts.json'

CONST_NAME_SHEETS = [
    '0-Cost_Pillar',
    '1-Security_Pillar',
    '2-Fault_Tolerance_Pillar',
    '3-EC2_RightSizing',
    '4-Underutilized_EBS',
    '5-Idle_RDS_DB',
    '6-Idle_Load_Balancer',
    '7-Unassociated_IP',
    '8-Saving_Plans',
    '9-Rds_RI',
    '10-ElastiCache_RI'
    ]

CONST_NAME_SHEETS_RS = [
    '0-Cost_Pillar',
    '1-Security_Pillar',
    '2-Fault_Tolerance_Pillar',
    '3-EC2_RightSizing',
    '4-Underutilized_EBS',
    '5-Idle_RDS_DB',
    '6-Idle_Load_Balancer',
    '7-Unassociated_IP',
    '8-Saving_Plans',
    '9-Rds_RI',
    '10-ElastiCache_RI'
    ]
#----------------------------------------------------------------------------------------------------------------------------------------------------
# CONFIGURATION OF EC2 RIGHTSIZING FILE STRUCTURE
#----------------------------------------------------------------------------------------------------------------------------------------------------
CONST_RIGHTSIZING_FILENAME = 'ec2-rightsizing-recommendations.csv'
CONST_RIGHTSIZING_FILENAME_STAR = '/unfiltered/ec2-rightsizing-recommendations*.csv'
CONST_FULL_REPORT_RIGHTSIZING = "/unfiltered/" + CONST_RIGHTSIZING_FILENAME

CONST_CO_ERSR = 'EC2 RightSizing Recommendations'
# Account ID	Account name	Instance ID	Finding reason(s)	Instance name	Instance type	OS	Region	user:Name	Total running hours	RI hours	On-Demand hours	Savings Plans hours	CPU utilization	Memory utilization	Disk utilization	EBS read (Ops/s)	EBS write (Ops/s)	EBS read throughput (KiB/s)	EBS write throughput (KiB/s)	Disk read (Ops/s)	Disk write (Ops/s)	Disk read throughput (KiB/s)	Disk write throughput (KiB/s)	Network in (KiB/s)	Network out (KiB/s)	Network packets in (Packets/s)	Network packets out (Packets/s)	Recommended action	Recommended instance type 1	Recommended instance type 1 Estimated savings	Recommended instance type 1 Projected CPU utilization	Recommended instance type 1 Projected memory utilization	Recommended instance type 1 Projected disk utilization	Recommended instance type 1 Platform difference(s)	Recommended instance type 2	Recommended instance type 2 Estimated savings	Recommended instance type 2 Projected CPU utilization	Recommended instance type 2 Projected memory utilization	Recommended instance type 2 Projected disk utilization	Recommended instance type 2 Platform difference(s)	Recommended instance type 3	Recommended instance type 3 Estimated savings	Recommended instance type 3 Projected CPU utilization	Recommended instance type 3 Projected memory utilization	Recommended instance type 3 Projected disk utilization	Recommended instance type 3 Platform difference(s)
CONST_HEADER_ERCR = ["AccountID","Accountname","InstanceID","Check","Instancename","InstanceType","OS","Region","userName","Totalrunninghours","RIhours","On-Demandhours","SavingsPlanshours","CPUutilization","Memoryutilization","Diskutilization","EBSreadOpss","EBSwriteOpss","EBSreadthroughputKiBs","EBSwritethroughputKiBs)","DiskreadOpss","DiskwriteOpss","DiskreadthroughputKiBs","DiskwritethroughputKiBs","NetworkinKiBs","NetworkoutKiBs","NetworkpacketsinPacketss","NetworkpacketsoutPacketss","Recommendedaction","Recommendedinstancetype1","EstimatedMonthlySavings","Recommendedinstancetype1ProjectedCPUutilization","Recommendedinstancetype1Projectedmemoryutilization","Recommendedinstancetype1Projecteddiskutilization","Recommendedinstancetype1Platformdifferences","Recommendedinstancetype2","Recommendedinstancetype2Estimatedsavings","Recommendedinstancetype2ProjectedCPUutilization","Recommendedinstancetype2Projectedmemoryutilization","Recommendedinstancetype2Projecteddiskutilization","Recommendedinstancetype2Platformdifferences","Recommendedinstancetype3","Recommendedinstancetype3Estimatedsavings","Recommendedinstancetype3ProjectedCPUutilization","Recommendedinstancetype3Projectedmemoryutilization","Recommendedinstancetype3Projecteddiskutilization","Recommendedinstancetype3Platformdifferences"]
CONST_CO_ERCR_FIELDS = [i for i in range(len(CONST_HEADER_ERCR))]


#----------------------------------------------------------------------------------------------------------------------------------------------------
# CONFIGURATION OF TATOOL FILE STRUCTURE
#----------------------------------------------------------------------------------------------------------------------------------------------------
CONST_GLOBAL_FIRST_LINE_XLS = "Check,Status"
CONST_GLOBAL_FIRST_LINE_XLS_LIST = ["Check","Status","TACategory"]
CONST_COST_PILLAR_FIRST_LINE_XLS_LIST = ["CostDomain","CostType"]
CONST_GLOBAL_COLUMNS_XLS_LIST = ["Status","Check","TACategory"]
CONST_COST_PILLAR_COLUMNS_XLS_LIST0 = ["CostDomain","CostType","X", "EstimatedMonthlySavings"] 
CONST_COST_PILLAR_COLUMNS_XLS_LIST = ["CostDomain","CostType","X", "Y", "EstimatedMonthlySavings"] 
CONST_COST_PILLAR_COLUMNS_XLS_LIST2 = ["CostDomain","CostType","X", "Y", "Z", "EstimatedMonthlySavings"] 
CONST_COST_PILLAR_COLUMNS_XLS_LIST3 = ["CostDomain","CostType","EstimatedMonthlySavings"] 
CONST_GLOBAL_FIRST_LINE_XLS_LIST_CO = ["Check","Subtype","Account","Number of"]
CONST_FULL_REPORT_RESOURCE = "/unfiltered/full_report_with_resource-ids.csv"
CONST_HEADER_CSV_TATOOL = ["CheckId","AccountId","AccountName","TACategory","Status","Check","Region","isSuppressed"]

CONST_SC = 'security'
CONST_FT = 'fault_tolerance'
CONST_CO = 'cost-optimization'


CONST_CO_LUAEI = 'Low Utilization Amazon EC2 Instances'
#Region/AZ	Instance ID	Instance Name	Instance Type	Estimated Monthly Savings	Day 1	Day 2	Day 3	Day 4	Day 5	Day 6	Day 7	Day 8	Day 9	Day 10	Day 11	Day 12	Day 13	Day 14	14-Day Average CPU Utilization	14-Day Average Network I/O	Number of Days Low Utilization
CONST_HEADER_LUAEI = ["CheckId","AccountId","AccountName","TACategory","Status","Check","Region","isSuppressed","COL8","COL9","ResourceId","ResourceName","InstanceType","EstimatedMonthlySavings"]
CONST_CO_LUAEI_FIELDS = [i for i in range(len(CONST_HEADER_LUAEI))]

CONST_CO_UUAEV = 'Underutilized Amazon EBS Volumes'
#Region	Volume ID	Volume Name	Volume Type	Volume Size	Monthly Storage Cost	Snapshot ID	Snapshot Name	Snapshot Age
CONST_HEADER_UUAEV = ["CheckId","AccountId","AccountName","TACategory","Status","Check","Region","isSuppressed","COL8","COL9","ResourceId","ResourceName","VolumeType","VolumeSize","EstimatedMonthlySavings","SnapshotId"]
CONST_CO_UUAEV_FIELDS = [i for i in range(len(CONST_HEADER_UUAEV))]

CONST_CO_ARIDI = 'Amazon RDS Idle DB Instances'
#Region	DB Instance Name	Multi-AZ	Instance Type	Storage Provisioned (GB)	Days Since Last Connection	Estimated Monthly Savings (On Demand)
CONST_HEADER_ARIDI = ["CheckId","AccountId","AccountName","TACategory","Status","Check","Region","isSuppressed","COL8","COL9","ResourceId","MultiAZ","InstanceType","StorageProvisionedInGb","DaysSinceLastConnection","EstimatedMonthlySavings"]
CONST_CO_ARIDI_FIELDS = [i for i in range(len(CONST_HEADER_ARIDI))]

CONST_CO_ILB = 'Idle Load Balancers'
#Region	Load Balancer Name	Reason	Estimated Monthly Savings
CONST_HEADER_ILB = ["CheckId","AccountId","AccountName","TACategory","Status","Check","Region","isSuppressed","COL8","COL9","ResourceId","Reason","EstimatedMonthlySavings"]
CONST_CO_ILB_FIELDS = [i for i in range(len(CONST_HEADER_ILB))]

CONST_CO_UEIA = 'Unassociated Elastic IP Addresses'
#Region	IP Address
CONST_HEADER_UEIA = ["CheckId","AccountId","AccountName","TACategory","Status","Check","Region","isSuppressed","COL8","COL9","ResourceId","EstimatedMonthlySavings"]
CONST_CO_UEIA_FIELDS = [i for i in range(len(CONST_HEADER_UEIA))]

CONST_CO_UARC = 'underutilized amazon redshift clusters'
#Status	Region	Cluster	Instance Type	Reason	Estimated Monthly Savings
CONST_HEADER_UARC = ["CheckId","AccountId","AccountName","TACategory","Status","Check","Region","isSuppressed","COL8","COL9","ResourceId","InstanceType","Reason","EstimatedMonthlySavings"]
CONST_CO_UARC_FIELDS = [i for i in range(len(CONST_HEADER_UARC))]

CONST_CO_AECRNO = 'Amazon ElastiCache Reserved Node Optimization'
#Region	Family	Node Type	Product Description	Recommended number of Reserved Nodes to purchase	Expected Average Reserved Node Utilization	Estimated Savings with Recommendation (monthly)	Upfront Cost of Reserved Nodes	Estimated cost of Reserved Nodes (monthly)	Estimated On-Demand Cost Post Recommended Reserved Nodes Purchase (monthly)	Estimated Break Even (months)	Lookback Period (days)	Term (years)
CONST_HEADER_AECRNO = ["CheckId","AccountId","AccountName","TACategory","Status","Check","Region","isSuppressed","COL8","COL9","Family","InstanceType","ProductDescription","RecommendedNumberToPurchase","ExpectedAverageUtilization","EstimatedMonthlySavings","UpfrontCost","COL17","EstimatedCostOfReservedNodesMonthly","EstimatedBreakEvenInMonths","LookbackPeriodInDays","TermInYears"]
CONST_CO_AECRNO_FIELDS = [i for i in range(len(CONST_HEADER_AECRNO))]

CONST_CO_AERIO = 'Amazon Elasticsearch Reserved Instance Optimization'
#Region	Instance Class	Instance Size	Recommended number of Reserved Instances to purchase	Expected Average Reserved Instance Utilization	Estimated Savings with Recommendation (monthly)	Upfront Cost of Reserved Instances	Estimated cost of Reserved Instances (monthly)	Estimated On-Demand Cost Post Recommended Reserved Instance Purchase (monthly)	Estimated Break Even (months)	Lookback Period (days)	Term (years)
CONST_HEADER_AERIO = ["CheckId","AccountId","AccountName","TACategory","Status","Check","Region","isSuppressed","COL8","COL9","Family","InstanceType","RecommendedNumberToPurchase","ExpectedAverageUtilization","EstimatedMonthlySavings","UpfrontCost","EstimatedCostOfReservedInstancesMonthly","EstimatedBreakEvenInMonths","LookbackPeriodInDays","TermInYears"]
CONST_CO_AERIO_FIELDS = [i for i in range(len(CONST_HEADER_AERIO))]

CONST_CO_ARRNO = 'amazon redshift reserved node optimization'
#Region	Family	Node Type	Recommended number of Reserved Nodes to purchase	Expected Average Reserved Node Utilization	Estimated Savings with Recommendation (monthly)	Upfront Cost of Reserved Nodes	Estimated cost of Reserved Nodes (monthly)	Estimated On-Demand Cost Post Recommended Reserved Nodes Purchase (monthly)	Estimated Break Even (months)	Lookback Period (days)	Term (years)
CONST_HEADER_ARRNO = ["CheckId","AccountId","AccountName","TACategory","Status","Check","Region","isSuppressed","COL8","COL9","Family","InstanceType","RecommendedNumberToPurchase","ExpectedAverageUtilization","EstimatedMonthlySavings","UpfrontCost","EstimatedCostOfReservedNodesMonthly","EstimatedBreakEvenInMonths","LookbackPeriodInDays","TermInYears"]
CONST_CO_ARRNO_FIELDS = [i for i in range(len(CONST_HEADER_ARRNO))]

CONST_CO_ARDSRIO = 'Amazon Relational Database Service (RDS) Reserved Instance Optimization'
#Region	Family	Instance Type	License Model	Database Edition	Database Engine	Deployment Option	Recommended number of Reserved Instances to purchase	Expected Average Reserved Instance Utilization	Estimated Savings with Recommendation (monthly)	Upfront Cost of Reserved Instances	Estimated cost of Reserved Instances (monthly)	Estimated On-Demand Cost Post Recommended Reserved Instance Purchase (monthly)	Estimated Break Even (months)	Lookback Period (days)	Term (years)
CONST_HEADER_ARDSRIO = ["CheckId","AccountId","AccountName","TACategory","Status","Check","Region","isSuppressed","COL8","COL9","Family","InstanceType","LicenseModel","DatabaseEdition","DatabaseEngine","DeploymentOption","RecommendedNumberToPurchase","ExpectedAverageUtilization","EstimatedMonthlySavings","UpfrontCost","EstimatedCostOfReservedNodesMonthly","EstimatedBreakEvenInMonths","LookbackPeriodInDays","TermInYears"]
CONST_CO_ARDSRIO_FIELDS = [i for i in range(len(CONST_HEADER_ARDSRIO))]

CONST_CO_SP = 'Savings Plan'
#Savings Plan type	Payment option	Upfront cost	Hourly commitment to purchase	Estimated average utilization	Estimated Monthly Savings	Estimated savings percentage	Lookback Period (days)	Term (years)
CONST_HEADER_SP = ["CheckId","AccountId","AccountName","TACategory","Status","Check","Region","isSuppressed","COL8","SavingsPlanType","PaymentOption","UpfrontCost","HourlyCommitmentToPurchase","EstimatedAverageUtilization","EstimatedMonthlySavings","EstimatedSavingsPercentage","LookbackPeriodInDays","TermInYears"]
CONST_CO_SP_FIELDS = [i for i in range(len(CONST_HEADER_SP))]


# create console handler and set level to INFO
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)

exec_tatool = tatool.tatool()
pd.options.mode.chained_assignment = None 
os.system("")

class TatoolFollowUp:
    def __init__(self):
        self.counter=0
        self.args=[]

    #----------------------------------------------------------------------------------------------------------------------------------------------
    def RepresentsInt(s):
         try:
            int(s)
            return True
         except ValueError:
              return False

    #----------------------------------------------------------------------------------------------------------------------------------------------
    def cmdline_parser_lst_accounts_for_domain( self, p_DOMAIN, p_LOCAL_TATOOL_FILE):
        now = datetime.now()
        date_120_days_ago = dateparser.parse('120 days ago')
        parser = argparse.ArgumentParser(
            description='Tatool - Enterprise Customer Trusted Advisor detailed view'
        )
        parser.add_argument('-a', '--account_id', nargs='+', dest='account_id', type=str, required=False, default=False,
                            help='Customer AccountId. If specified it runs only for this account')
        parser.add_argument('-accfile', '--accounts_file', dest='accounts_file', type=str, required=False, default=False,
                            help='File with a list of Customer AccountId. If specified it runs only for the list of accounts specified in the file.It must be specified a single account for each line of the file. Look at README for a file sample.')
        bucketArg = parser.add_argument('-b', '--bucket-s3', dest='s3bucket', type=str, required=False,
                            help='This is the S3 bucket where the Tatool data will be stored.')
        bcaArg = parser.add_argument('-bca', '--bca-reason', dest='bcareason', type=str, required=False, default='MBR monthly Report',
                            help='Please provide the business case authorization (BCA) reason why you need to run tatool on the accounts')
        parser.add_argument('-cet', '--cases_end_time', dest='cases_end_time',
                            type=str, required=False, default=now.strftime("%Y-%m-%d"),
                            help='This option specifies the beforeTime value for the cases search. It end to search from the time set. The format to insert is: YYYY-MM-DD. Default: ' + now.strftime("%Y-%m-%d"))
        parser.add_argument('-cst', '--cases_start_time', dest='cases_start_time',
                            type=str, required=False, default=date_120_days_ago.strftime("%Y-%m-%d"),
                            help='This option specifies the afterTime value for the cases search. It starts to search from the time set. The format to insert is: YYYY-MM-DD. Default: ' + date_120_days_ago.strftime("%Y-%m-%d"))
        domainArg = parser.add_argument('-d', '--customer_domain', dest='customer_domain', default=p_DOMAIN,
                            type=str, required=False, help='Report Customer Domain')
        parser.add_argument('-display', '--displayformat', dest='displayformat',
                            type=str, required=False, default='name',
                            help='This option specifies how the account must be displayed. Supported formats are email, name, accountid. Default: name.')
        parser.add_argument('-f', '--filter_file_ta', dest='filter_file_ta',
                            type=str, required=False, default=None, help='Full path and filename of the file containing account-id, Check Name and resource-id to be filtered.')
        parser.add_argument('-g', '--graphs_ta', dest='graphs_ta', action="store_true",
                            help='Create a file containing graphs from Trusted Advisor Statistics')
        genlstonlyArg = parser.add_argument('-generateaccountslistonly', '--generateaccountslistonly', dest='generateaccountslistonly', type=str, required=False, default=CONST_ACCOUNTS_LIST_FILENAME,
                            help='The option allows to write on file the account list associated with account name or mail and after that the script exits.')
        parser.add_argument("-l", "--log", dest="logLevel", default='INFO',
                            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help="Set the logger level")
        parser.add_argument('-no_update_trends', '--no_update_trends', dest='no_update_trends', action="store_true",
                            help='Option to avoid that the trend history is updated. If specified the trend will not update the historic statistics')
        outputArg = parser.add_argument('-o', '--output_file', dest='output_file',
                            type=str, required=False, default=None,
                            help='Full path and name of the zip file for the output files generated.')
        parser.add_argument('-p', '--payers_id', nargs='+', dest='payers_id', type=str, required=False, default=False,
                            help='Customer Payer AccountIds. If specified it runs only for the payer accounts and all the linked accounts.')
        parser.add_argument('-pdf', '--ta_checks_pdf', dest='ta_checks_pdf', action="store_true",
                            help='Generate PDF file for each trusted advisor check that raised a warning or an error. (parameter only available on Windows and Mac OSX). You need ton install wkhtmltopdf from https://wkhtmltopdf.org/ before using this parameter.')
        parser.add_argument('-r', '--refresh_ta_checks', dest='refresh_ta_checks', action="store_true",
                            help='Refresh trusted advisor checks before getting the detail.')
        parser.add_argument('-ri_opp', '--ri_opportunities', dest='ri_opportunities', action="store_true",
                            help='Collect and shows the Reserved Instances opportunities according to the Trusted Advisor Suggestions.')
        parser.add_argument('-s', '--support_cases', dest='support_cases', action="store_true",
                            help='Check the support cases opened for the accounts.')
        parser.add_argument('-s3acc', '--s3_access_key', dest='s3accesskey', type=str, required=False, default=None,
                            help='This is the S3 accesskey to access S3. Providing credentials is optional because the boto libraries will search in the configuration files according to this document: http://boto3.readthedocs.io/en/latest/guide/configuration.html')
        parser.add_argument('-s3sec', '--s3_secret_key', dest='s3secretkey', type=str, required=False, default=None,
                            help='This is the S3 secretkey to access S3. Providing credentials is optional because the boto libraries will search in the configuration files according to this document: http://boto3.readthedocs.io/en/latest/guide/configuration.html')
        threadArg = parser.add_argument('-threads', '--threads', dest='threads',
                            type=int, required=False, default=10, help='Number of concurrent k2 api calls. Default: 10')
        taArg = parser.add_argument('-t', '--trusted_advisor', dest='trusted_advisor', action="store_true",
                            help='Run the Trusted Advisor checks for the accounts.')

        domainArg.default = p_DOMAIN
        threadArg.default = v_THREAD
        bcaArg.default = 'MBR monthly Report'
        bucketArg.default = v_S3_BUCKET
        genlstonlyArg.default = CONST_ACCOUNTS_LIST_FILENAME
        taArg.default = True
        outputArg.default = p_LOCAL_TATOOL_FILE
        #input_args = parser.parse_args()

        return parser

    #----------------------------------------------------------------------------------------------------------------------------------------------
    def cmdline_parser_lst_accounts_for_payerid( self, p_PAYERID, p_LOCAL_TATOOL_FILE):
        now = datetime.now()
        date_120_days_ago = dateparser.parse('120 days ago')
        parser = argparse.ArgumentParser(
            description='Tatool - Enterprise Customer Trusted Advisor detailed view'
        )
        parser.add_argument('-a', '--account_id', nargs='+', dest='account_id', type=str, required=False, default=False,
                            help='Customer AccountId. If specified it runs only for this account')
        parser.add_argument('-accfile', '--accounts_file', dest='accounts_file', type=str, required=False, default=False,
                            help='File with a list of Customer AccountId. If specified it runs only for the list of accounts specified in the file.It must be specified a single account for each line of the file. Look at README for a file sample.')
        bucketArg = parser.add_argument('-b', '--bucket-s3', dest='s3bucket', type=str, required=False, default=v_S3_BUCKET,
                            help='This is the S3 bucket where the Tatool data will be stored.')
        bcaArg = parser.add_argument('-bca', '--bca-reason', dest='bcareason', type=str, required=False, default = 'MBR monthly Report',
                            help='Please provide the business case authorization (BCA) reason why you need to run tatool on the accounts')
        parser.add_argument('-cet', '--cases_end_time', dest='cases_end_time',
                            type=str, required=False, default=now.strftime("%Y-%m-%d"),
                            help='This option specifies the beforeTime value for the cases search. It end to search from the time set. The format to insert is: YYYY-MM-DD. Default: ' + now.strftime("%Y-%m-%d"))
        parser.add_argument('-cst', '--cases_start_time', dest='cases_start_time',
                            type=str, required=False, default=date_120_days_ago.strftime("%Y-%m-%d"),
                            help='This option specifies the afterTime value for the cases search. It starts to search from the time set. The format to insert is: YYYY-MM-DD. Default: ' + date_120_days_ago.strftime("%Y-%m-%d"))
        parser.add_argument('-d', '--customer_domain', dest='customer_domain',
                            type=str, required=False, default=False, help='Report Customer Domain')
        parser.add_argument('-display', '--displayformat', dest='displayformat',
                            type=str, required=False, default='name',
                            help='This option specifies how the account must be displayed. Supported formats are email, name, accountid. Default: name.')
        parser.add_argument('-f', '--filter_file_ta', dest='filter_file_ta',
                            type=str, required=False, default=None, help='Full path and filename of the file containing account-id, Check Name and resource-id to be filtered.')
        parser.add_argument('-g', '--graphs_ta', dest='graphs_ta', action="store_true",
                            help='Create a file containing graphs from Trusted Advisor Statistics')
        genlstonlyArg = parser.add_argument('-generateaccountslistonly', '--generateaccountslistonly', dest='generateaccountslistonly', type=str, required=False, default = CONST_ACCOUNTS_LIST_FILENAME,
                            help='The option allows to write on file the account list associated with account name or mail and after that the script exits.')
        parser.add_argument("-l", "--log", dest="logLevel", default='INFO',
                            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help="Set the logger level")
        parser.add_argument('-no_update_trends', '--no_update_trends', dest='no_update_trends', action="store_true",
                            help='Option to avoid that the trend history is updated. If specified the trend will not update the historic statistics')
        outputArg = parser.add_argument('-o', '--output_file', dest='output_file',
                            type=str, required=False, default=None,
                            help='Full path and name of the zip file for the output files generated.')
        payeridArg = parser.add_argument('-p', '--payers_id', dest='payers_id', type=str, required=False, default=[p_PAYERID], 
                            help='Customer Payer AccountIds. If specified it runs only for the payer accounts and all the linked accounts.')
        parser.add_argument('-pdf', '--ta_checks_pdf', dest='ta_checks_pdf', action="store_true",
                            help='Generate PDF file for each trusted advisor check that raised a warning or an error. (parameter only available on Windows and Mac OSX). You need ton install wkhtmltopdf from https://wkhtmltopdf.org/ before using this parameter.')
        parser.add_argument('-r', '--refresh_ta_checks', dest='refresh_ta_checks', action="store_true",
                            help='Refresh trusted advisor checks before getting the detail.')
        parser.add_argument('-ri_opp', '--ri_opportunities', dest='ri_opportunities', action="store_true",
                            help='Collect and shows the Reserved Instances opportunities according to the Trusted Advisor Suggestions.')
        parser.add_argument('-s', '--support_cases', dest='support_cases', action="store_true",
                            help='Check the support cases opened for the accounts.')
        parser.add_argument('-s3acc', '--s3_access_key', dest='s3accesskey', type=str, required=False, default=None,
                            help='This is the S3 accesskey to access S3. Providing credentials is optional because the boto libraries will search in the configuration files according to this document: http://boto3.readthedocs.io/en/latest/guide/configuration.html')
        parser.add_argument('-s3sec', '--s3_secret_key', dest='s3secretkey', type=str, required=False, default=None,
                            help='This is the S3 secretkey to access S3. Providing credentials is optional because the boto libraries will search in the configuration files according to this document: http://boto3.readthedocs.io/en/latest/guide/configuration.html')
        threadArg = parser.add_argument('-threads', '--threads', dest='threads',
                            type=int, required=False, default=10, help='Number of concurrent k2 api calls. Default: 10')
        taArg = parser.add_argument('-t', '--trusted_advisor', dest='trusted_advisor', action="store_true",
                            help='Run the Trusted Advisor checks for the accounts.')

        payeridArg.default = [p_PAYERID]
        threadArg.default = v_THREAD
        bcaArg.default = 'MBR monthly Report'
        bucketArg.default = v_S3_BUCKET
        genlstonlyArg.default = CONST_ACCOUNTS_LIST_FILENAME
        taArg.default = True
        outputArg.default = p_LOCAL_TATOOL_FILE
        #input_args = parser.parse_args()

        return parser

    #----------------------------------------------------------------------------------------------------------------------------------------------
    def cmdline_parser_ta_for_domain( self, p_DOMAIN, p_LOCAL_TATOOL_FILE):
        now = datetime.now()
        date_120_days_ago = dateparser.parse('120 days ago')
        parser = argparse.ArgumentParser(
            description='Tatool - Enterprise Customer Trusted Advisor detailed view'
        )
        parser.add_argument('-a', '--account_id', dest='account_id', type=str, required=False, default=False,
                            help='Customer AccountId. If specified it runs only for this account')
        parser.add_argument('-accfile', '--accounts_file', dest='accounts_file', type=str, required=False, default=False,
                            help='File with a list of Customer AccountId. If specified it runs only for the list of accounts specified in the file.It must be specified a single account for each line of the file. Look at README for a file sample.')
        bucketArg = parser.add_argument('-b', '--bucket-s3', dest='s3bucket', type=str, required=False,
                            help='This is the S3 bucket where the Tatool data will be stored.')
        bcaArg = parser.add_argument('-bca', '--bca-reason', dest='bcareason', type=str, required=False,
                            help='Please provide the business case authorization (BCA) reason why you need to run tatool on the accounts')
        parser.add_argument('-cet', '--cases_end_time', dest='cases_end_time',
                            type=str, required=False, default=now.strftime("%Y-%m-%d"),
                            help='This option specifies the beforeTime value for the cases search. It end to search from the time set. The format to insert is: YYYY-MM-DD. Default: ' + now.strftime("%Y-%m-%d"))
        parser.add_argument('-cst', '--cases_start_time', dest='cases_start_time',
                            type=str, required=False, default=date_120_days_ago.strftime("%Y-%m-%d"),
                            help='This option specifies the afterTime value for the cases search. It starts to search from the time set. The format to insert is: YYYY-MM-DD. Default: ' + date_120_days_ago.strftime("%Y-%m-%d"))
        domainArg = parser.add_argument('-d', '--customer_domain', dest='customer_domain',
                            type=str, required=False, default=p_DOMAIN, help='Report Customer Domain')
        parser.add_argument('-display', '--displayformat', dest='displayformat',
                            type=str, required=False, default='name',
                            help='This option specifies how the account must be displayed. Supported formats are email, name, accountid. Default: name.')
        """
        #Send mail report, ready to be implemented in case of a host running in batch for multiple customers.
        parser.add_argument('-e', '--email', dest='send_mail', action='store_true',
                            help='Send the email to the address specified by the -to flag. Default: ' + getpass.getuser() + '@amazon.com.')
        """
        parser.add_argument('-f', '--filter_file_ta', dest='filter_file_ta',
                            type=str, required=False, default=None, help='Full path and filename of the file containing account-id, Check Name and resource-id to be filtered.')
        parser.add_argument('-g', '--graphs_ta', dest='graphs_ta', action="store_true",
                            help='Create a file containing graphs from Trusted Advisor Statistics')
        genlstonlyArg = parser.add_argument('-generateaccountslistonly', '--generateaccountslistonly', dest='generateaccountslistonly', type=bool, required=False, default=False,
                            help='The option allows to write on file the account list associated with account name or mail and after that the script exits.')
        parser.add_argument("-l", "--log", dest="logLevel", default='INFO',
                            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help="Set the logger level")
        parser.add_argument('-no_update_trends', '--no_update_trends', dest='no_update_trends', action="store_true",
                            help='Option to avoid that the trend history is updated. If specified the trend will not update the historic statistics')
        outputArg = parser.add_argument('-o', '--output_file', dest='output_file',
                            type=str, required=False, default=None,
                            help='Full path and name of the zip file for the output files generated.')
        parser.add_argument('-p', '--payers_id', nargs='+', dest='payers_id', type=str, required=False, default=False,
                            help='Customer Payer AccountIds. If specified it runs only for the payer accounts and all the linked accounts.')
        parser.add_argument('-pdf', '--ta_checks_pdf', dest='ta_checks_pdf', action="store_true",
                            help='Generate PDF file for each trusted advisor check that raised a warning or an error. (parameter only available on Windows and Mac OSX). You need ton install wkhtmltopdf from https://wkhtmltopdf.org/ before using this parameter.')
        parser.add_argument('-r', '--refresh_ta_checks', dest='refresh_ta_checks', action="store_true",
                            help='Refresh trusted advisor checks before getting the detail.')
        parser.add_argument('-ri_opp', '--ri_opportunities', dest='ri_opportunities', action="store_true",
                            help='Collect and shows the Reserved Instances opportunities according to the Trusted Advisor Suggestions.')
        parser.add_argument('-s', '--support_cases', dest='support_cases', action="store_true",
                            help='Check the support cases opened for the accounts.')
        parser.add_argument('-s3acc', '--s3_access_key', dest='s3accesskey', type=str, required=False, default=None,
                            help='This is the S3 accesskey to access S3. Providing credentials is optional because the boto libraries will search in the configuration files according to this document: http://boto3.readthedocs.io/en/latest/guide/configuration.html')
        parser.add_argument('-s3sec', '--s3_secret_key', dest='s3secretkey', type=str, required=False, default=None,
                            help='This is the S3 secretkey to access S3. Providing credentials is optional because the boto libraries will search in the configuration files according to this document: http://boto3.readthedocs.io/en/latest/guide/configuration.html')
        threadArg = parser.add_argument('-threads', '--threads', dest='threads',
                            type=int, required=False, default=10, help='Number of concurrent k2 api calls. Default: 10')
        taArg = parser.add_argument('-t', '--trusted_advisor', dest='trusted_advisor', action="store_true",
                            help='Run the Trusted Advisor checks for the accounts.')
        """
        #Send mail report, ready to be implemented in case of a host running in batch for multiple customers.
        parser.add_argument('-to', '--to', dest='email_address',
                            type=str, required=False, default=getpass.getuser() + '@amazon.com',
                            help='Email address to send the CWCB report. Default: ' + getpass.getuser() + '@amazon.com.')
        """

        domainArg.default = p_DOMAIN
        threadArg.default = v_THREAD
        bcaArg.default = 'MBR monthly Report'
        bucketArg.default = v_S3_BUCKET
        genlstonlyArg.default = False
        taArg.default = True
        outputArg.default = p_LOCAL_TATOOL_FILE
        #input_args = parser.parse_args()

        return parser

    #----------------------------------------------------------------------------------------------------------------------------------------------
    def cmdline_parser_ta_for_payerid( self, p_PAYERID, p_LOCAL_TATOOL_FILE):
        now = datetime.now()
        date_120_days_ago = dateparser.parse('120 days ago')
        parser = argparse.ArgumentParser(
            description='Tatool - Enterprise Customer Trusted Advisor detailed view'
        )
        parser.add_argument('-a', '--account_id', dest='account_id', type=str, required=False, default=False,
                            help='Customer AccountId. If specified it runs only for this account')
        parser.add_argument('-accfile', '--accounts_file', dest='accounts_file', type=str, required=False, default=False,
                            help='File with a list of Customer AccountId. If specified it runs only for the list of accounts specified in the file.It must be specified a single account for each line of the file. Look at README for a file sample.')
        bucketArg = parser.add_argument('-b', '--bucket-s3', dest='s3bucket', type=str, required=False,
                            help='This is the S3 bucket where the Tatool data will be stored.')
        bcaArg = parser.add_argument('-bca', '--bca-reason', dest='bcareason', type=str, required=False,
                            help='Please provide the business case authorization (BCA) reason why you need to run tatool on the accounts')
        parser.add_argument('-cet', '--cases_end_time', dest='cases_end_time',
                            type=str, required=False, default=now.strftime("%Y-%m-%d"),
                            help='This option specifies the beforeTime value for the cases search. It end to search from the time set. The format to insert is: YYYY-MM-DD. Default: ' + now.strftime("%Y-%m-%d"))
        parser.add_argument('-cst', '--cases_start_time', dest='cases_start_time',
                            type=str, required=False, default=date_120_days_ago.strftime("%Y-%m-%d"),
                            help='This option specifies the afterTime value for the cases search. It starts to search from the time set. The format to insert is: YYYY-MM-DD. Default: ' + date_120_days_ago.strftime("%Y-%m-%d"))
        parser.add_argument('-d', '--customer_domain', dest='customer_domain',
                            type=str, required=False, default=False, help='Report Customer Domain')
        parser.add_argument('-display', '--displayformat', dest='displayformat',
                            type=str, required=False, default='name',
                            help='This option specifies how the account must be displayed. Supported formats are email, name, accountid. Default: name.')
        """
        #Send mail report, ready to be implemented in case of a host running in batch for multiple customers.
        parser.add_argument('-e', '--email', dest='send_mail', action='store_true',
                            help='Send the email to the address specified by the -to flag. Default: ' + getpass.getuser() + '@amazon.com.')
        """
        parser.add_argument('-f', '--filter_file_ta', dest='filter_file_ta',
                            type=str, required=False, default=None, help='Full path and filename of the file containing account-id, Check Name and resource-id to be filtered.')
        parser.add_argument('-g', '--graphs_ta', dest='graphs_ta', action="store_true",
                            help='Create a file containing graphs from Trusted Advisor Statistics')
        genlstonlyArg = parser.add_argument('-generateaccountslistonly', '--generateaccountslistonly', dest='generateaccountslistonly', type=bool, required=False, default=False,
                            help='The option allows to write on file the account list associated with account name or mail and after that the script exits.')
        parser.add_argument("-l", "--log", dest="logLevel", default='INFO',
                            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help="Set the logger level")
        parser.add_argument('-no_update_trends', '--no_update_trends', dest='no_update_trends', action="store_true",
                            help='Option to avoid that the trend history is updated. If specified the trend will not update the historic statistics')
        outputArg = parser.add_argument('-o', '--output_file', dest='output_file',
                            type=str, required=False, default=None,
                            help='Full path and name of the zip file for the output files generated.')
        payeridArg = parser.add_argument('-p', '--payers_id', nargs='+', dest='payers_id', type=str, required=False, default=[p_PAYERID],
                            help='Customer Payer AccountIds. If specified it runs only for the payer accounts and all the linked accounts.')
        parser.add_argument('-pdf', '--ta_checks_pdf', dest='ta_checks_pdf', action="store_true",
                            help='Generate PDF file for each trusted advisor check that raised a warning or an error. (parameter only available on Windows and Mac OSX). You need ton install wkhtmltopdf from https://wkhtmltopdf.org/ before using this parameter.')
        parser.add_argument('-r', '--refresh_ta_checks', dest='refresh_ta_checks', action="store_true",
                            help='Refresh trusted advisor checks before getting the detail.')
        parser.add_argument('-ri_opp', '--ri_opportunities', dest='ri_opportunities', action="store_true",
                            help='Collect and shows the Reserved Instances opportunities according to the Trusted Advisor Suggestions.')
        parser.add_argument('-s', '--support_cases', dest='support_cases', action="store_true",
                            help='Check the support cases opened for the accounts.')
        parser.add_argument('-s3acc', '--s3_access_key', dest='s3accesskey', type=str, required=False, default=None,
                            help='This is the S3 accesskey to access S3. Providing credentials is optional because the boto libraries will search in the configuration files according to this document: http://boto3.readthedocs.io/en/latest/guide/configuration.html')
        parser.add_argument('-s3sec', '--s3_secret_key', dest='s3secretkey', type=str, required=False, default=None,
                            help='This is the S3 secretkey to access S3. Providing credentials is optional because the boto libraries will search in the configuration files according to this document: http://boto3.readthedocs.io/en/latest/guide/configuration.html')
        threadArg = parser.add_argument('-threads', '--threads', dest='threads',
                            type=int, required=False, default=10, help='Number of concurrent k2 api calls. Default: 10')
        taArg = parser.add_argument('-t', '--trusted_advisor', dest='trusted_advisor', action="store_true",
                            help='Run the Trusted Advisor checks for the accounts.')
        """
        #Send mail report, ready to be implemented in case of a host running in batch for multiple customers.
        parser.add_argument('-to', '--to', dest='email_address',
                            type=str, required=False, default=getpass.getuser() + '@amazon.com',
                            help='Email address to send the CWCB report. Default: ' + getpass.getuser() + '@amazon.com.')
        """

        payeridArg.default = [p_PAYERID]
        threadArg.default = v_THREAD
        bcaArg.default = 'MBR monthly Report'
        bucketArg.default = v_S3_BUCKET
        genlstonlyArg.default = False
        taArg.default = True
        outputArg.default = p_LOCAL_TATOOL_FILE
        #input_args = parser.parse_args()

        return parser

    #----------------------------------------------------------------------------------------------------------------------------------------------
    def cmdline_parser_ta_for_accountid( self, p_PAYERID, p_LOCAL_TATOOL_FILE):
        now = datetime.now()
        date_120_days_ago = dateparser.parse('120 days ago')
        parser = argparse.ArgumentParser(
            description='Tatool - Enterprise Customer Trusted Advisor detailed view'
        )
        accountArg = parser.add_argument('-a', '--account_id', nargs='+', dest='account_id', type=str, required=False, default=False,
                            help='Customer AccountId. If specified it runs only for this account')
        parser.add_argument('-accfile', '--accounts_file', dest='accounts_file', type=str, required=False, default=False,
                            help='File with a list of Customer AccountId. If specified it runs only for the list of accounts specified in the file.It must be specified a single account for each line of the file. Look at README for a file sample.')
        bucketArg = parser.add_argument('-b', '--bucket-s3', dest='s3bucket', type=str, required=False,
                            help='This is the S3 bucket where the Tatool data will be stored.')
        bcaArg = parser.add_argument('-bca', '--bca-reason', dest='bcareason', type=str, required=False,
                            help='Please provide the business case authorization (BCA) reason why you need to run tatool on the accounts')
        parser.add_argument('-cet', '--cases_end_time', dest='cases_end_time',
                            type=str, required=False, default=now.strftime("%Y-%m-%d"),
                            help='This option specifies the beforeTime value for the cases search. It end to search from the time set. The format to insert is: YYYY-MM-DD. Default: ' + now.strftime("%Y-%m-%d"))
        parser.add_argument('-cst', '--cases_start_time', dest='cases_start_time',
                            type=str, required=False, default=date_120_days_ago.strftime("%Y-%m-%d"),
                            help='This option specifies the afterTime value for the cases search. It starts to search from the time set. The format to insert is: YYYY-MM-DD. Default: ' + date_120_days_ago.strftime("%Y-%m-%d"))
        parser.add_argument('-d', '--customer_domain', dest='customer_domain',
                            type=str, required=False, default=False, help='Report Customer Domain')
        parser.add_argument('-display', '--displayformat', dest='displayformat',
                            type=str, required=False, default='name',
                            help='This option specifies how the account must be displayed. Supported formats are email, name, accountid. Default: name.')
        """
        #Send mail report, ready to be implemented in case of a host running in batch for multiple customers.
        parser.add_argument('-e', '--email', dest='send_mail', action='store_true',
                            help='Send the email to the address specified by the -to flag. Default: ' + getpass.getuser() + '@amazon.com.')
        """
        parser.add_argument('-f', '--filter_file_ta', dest='filter_file_ta',
                            type=str, required=False, default=None, help='Full path and filename of the file containing account-id, Check Name and resource-id to be filtered.')
        parser.add_argument('-g', '--graphs_ta', dest='graphs_ta', action="store_true",
                            help='Create a file containing graphs from Trusted Advisor Statistics')
        genlstonlyArg = parser.add_argument('-generateaccountslistonly', '--generateaccountslistonly', dest='generateaccountslistonly', type=bool, required=False, default=False,
                            help='The option allows to write on file the account list associated with account name or mail and after that the script exits.')
        parser.add_argument("-l", "--log", dest="logLevel", default='INFO',
                            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help="Set the logger level")
        parser.add_argument('-no_update_trends', '--no_update_trends', dest='no_update_trends', action="store_true",
                            help='Option to avoid that the trend history is updated. If specified the trend will not update the historic statistics')
        outputArg = parser.add_argument('-o', '--output_file', dest='output_file',
                            type=str, required=False, default=None,
                            help='Full path and name of the zip file for the output files generated.')
        payerArg = parser.add_argument('-p', '--payers_id', nargs='+', dest='payers_id', type=str, required=False, default=False,
                            help='Customer Payer AccountIds. If specified it runs only for the payer accounts and all the linked accounts.')
        parser.add_argument('-pdf', '--ta_checks_pdf', dest='ta_checks_pdf', action="store_true",
                            help='Generate PDF file for each trusted advisor check that raised a warning or an error. (parameter only available on Windows and Mac OSX). You need ton install wkhtmltopdf from https://wkhtmltopdf.org/ before using this parameter.')
        parser.add_argument('-r', '--refresh_ta_checks', dest='refresh_ta_checks', action="store_true",
                            help='Refresh trusted advisor checks before getting the detail.')
        parser.add_argument('-ri_opp', '--ri_opportunities', dest='ri_opportunities', action="store_true",
                            help='Collect and shows the Reserved Instances opportunities according to the Trusted Advisor Suggestions.')
        parser.add_argument('-s', '--support_cases', dest='support_cases', action="store_true",
                            help='Check the support cases opened for the accounts.')
        parser.add_argument('-s3acc', '--s3_access_key', dest='s3accesskey', type=str, required=False, default=None,
                            help='This is the S3 accesskey to access S3. Providing credentials is optional because the boto libraries will search in the configuration files according to this document: http://boto3.readthedocs.io/en/latest/guide/configuration.html')
        parser.add_argument('-s3sec', '--s3_secret_key', dest='s3secretkey', type=str, required=False, default=None,
                            help='This is the S3 secretkey to access S3. Providing credentials is optional because the boto libraries will search in the configuration files according to this document: http://boto3.readthedocs.io/en/latest/guide/configuration.html')
        threadArg = parser.add_argument('-threads', '--threads', dest='threads',
                            type=int, required=False, default=10, help='Number of concurrent k2 api calls. Default: 10')
        taArg = parser.add_argument('-t', '--trusted_advisor', dest='trusted_advisor', action="store_true",
                            help='Run the Trusted Advisor checks for the accounts.')
        """
        #Send mail report, ready to be implemented in case of a host running in batch for multiple customers.
        parser.add_argument('-to', '--to', dest='email_address',
                            type=str, required=False, default=getpass.getuser() + '@amazon.com',
                            help='Email address to send the CWCB report. Default: ' + getpass.getuser() + '@amazon.com.')
        """

        payerArg.default = p_PAYERID
        threadArg.default = v_THREAD
        bcaArg.default = 'MBR monthly Report'
        bucketArg.default = v_S3_BUCKET
        genlstonlyArg.default = False
        taArg.default = True
        outputArg.default = p_LOCAL_TATOOL_FILE
        #input_args = parser.parse_args()

        return parser

    def find_specific_cell( p_currentSheet, p_value):
        for row in range(1, p_currentSheet.max_row + 1):
            for column in "C":  # Here you can add or reduce the columns
                cell_name = "{}{}".format(column, row)
                if p_currentSheet[cell_name].value == p_value:
                    #print("{1} cell is located on {0}" .format(cell_name, currentSheet[cell_name].value))
                    print("Update cell position {} has value {}".format(cell_name, p_currentSheet[cell_name].value))
                    return cell_name
                else:
                    return "A0"
    #----------------------------------------------------------------------------------------------------------------------------------------------
    # full_report_with_resource-ids.csv
    # CheckId,Account-Id,Account Display Name,TA Category,Status External,TA Check Name,Region,isSuppressed,---,Resources_Metadata
    #----------------------------------------------------------------------------------------------------------------------------------------------
    def generate2_xls_from_ta_csv(self, filenameXLS, p_lstFolders, p_DATETIME, p_FULL_DATETIME):
        v_FILENAME_EXCEL_FILE = "TrustedAdvisor_"+p_FULL_DATETIME+"_"+filenameXLS
        writer = pd.ExcelWriter(v_FILENAME_EXCEL_FILE, engine='xlsxwriter')
        maxfolders = len(p_lstFolders)

        df_ta = []
        df2 = []
        df3 = []
        df_ta_co = []
        df_ta_co_sheet = []
        df_ta_co_group = []
        df_ta_co_global = []
        df_ta_se = []
        df_ta_ft = []
        df_ta_co = []
        folder = 1
        v_RIGHT_SIZING = False

        v_GLOBAL_FIRST_LINE_XLS_LIST = ["Check","Status","TACategory"]
        v_GLOBAL_COLUMNS_XLS_LIST = ["Status","Check","TACategory"]
        v_COST_PILLAR_FIRST_LINE_XLS_LIST = ["CostDomain","CostType"]
        v_COST_PILLAR_COLUMNS_XLS_LIST = ["CostDomain","CostType","EstimatedMonthlySavings"]

        logger.info("Number of folders to analyze : " + str(len(p_lstFolders)))
        logger.info("v_GLOBAL_COLUMNS_XLS_LIST = " + ','.join(v_GLOBAL_COLUMNS_XLS_LIST))
        if len(p_lstFolders) <= 0:
            return

        for aFolder in p_lstFolders:

            df_ta_co_group.clear()
            co_lines = 0

            logger.info('+' + '-'*98 + '+') 
            logger.info("List of folder(s) to analyze : " + aFolder[0])
            v_GLOBAL_FIRST_LINE_XLS_LIST.append(aFolder[0])
            v_COST_PILLAR_FIRST_LINE_XLS_LIST.append(aFolder[0])
            v_GLOBAL_COLUMNS_XLS_LIST.append(aFolder[0])
            v_COST_PILLAR_COLUMNS_XLS_LIST.append(aFolder[0])

            logger.info("Retreiving tatool figures from folder : < " + str(aFolder[0]) + " >")
            df_ta.append(  pd.read_csv(str(aFolder[0]) + CONST_FULL_REPORT_RESOURCE, usecols = [0,1,2,3,4,5,6,7], names = CONST_HEADER_CSV_TATOOL, skiprows=1))

            logger.info( "Extracting SECURITY figures from < " + aFolder[0] + CONST_FULL_REPORT_RESOURCE + " >")
            df = pd.DataFrame(df_ta[folder-1][(df_ta[folder-1]["TACategory"] == 'security') & (df_ta[folder-1]["Status"] != 'ok')].groupby(["Check","Status","TACategory"])["CheckId"].count().reset_index(name='CheckId'))
            df['Status'] = df['Status'].replace({'error':'ERR', 'warning':'Warn'})
            df_ta_se.append( df)
            logger.debug(tabulate.tabulate(df_ta_se[folder-1], headers='keys', tablefmt='psql', showindex="always"))

            logger.info( "Extractiong FAULT TOLTERANCE figuers from < " + aFolder[0] + CONST_FULL_REPORT_RESOURCE + " >")
            df = pd.DataFrame(df_ta[folder-1][(df_ta[folder-1]["TACategory"] == 'fault_tolerance') & (df_ta[folder-1]["Status"] != 'ok')].groupby(["Check","Status","TACategory"])["CheckId"].count().reset_index(name='CheckId'))
            df['Status'] = df['Status'].replace({'error':'ERR', 'warning':'Warn'})
            df_ta_ft.append( df)
            logger.debug(tabulate.tabulate(df_ta_ft[folder-1], headers='keys', tablefmt='psql', showindex="always"))

            lst_files = glob2.glob(str(aFolder[0]) + CONST_RIGHTSIZING_FILENAME_STAR)
            selection = 'n'

            if len(lst_files):
                selection = input("\033[1;41m Found RightSizing files ! Do we have to process them ? (default process Low EC2 utilization only): (o/n) \033[1;0m") 
                if (selection == 'o'):
                
                    v_RIGHT_SIZING = True
                    
                    # EC2 RightSizing Recommendations
                    for file in lst_files:
                        logger.info( "Extracting EC2 RightSizing Recommendations from < " + file + " >")
                        if not len(df2):
                            df2 = pd.read_csv(file, usecols = CONST_CO_ERCR_FIELDS, names = CONST_HEADER_ERCR, skiprows=1)
                        else:
                            df2 = df2.append(pd.read_csv(file, usecols = CONST_CO_ERCR_FIELDS, names = CONST_HEADER_ERCR, skiprows=1))

                    df2["EstimatedMonthlySavings"] = df2["EstimatedMonthlySavings"].replace('[\$,]', '', regex=True).astype(float)
                    df2 = df2.reset_index()
                    df2["Check"] = CONST_CO_ERSR
                    df_ta_co_sheet.append( df2)
                    df_ta_co_group.append( pd.DataFrame(df2.groupby(["Check","InstanceType"]).sum("EstimatedMonthlySavings")))
                    logger.debug(tabulate.tabulate(df_ta_co_group[co_lines], headers='keys', tablefmt='psql', showindex="always"))
                    co_lines += 1
            
            if (not len(lst_files)) or (selection == 'n'):
                logger.info( "No EC2 RightSizing Recommendations file exist in folder < " + aFolder[0] + CONST_FULL_REPORT_RIGHTSIZING + " >")

                # Low Utilization Amazon EC2 Instances
                logger.info( CONST_CO_LUAEI + " from file < " + aFolder[0] + CONST_FULL_REPORT_RESOURCE + " >")
                df2 = pd.read_csv(str(aFolder[0]) + CONST_FULL_REPORT_RESOURCE, usecols = CONST_CO_LUAEI_FIELDS, names = CONST_HEADER_LUAEI, skiprows=1)
                df2 = df2[(df2["TACategory"] == 'cost_optimizing') & (df2["Check"] == CONST_CO_LUAEI)]
                df2["EstimatedMonthlySavings"] = df2["EstimatedMonthlySavings"].replace('[\$,]', '', regex=True).astype(float)
                df_ta_co_sheet.append( df2)
                df3 = pd.DataFrame(df2.groupby(["Check","InstanceType"]).sum("EstimatedMonthlySavings"))
                df3 = df3.reset_index()
                df3.columns = CONST_COST_PILLAR_COLUMNS_XLS_LIST0
                df_ta_co_group.append( df3)
                logger.debug(tabulate.tabulate(df_ta_co_group[co_lines], headers='keys', tablefmt='psql', showindex="always"))
                co_lines += 1

            # Underutilized Amazon EBS Volumes
            logger.info( CONST_CO_UUAEV + " from file < " + aFolder[0] + CONST_FULL_REPORT_RESOURCE + " >")
            df2 = pd.read_csv(str(aFolder[0]) + CONST_FULL_REPORT_RESOURCE, usecols = CONST_CO_UUAEV_FIELDS, names = CONST_HEADER_UUAEV, skiprows=1)
            df2 = df2[(df2["TACategory"] == 'cost_optimizing') & (df2["Check"] == CONST_CO_UUAEV)]
            df2["EstimatedMonthlySavings"] = df2["EstimatedMonthlySavings"].replace('[\$,]', '', regex=True).astype(float)
            df2 = df2.reset_index()
            df_ta_co_sheet.append( df2)
            df3 = pd.DataFrame(df2.groupby(["Check","VolumeType"]).sum("EstimatedMonthlySavings"))
            df3 = df3.reset_index()
            df3.columns = CONST_COST_PILLAR_COLUMNS_XLS_LIST
            df_ta_co_group.append( df3)
            logger.debug(tabulate.tabulate(df_ta_co_group[co_lines], headers='keys', tablefmt='psql', showindex="always"))
            co_lines += 1

            # Amazon RDS Idle DB Instances
            logger.info( CONST_CO_ARIDI + " from file < " + aFolder[0] + CONST_FULL_REPORT_RESOURCE + " >")
            df2 = pd.read_csv(str(aFolder[0]) + CONST_FULL_REPORT_RESOURCE, usecols = CONST_CO_ARIDI_FIELDS, names = CONST_HEADER_ARIDI, skiprows=1)
            df2 = df2[(df2["TACategory"] == 'cost_optimizing') & (df2["Check"] == CONST_CO_ARIDI)]
            df2["EstimatedMonthlySavings"] = df2["EstimatedMonthlySavings"].replace('[\$,]', '', regex=True).astype(float)
            df2 = df2.reset_index()
            df_ta_co_sheet.append( df2)
            df3 = pd.DataFrame(df2.groupby(["Check","InstanceType"]).sum("EstimatedMonthlySavings"))
            df3 = df3.reset_index()
            df3.columns = CONST_COST_PILLAR_COLUMNS_XLS_LIST
            df_ta_co_group.append( df3)
            logger.debug(tabulate.tabulate(df_ta_co_group[co_lines], headers='keys', tablefmt='psql', showindex="always"))
            co_lines += 1

            # idle load balancers
            logger.info( CONST_CO_ILB + " from file < " + aFolder[0] + CONST_FULL_REPORT_RESOURCE + " >")
            df2 = pd.read_csv(str(aFolder[0]) + CONST_FULL_REPORT_RESOURCE, usecols = CONST_CO_ILB_FIELDS, names = CONST_HEADER_ILB, skiprows=1)
            df2 = df2[(df2["TACategory"] == 'cost_optimizing') & (df2["Check"] == CONST_CO_ILB)]
            df2["EstimatedMonthlySavings"] = df2["EstimatedMonthlySavings"].replace('[\$,]', '', regex=True).astype(float)
            df2 = df2.reset_index()
            df_ta_co_sheet.append( df2)
            df3 = pd.DataFrame(df2.groupby(["Check","Reason"]).sum("EstimatedMonthlySavings"))
            df3 = df3.reset_index()
            df3.columns = CONST_COST_PILLAR_COLUMNS_XLS_LIST
            df_ta_co_group.append( df3)
            logger.debug(tabulate.tabulate(df_ta_co_group[co_lines], headers='keys', tablefmt='psql', showindex="always"))
            co_lines += 1

            # unassociated elastic ip addresses
            logger.info( CONST_CO_UEIA + " from file < " + aFolder[0] + CONST_FULL_REPORT_RESOURCE + " >")
            df2 = pd.read_csv(str(aFolder[0]) + CONST_FULL_REPORT_RESOURCE, usecols = CONST_CO_UEIA_FIELDS, names = CONST_HEADER_UEIA, skiprows=1)
            df2 = df2[(df2["TACategory"] == 'cost_optimizing') & (df2["Check"] == CONST_CO_UEIA)]
            df2["EstimatedMonthlySavings"] = df2["EstimatedMonthlySavings"].replace('[\$,]', '', regex=True).astype(float)
            df2["EstimatedMonthlySavings"] = v_COST_EIP_UNUSED
            df2 = df2.reset_index()
            df_ta_co_sheet.append( df2)
            df3 = pd.DataFrame(df2.groupby(["Check","Region"]).sum("EstimatedMonthlySavings"))
            df3 = df3.reset_index()
            df3.columns = CONST_COST_PILLAR_COLUMNS_XLS_LIST
            df_ta_co_group.append( df3)
            logger.debug(tabulate.tabulate(df_ta_co_group[co_lines], headers='keys', tablefmt='psql', showindex="always"))
            co_lines += 1

            # Savings Plan
            logger.info( CONST_CO_SP + " from file < " + aFolder[0] + CONST_FULL_REPORT_RESOURCE + " >")
            df2 = pd.read_csv(str(aFolder[0]) + CONST_FULL_REPORT_RESOURCE, usecols = CONST_CO_SP_FIELDS, names = CONST_HEADER_SP, skiprows=1)
            df2 = df2[(df2["TACategory"] == 'cost_optimizing') & (df2["Check"] == CONST_CO_SP)]
            df2["EstimatedMonthlySavings"] = df2["EstimatedMonthlySavings"].replace('[\$,]', '', regex=True).astype(float)
            df2 = df2.reset_index()
            df_ta_co_sheet.append( df2)
            df3 = pd.DataFrame(df2[(df2["TermInYears"] == 'Three Years')].groupby(["Check","SavingsPlanType","TermInYears"]).sum("EstimatedMonthlySavings"))
            df3 = df3.reset_index()
            df3.columns = CONST_COST_PILLAR_COLUMNS_XLS_LIST2
            df_ta_co_group.append( df3)
            logger.debug(tabulate.tabulate(df_ta_co_group[co_lines], headers='keys', tablefmt='psql', showindex="always"))
            co_lines += 1

            # Amazon Relational Database Service (RDS) Reserved Instance Optimization
            logger.info( CONST_CO_ARDSRIO + " from file < " + aFolder[0] + CONST_FULL_REPORT_RESOURCE + " >")
            try:
                df2 = pd.read_csv(str(aFolder[0]) + CONST_FULL_REPORT_RESOURCE, usecols = CONST_CO_ARDSRIO_FIELDS, names = CONST_HEADER_ARDSRIO, skiprows=1)
            except:
                logger.error( "read_csv() " + CONST_CO_ARDSRIO + " from file < " + aFolder[0] + CONST_FULL_REPORT_RESOURCE + " >")
                df2 = pd.read_csv(str(aFolder[0]) + CONST_FULL_REPORT_RESOURCE, usecols = CONST_CO_ARDSRIO_FIELDS, names = CONST_HEADER_ARDSRIO, skiprows=1, on_bad_lines='skip', engine='python')
            df2 = df2[(df2["TACategory"] == 'cost_optimizing') & (df2["Check"] == CONST_CO_ARDSRIO)]
            df2["EstimatedMonthlySavings"] = df2["EstimatedMonthlySavings"].replace('[\$,]', '', regex=True).astype(float)
            df2 = df2.reset_index()
            df_ta_co_sheet.append( df2)
            df3 = pd.DataFrame(df2.groupby(["Check","InstanceType"]).sum("EstimatedMonthlySavings"))
            df3 = df3.reset_index()
            df3.columns = CONST_COST_PILLAR_COLUMNS_XLS_LIST
            df_ta_co_group.append( df3)
            logger.debug(tabulate.tabulate(df_ta_co_group[co_lines], headers='keys', tablefmt='psql', showindex="always"))
            co_lines += 1

            # Amazon ElastiCache Reserved Node Optimization
            logger.info( CONST_CO_AECRNO + " from file < " + aFolder[0] + CONST_FULL_REPORT_RESOURCE + " >")
            try:
                df2 = pd.read_csv(str(aFolder[0]) + CONST_FULL_REPORT_RESOURCE, usecols = CONST_CO_AECRNO_FIELDS, names = CONST_HEADER_AECRNO, skiprows=1)
            except:
                logger.error( "read_csv() " + CONST_CO_AECRNO + " from file < " + aFolder[0] + CONST_FULL_REPORT_RESOURCE + " >")
                df2 = pd.read_csv(str(aFolder[0]) + CONST_FULL_REPORT_RESOURCE, usecols = CONST_CO_AECRNO_FIELDS, names = CONST_HEADER_AECRNO, skiprows=1, on_bad_lines='skip', engine='python')
            df2 = df2[(df2["TACategory"] == 'cost_optimizing') & (df2["Check"] == CONST_CO_AECRNO)]
            df2["EstimatedMonthlySavings"] = df2["EstimatedMonthlySavings"].replace('[\$,]', '', regex=True).astype(float)
            df2 = df2.reset_index()
            df_ta_co_sheet.append( df2)
            df3 = pd.DataFrame(df2[(df2["TermInYears"] == 'THREE_YEARS')].groupby(["Check","ProductDescription"]).sum("EstimatedMonthlySavings"))
            df3 = df3.reset_index()
            df3.columns = CONST_COST_PILLAR_COLUMNS_XLS_LIST
            df_ta_co_group.append( df3)
            logger.debug(tabulate.tabulate(df_ta_co_group[co_lines], headers='keys', tablefmt='psql', showindex="always"))
            co_lines += 1

            folder += 1
            
            #df_ta_co.append( pd.pivot_table(pd.concat(df_ta_co_group), index=['Check','InstanceType'], values='EstimatedMonthlySavings', aggfunc='sum'))
            df = pd.pivot_table(pd.concat(df_ta_co_group), index=['CostDomain','CostType'], values='EstimatedMonthlySavings')
            df = df.reset_index()
            df.columns = CONST_COST_PILLAR_COLUMNS_XLS_LIST3
            df_ta_co.append( df)
            logger.debug(tabulate.tabulate(df_ta_co[0], headers='keys', tablefmt='psql', showindex="always"))
 
        logger.info('+' + '-'*98 + '+') 
        logger.info("Now merging " + str(len(p_lstFolders)) + " dataframes folders")
        logger.info("Parameter v_GLOBAL_FIRST_LINE_XLS_LIST= [ " + ', '.join(v_GLOBAL_FIRST_LINE_XLS_LIST) +' ]')
        logger.info("Parameter v_COST_PILLAR_FIRST_LINE_XLS_LIST= [ " + ', '.join(v_COST_PILLAR_FIRST_LINE_XLS_LIST) +' ]')
        logger.info("Number of CONST_NAME_SHEETS= " + str(len(CONST_NAME_SHEETS)) + " /Number of df_ta_co_sheet= " + str(len(df_ta_co_sheet)))

        df_ta_se_global = df_ta_se[0]
        if (len(p_lstFolders)>1):
            for i in range(len(df_ta_se)-1):
                df_ta_se_global = pd.merge(df_ta_se_global, df_ta_se[i+1], how="outer", on=["Check","Status","TACategory"])
        
        df_ta_ft_global = df_ta_ft[0]
        if (len(p_lstFolders)>1):
            for i in range(len(df_ta_ft)-1):
                df_ta_ft_global = pd.merge(df_ta_ft_global, df_ta_ft[i+1], how="outer", on=["Check","Status","TACategory"])

        # ------------------------------------ COST OPTIM WORKSHEET
        logger.info("Writing details for worksheet(0) : " + CONST_NAME_SHEETS[0] + ") / Nbr lines = " + str(len(df_ta_co_global)))
        df_ta_co_global = df_ta_co[0]
        if (len(p_lstFolders)>1):
            for i in range(len(df_ta_co)-1):
                # df_ta_co_globalj_crossed = pd.pivot_table(df_ta_co_global[i], index=['Check','InstanceType'], values='EstimatedMonthlySavings', aggfunc='sum')
                # df_ta_co_globalj_crossed2 = pd.pivot_table(df_ta_co_global[i], index=['Check'], values='EstimatedMonthlySavings', aggfunc='sum')
                # multi_index_tuples = [(x, f'{x}_TOTAL') for x in df_ta_co_globalj_crossed2.columns]
                # df_ta_co_globalj_crossed2.columns = pd.MultiIndex.from_tuples(multi_index_tuples, names=['Check', 'InstanceType'])
                # df_ta_co_globalj_crossed2 = df_ta_co_globalj_crossed2.sort_index(axis=1, level=[0,1])
                # happily join on the same index
                # df_ta_co_crossed = pd.merge(df_ta_co_globalj_crossed, df_ta_co_globalj_crossed2, how='left', left_index=True, right_index=True)
                #df_ta_co_crossed.set_axis(v_COST_PILLAR_FIRST_LINE_XLS_LIST, axis=1, inplace=True)
                
                df_ta_co_global = pd.merge(df_ta_co_global, df_ta_co[i+1], how="outer", on=["CostDomain","CostType"])
                logger.debug(tabulate.tabulate(df_ta_co[i+1], headers='keys', tablefmt='psql', showindex="always"))
                #df_ta_co_crossed.to_excel(writer, sheet_name=CONST_NAME_SHEETS[0]) #, columns=v_COST_PILLAR_COLUMNS_XLS_LIST

        logger.debug(tabulate.tabulate(df_ta_co_global, headers='keys', tablefmt='psql', showindex="always"))
        #df_ta_co_global = df_ta_co_global.reset_index()
        df_ta_co_global.columns = v_COST_PILLAR_FIRST_LINE_XLS_LIST 
        df_ta_co_global = pd.pivot_table(df_ta_co_global, index=['CostDomain','CostType'])
        df_ta_co_global.to_excel(writer, sheet_name=CONST_NAME_SHEETS[0])

        # ------------------------------------ SECURITY WORKSHEET
        logger.info("Writing details for worksheet(1) : " + CONST_NAME_SHEETS[1] + ") / Nbr lines = " + str(len(df_ta_se_global)))
        df_ta_se_global.set_axis(v_GLOBAL_FIRST_LINE_XLS_LIST, axis=1, inplace=True)
        df_ta_se_global.to_excel(writer, sheet_name=CONST_NAME_SHEETS[1], columns=v_GLOBAL_COLUMNS_XLS_LIST)

        # ------------------------------------ FAULT TOLERANCE WORKSHEET
        logger.info("Writing details for worksheet(2) : " + CONST_NAME_SHEETS[2] + ") / Nbr lines = " + str(len(df_ta_ft_global)))
        df_ta_ft_global.set_axis(v_GLOBAL_FIRST_LINE_XLS_LIST, axis=1, inplace=True)
        df_ta_ft_global.to_excel(writer, sheet_name=CONST_NAME_SHEETS[2], columns=v_GLOBAL_COLUMNS_XLS_LIST)

        # ------------------------------------ DETAILS WORKSHEETS
        if (len(df_ta_co_sheet)>=1):
            l_firstIndex = int(len(df_ta_co_sheet)/len(p_lstFolders)*(len(p_lstFolders)-1))
            l_lastIndex = int(len(df_ta_co_sheet)-1)
            l_indexSheetName = 3
            logger.info("Writing details for worksheets range(" + str(l_firstIndex) + ' , ' + str(l_lastIndex) + ")")
            for i in range(l_firstIndex,l_lastIndex+1):
                df_ta_co_sheet[i].to_excel(writer, sheet_name=CONST_NAME_SHEETS[l_indexSheetName])
                logger.info("Writing details for worksheet(" + str(i+3) + ') : ' + CONST_NAME_SHEETS[l_indexSheetName] + " / Nbr lines = " + str(len(df_ta_co_sheet[i])))
                l_indexSheetName += 1
 
        workbook  = writer.book

        # Creating COST OPTIM Graph ----------------------------------------------------------------------------------------------
        logger.info("Creating COST OPTIM Graph in XLSX file !")
        title = name = CONST_NAME_SHEETS[0]
        worksheet = writer.sheets[name]
        money_fmt = workbook.add_format({'num_format': '$#,##0'})
        (max_row, max_col) = df_ta_co_global.shape
        worksheet.set_column('C:'+string.ascii_uppercase[max_col+2], 20, money_fmt)
        
        my_format = workbook.add_format({'align': 'center', 'valign': 'center', 'text_wrap': True})
        worksheet.set_column('A:A', 50, my_format)
        
        worksheet.set_column('B:B', 30)
        chart = workbook.add_chart({'type': 'bar'})

        worksheet.insert_chart('G2', chart, {'x_scale': 2, 'y_scale': 2.5})

        total_format = workbook.add_format({'num_format': '$#,##0', 'bold': True, 'font_color': 'red','align': 'right', 'valign': 'right', 'text_wrap': True})
        worksheet.write('B'+str(max_row+3), 'TOTAL', total_format)

        for x in range(1,max_col+1):
            chart.set_title({'name': title})
            showValue=True
            chart.add_series({
                    'categories': '=\''+name+'\'!$A$2:$B$'+str(round(max_row+1)),
                    'values':     '=\''+name+'\'!$'+string.ascii_uppercase[x+1]+'$2:$'+string.ascii_uppercase[x+1]+'$'+str(max_row+1),
                    'name': '=\''+name+'\'!$'+string.ascii_uppercase[x+1]+'$1',
                    'data_labels': {'value': True}})
            worksheet.write_formula(string.ascii_uppercase[x+1]+str(max_row+3), '=SUM('+string.ascii_uppercase[x+1]+'2:'+string.ascii_uppercase[x+1]+str(max_row+1) + ')', total_format)
            logger.info('Adding CHART  : categories: ='+name+'!$A$2:$B$'+str(round(max_row+1)))
            logger.info('              : values    : ='+name+'\'!$'+string.ascii_uppercase[x+1]+'$2:$'+string.ascii_uppercase[x+1]+'$'+str(max_row+1))
            logger.info('              : name      : ='+name+'\'!$'+string.ascii_uppercase[x+1]+'$1')        

        # Creating SECURITY Graph ----------------------------------------------------------------------------------------------
        logger.info("Creating SECURITY Graph in XLSX file !")
        title = name = CONST_NAME_SHEETS[1]
        worksheet = writer.sheets[name]
        worksheet.set_column('C:C', 100)
        chart = workbook.add_chart({'type': 'bar'})

        worksheet.insert_chart('G2', chart, {'x_scale': 2, 'y_scale': 4})
        (max_row, max_col) = df_ta_se_global.shape

        for x in range(3,max_col):
            chart.set_title({'name': title})
            if (x==(max_col)):
                continue
            chart.set_title({'name': title})
            showValue=False
            if (x==(max_col-1)):
                showValue=True
            chart.add_series({
                'categories': '=\''+name+'\'!$B$2:$C$'+str(max_row+1),
                'values': '=\''+name+'\'!$'+string.ascii_uppercase[x+1]+'$2:$'+string.ascii_uppercase[x+1]+'$'+str(max_row+1),
                'name': '=\''+name+'\'!$'+string.ascii_uppercase[x+1]+'$1',
                'data_labels': {'value': showValue}})
            logger.info('Adding CHART  : categories: ='+name+'!$B$2:$C$'+str(max_row+1))
            logger.info('              : values    : ='+name+'!$'+string.ascii_uppercase[x]+'$2:$'+string.ascii_uppercase[x+1]+'$'+str(max_row+1))
            logger.info('              : name      : ='+ '='+name+'!$'+string.ascii_uppercase[x+1]+'$1')

        # Creating FAULT TOLERANCE Graph ---------------------------------------------------------------------------------------
        logger.info("Creating FAULT TOLERANCE Graph in XLSX file !")
        title = name = CONST_NAME_SHEETS[2]
        worksheet = writer.sheets[name]
        worksheet.set_column('C:C', 100)
        chart = workbook.add_chart({'type': 'bar'})

        worksheet.insert_chart('G2', chart, {'x_scale': 2, 'y_scale': 2})
        (max_row, max_col) = df_ta_ft_global.shape

        for x in range(3,max_col):
            if (x==(max_col)):
                continue
            chart.set_title({'name': title})
            showValue=False
            if (x==(max_col-1)):
                showValue=True
            chart.add_series({
                'categories': '=\''+name+'\'!$B$2:$C$'+str(max_row+1),
                'values': '=\''+name+'\'!$'+string.ascii_uppercase[x+1]+'$2:$'+string.ascii_uppercase[x+1]+'$'+str(max_row+1),
                'name': '=\''+name+'\'!$'+string.ascii_uppercase[x+1]+'$1',
                'data_labels': {'value': showValue}})
            logger.info('Adding CHART  : categories: ='+name+'!$B$2:$C$'+str(max_row+1))
            logger.info('              : values    : ='+name+'!$'+string.ascii_uppercase[x]+'$2:$'+string.ascii_uppercase[x+1]+'$'+str(max_row+1))
            logger.info('              : name      : ='+name+'!$'+string.ascii_uppercase[x+1]+'$1')
        
        #writer.save()    
        writer.close()

        print(tabulate.tabulate(df_ta_se_global, headers='keys', tablefmt='psql', showindex="always"))
        print(tabulate.tabulate(df_ta_ft_global, headers='keys', tablefmt='psql', showindex="always"))
        print(tabulate.tabulate(df_ta_co_global.reset_index(), headers='keys', tablefmt='psql', showindex="always"))

        logger.info("!!! Please consult result in XLSX file : <"+ v_FILENAME_EXCEL_FILE +">")
        os.system(v_FILENAME_EXCEL_FILE)


    #----------------------------------------------------------------------------------------------------------------------------------------------
    def get_list_accounts(self, type_of_input, input_value):

        if (type_of_input == CONST_DOMAIN):
            parser = self.cmdline_parser_lst_accounts_for_domain( input_value, v_LIST_ACCOUNTS_FILE)
            v_CMD = "bin/tatool.py -d " + input_value + " -generateaccountslistonly " + CONST_ACCOUNTS_LIST_FILENAME + " -bca 'TAM duty'"
        elif (type_of_input == CONST_PAYERID):
            parser = self.cmdline_parser_lst_accounts_for_payerid( input_value, v_LIST_ACCOUNTS_FILE)
            v_CMD = "bin/tatool.py -p " + input_value + " -generateaccountslistonly " + CONST_ACCOUNTS_LIST_FILENAME + " -bca 'TAM duty'"

        logger.info( "Call tatool.py tool : <" + v_CMD + " >")
        exec_tatool.run(parser)
                       

    #----------------------------------------------------------------------------------------------------------------------------------------------
    def RepresentsInt(s):
        try: 
            int(s)
            return True
        except ValueError:
            return False

    #----------------------------------------------------------------------------------------------------------------------------------------------
	# 1) bin/tatool.py -a/p/d >> csv file
	# 2) Filter tatool results based on 'security'/'fault_tolerance'/'cost_optimization'
    #----------------------------------------------------------------------------------------------------------------------------------------------
    def generate_graph_xlsx_from_csv(self, p_XLS_FILENAME, p_ROOT):

        # Create a Pandas Excel writer using XlsxWriter as the engine.
        writer = pd.ExcelWriter(p_XLS_FILENAME, engine='xlsxwriter')
		
        lst_folders = glob2.glob('202?-*')
        title = 'Please choose the folders to process: '
        option = pick(lst_folders, title, multiselect=True, min_selection_count=1)
        print(option)

        #-------------- SECURITY ------------------
        lst_files = glob2.glob(os.path.join(option[0][0], "report*"+CONST_SC+".csv"))
        for folder in option:
            lst_files += glob2.glob(os.path.join(folder[0], "sc*.csv"))

        dt = pd.read_csv( lst_files[0][0])

        for aFile in lst_files[1:]:
            dt = pd.merge( dt, pd.read_csv( aFile[0]), on=['Check','Result'])

        # Convert the dataframe to an XlsxWriter Excel object.
        dt.to_excel(writer, sheet_name=CONST_SC)

        #-------------- FAULT_TOLERANCE ------------------
        lst_files = glob2.glob(os.path.join(option[0][0], "report*"+CONST_FT+".csv"))
        for folder in option:
            lst_files += glob2.glob(os.path.join(option[0][0], "ft*.csv"))

        dt = pd.read_csv( lst_files[0][0])

        for aFile in lst_files[1:]:
            dt = pd.merge( dt, pd.read_csv( aFile[0]), on=['Check','Result'])

        # Convert the dataframe to an XlsxWriter Excel object.
        dt.to_excel(writer, sheet_name=CONST_FT)

        #-------------- COST_OPTIMIZATION ------------------
        lst_files = glob2.glob(os.path.join(option[0][0], "report*"+CONST_CO+".csv"))
        for folder in option:
            lst_files += glob2.glob(os.path.join(option[0][0], "co*.csv"))

        if len(lst_files)>=1:
            dt = pd.read_csv( lst_files[0][0])

        for aFile in lst_files[1:]:
            dt = pd.merge( dt, pd.read_csv( aFile[0]), on=['Check','Result'])

        # Convert the dataframe to an XlsxWriter Excel object.
        dt.to_excel(writer, sheet_name=CONST_CO)

        # Close the Pandas Excel writer and output the Excel file.
        writer.save()

    #----------------------------------------------------------------------------------------------------------------------------------------------
    def convert_json_to_csv(self, JSON_FILE, CSV_FILE):
        df_ta =  pd.read_json( JSON_FILE)
        df_ta2 = pd.DataFrame(df_ta)
        df_ta2.to_csv( CSV_FILE, header=None)

    #----------------------------------------------------------------------------------------------------------------------------------------------
	# 1) bin/tatool.py -a/p/d >> csv file
	# 2) Filter tatool results based on 'security'/'fault_tolerance'/'cost_optimization'
    #----------------------------------------------------------------------------------------------------------------------------------------------
    def process_tatool(self, type_of_input, input_value):

        logger.info("WORKING DIRECTORY IS < " + v_TODAY_DATETIME + " >")

        my_file = Path( "./" + v_TODAY_DATETIME)
        if not my_file.is_dir():
            logger.info( "Creating directory :" + v_TODAY_DATETIME)
            os.mkdir( v_TODAY_DATETIME)
        
        f = open( "./" + v_TODAY_DATETIME + "/" + v_NAME, "a")
        f.write( v_MONTH_DATETIME)
        f.close()
        v_CMD = "bin/tatool.py "
        v_LOCAL_TATOOL_FILE = v_TODAY_DATETIME + "/"
        v_S3_TATOOL_FILE = "tatool/"

        if (type_of_input == CONST_ACCOUNTID):
                logger.info("List of accounts for tatool tool : < " + input_value + " >")
                v_CMD += "-a " + input_value + " -threads " + v_THREAD + " -g -b " + v_S3_BUCKET + " -t -bca 'TAM DUTY'"
                parser = self.cmdline_parser_ta_for_accountid(input_value, my_file)
        elif (type_of_input == CONST_DOMAIN):
                v_CMD += "-d " + input_value + " -threads " + v_THREAD + " -g -b " + v_S3_BUCKET + " -t -bca 'TAM DUTY'"
                
                parser = self.get_list_accounts(type_of_input, input_value)

                df_list_accounts =  pd.read_csv(v_LIST_ACCOUNTS_FILE, usecols=['AccountId','Account_Name'], converters={'accountId': str}, skip_blank_lines=True).dropna()
                v_TATOOL_LST_ACCOUNTS = re.sub('\n', ' ', df_list_accounts['AccountId'].to_string(index=False, header=False))
                v_LST_ACCOUNTS = df_list_accounts['AccountId'].values.tolist()
                logger.info("List of accounts for tatool tool : < " + v_TATOOL_LST_ACCOUNTS + " >")
        
                v_FIRST_ACCOUNT = str(df_list_accounts['AccountId'][0])
                v_LOCAL_TATOOL_FILE += input_value + "_" + v_TODAY_DATETIME + "_TA.zip"
                v_S3_TATOOL_FILE += input_value + "/" + input_value + "_" + v_TODAY_DATETIME + "_TA.zip"

                my_file = Path( v_LOCAL_TATOOL_FILE)
                if not my_file.is_file():
                    parser = self.cmdline_parser_ta_for_domain(input_value, my_file)

        elif (type_of_input == CONST_PAYERID):
                v_CMD += "-p " + input_value + " -threads " + v_THREAD + " -g -b " + v_S3_BUCKET + " -t -bca 'TAM DUTY'"

                parser = self.get_list_accounts(type_of_input, input_value)

                df_list_accounts =  pd.read_csv(v_LIST_ACCOUNTS_FILE, usecols=['AccountId','Account_Name'], converters={'accountId': str}, skip_blank_lines=True).dropna()
                v_TATOOL_LST_ACCOUNTS = re.sub('\n', ' ', df_list_accounts['AccountId'].to_string(index=False, header=False))
                v_LST_ACCOUNTS = df_list_accounts['AccountId'].values.tolist()
                logger.info("List of accounts for tatool tool : < " + v_TATOOL_LST_ACCOUNTS + " >")
        
                v_FIRST_ACCOUNT = str(df_list_accounts['AccountId'][0])
                v_LOCAL_TATOOL_FILE += "payer_" + input_value + "_" + v_TODAY_DATETIME + "_TA.zip"
                v_S3_TATOOL_FILE += "payer_" + input_value + "/" + input_value + "_" + v_TODAY_DATETIME + "_TA.zip"

                my_file = Path( v_LOCAL_TATOOL_FILE)
                if not my_file.is_file():
                    parser = self.cmdline_parser_ta_for_payerid(input_value, my_file)

        logger.info( "Call tatool.py tool : <" + v_CMD + " >")
        exec_tatool.run(parser)                       

        s3 = boto3.resource('s3')
        logger.info( "download_file Bucket = : <" + v_S3_BUCKET + " Key = " + v_S3_TATOOL_FILE + ">")
        s3.meta.client.download_file( Bucket = v_S3_BUCKET, Key = v_S3_TATOOL_FILE, Filename = v_LOCAL_TATOOL_FILE)        
        
        print( "Unziping tatool file : < " + v_LOCAL_TATOOL_FILE + " >")
        my_file = Path( v_LOCAL_TATOOL_FILE)
        if my_file.is_file():
            zf = ZipFile( v_LOCAL_TATOOL_FILE, 'r')
            zf.extractall( v_TODAY_DATETIME)
            zf.close()
        
        else:
            logger.error('\033[31m' + "ERROR : No TA file details found in working directory !")


    #----------------------------------------------------------------------------------------------------------------------------------------------
    def execute(self):
        init(autoreset=True)
        os.system('cls')
        print('+' + '-'*98 + '+') 
        print("| \033[1;41m GENERATE TRUSTED ADVISOR FOLLOWUP XLS - TAM TOOL \033[1;0m" + ' '*(99-len("| GENERATE TRUSTED ADVISOR FOLLOWUP XLS - TAM TOOL  ")) + "|") 
        print('|' + ' '*98 + '|') 
        print("|    Opt-out : https://aea.aka.amazon.com/users/slepetre" + ' '*(99-len("|    Opt-out : https://aea.aka.amazon.com/users/slepetre")) + "|") 
        print("|    mwinit --username slepetre --aea" + ' '*(99-len("|    mwinit --username slepetre --aea")) + "|") 
        print("|    S3_BUCKET = " + v_S3_BUCKET + ' '*(99-len("|    S3_BUCKET = " + v_S3_BUCKET)) + "|")
        print("|    TATOOL_FILES = " + CONST_FULL_REPORT_RESOURCE + ' '*(99-len("|    TATOOL_FILES = " + CONST_FULL_REPORT_RESOURCE)) + "|")
        print("|         https://aws-ciw-readonly.amazon.com/cost-management/home?spoofAccountId=???#/rightsizing |")
        print('+' + '-'*98 + '+') 
        menu = {}
        menu['\033[1;41m 1 \033[1;0m']="- Retreive TA checks for a domain using tatool (start by retreiving list of linked accounts)" 
        menu['\033[1;41m 2 \033[1;0m']="- Generate XLS of TA SECU + FT+ CO from selected folders (Tatool files + EC2 rightsizing)"
        menu['\033[1;41m 3 \033[1;0m']="-------------------------------------------------------------------------------------------------" 
        menu['\033[1;41m 4 \033[1;0m']="- Retreive TA checks for a payerID (start by retreiving list of linked accounts)" 
        menu['\033[1;41m 5 \033[1;0m']="- Retreive TA checks for an accountID" 
        menu['\033[1;41m 6 \033[1;0m']="- Retreive TA checks using accounts listed in " + CONST_ACCOUNTS_LIST_FILENAME
        menu['\033[1;41m 7 \033[1;0m']="- Convert JSON file :" + CONST_ACCOUNTS_LIST_FILENAME_JSON + " in CSV file :" + CONST_ACCOUNTS_LIST_FILENAME
        menu['\033[1;41m 8 \033[1;0m']="- Get list of linked accounts for a DOMAIN"
        menu['\033[1;41m 9 \033[1;0m']="- Get list of linked accounts for a payerID"
        menu['\033[1;41m q \033[1;0m']="- Quit"
        print('+' + '-'*98 + '+') 
        g_lst_folders = []
        my_option = []

        while True: 
            g_lst_folders.clear()
            lst_files = glob2.glob('./202?-??-??/unfiltered/full_report_with_resource-ids.csv')
            for fn in lst_files:
                l_aPath = pathlib.PurePath(fn)
                g_lst_folders.append(l_aPath.parent.parent.as_posix())
            
            print("                                        MENU" + ' '*(99-len("                                        MENU" )) + " ")
            print('+' + '-'*98 + '+') 
            print('+' + '-'*98 + '+') 
            options=menu.keys()
            for entry in options: 
                print(entry, menu[entry])

            print('+' + '-'*98 + '+') 
            selection = input("\033[1;41m Please Select: \033[1;0m") 
            if (selection == '1'):
                print('+' + '-'*98 + '+') 
                input_value = input('Enter domain: ')
                #self.get_list_accounts(CONST_DOMAIN, input_value)
                self.process_tatool(CONST_DOMAIN, input_value)
                print('-'*20 + " DONE " +'-'*20)
            elif (selection == '2'):
                if len(g_lst_folders)<1:
                    logger.info(" ERROR NO FOLDER WITH TATOOL RESULTS !!!")
                    print('+' + '-'*98 + '+') 
                else:
                    title = 'Please choose the folders to process: '
                    my_option.clear()
                    my_option = pick(g_lst_folders, title, multiselect=True, min_selection_count=1)
                    self.generate2_xls_from_ta_csv( "followup.xlsx", my_option, v_MONTH_DATETIME, v_FULL_DATETIME)
                    print('-'*20 + " DONE " +'-'*20)
                    print('.')
                    print('.')
                    print('.')
            elif (selection == '4'):
                print('+' + '-'*98 + '+') 
                input_value = input('Enter payerid: ')
                #self.get_list_accounts(CONST_PAYERID, input_value)
                self.process_tatool(CONST_PAYERID, input_value)
                print('-'*20 + " DONE " +'-'*20)
            elif (selection == '5'):
                print('+' + '-'*98 + '+') 
                input_value = input('Enter accountid: ')
                self.process_tatool(CONST_ACCOUNTID, input_value)
                print('-'*20 + " DONE " +'-'*20)
            elif (selection == '6'):
                print('+' + '-'*98 + '+') 
                self.process_tatool('file', CONST_ACCOUNTS_LIST_FILENAME)
                print('-'*20 + " DONE " +'-'*20)
            elif (selection == '7'):
                print('+' + '-'*98 + '+') 
                self.convert_json_to_csv(self, CONST_ACCOUNTS_LIST_FILENAME_JSON, CONST_ACCOUNTS_LIST_FILENAME)
                print('-'*20 + " DONE " +'-'*20)
            elif (selection == '8'):
                print('+' + '-'*98 + '+') 
                input_value = input('Enter DOMAIN (Ex. dalkia.fr): ')
                self.get_list_accounts(CONST_DOMAIN, input_value)
                print('-'*20 + " DONE " +'-'*20)
            elif (selection == '9'):
                print('+' + '-'*98 + '+') 
                input_value = input('Enter payerID (Ex. 11223093409): ')
                self.get_list_accounts(CONST_PAYERID, input_value)
                print('-'*20 + " DONE " +'-'*20)
            elif (selection == 'q'):
                break
            else: 
                print("Unknown Option Selected !")

if __name__ == "__main__":
    program = TatoolFollowUp()
    program.execute()

