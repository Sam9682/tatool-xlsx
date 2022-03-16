import argparse
import logging
import sys
import os
import getpass
import tempfile
import json
import shutil
import platform
import dateparser

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

logger = logging.getLogger(__name__)

from datetime import datetime, timedelta
from shutil import copyfile
from app_classes.config import Config
from app_classes.aws_account import aws_account
from app_classes.trusted_advisor import TrustedAdvisor
from app_classes.reserved_instances import Reserved_Instances
from app_classes.zipper import Zipper
from app_classes.excel_graphs_data import excel_graphs_data
from app_classes.global_excel_graphs_writer import global_excel_graphs_writer
from app_classes.global_trends_graphs_writer import global_excel_trends_graphs_writer
from app_classes.update_trends import Update_Trends
from app_classes.account_excel_graphs_writer import Account_Level_Graphs
from app_classes.ri_excel_graphs_writer import ri_excel_graphs_writer
from app_classes.s3_handler import S3Handler
from app_classes.support_cases import SupportCases
from app_classes.k2helper import k2workbench
from app_classes.get_bca import BCA

#from app_classes.mailsend import Mailsend

class tatool:
    def __init__(self):
        self.counter=0
        self.args=[]
        
    #----------------------------------------------------------------------------------------------------------------------------------------------
    def cmdline_parser(self):
        now = datetime.now()
        date_120_days_ago = dateparser.parse('120 days ago')
        parser = argparse.ArgumentParser(
            description='Tatool - Enterprise Customer Trusted Advisor detailed view'
        )
        parser.add_argument('-a', '--account_id', nargs='+', dest='account_id', type=str, required=False, default=False,
                            help='Customer AccountId. If specified it runs only for this account')
        parser.add_argument('-accfile', '--accounts_file', dest='accounts_file', type=str, required=False, default=False,
                            help='File with a list of Customer AccountId. If specified it runs only for the list of accounts specified in the file.It must be specified a single account for each line of the file. Look at README for a file sample.')
        parser.add_argument('-b', '--bucket-s3', dest='s3bucket', type=str, required=False,
                            help='This is the S3 bucket where the Tatool data will be stored.')
        parser.add_argument('-bca', '--bca-reason', dest='bcareason', type=str, required=False,
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
        parser.add_argument('-generateaccountslistonly', '--generateaccountslistonly', dest='generateaccountslistonly', required=False, default=False,
                            help='The option allows to write on file the account list associated with account name or mail and after that the script exits.')
        parser.add_argument("-l", "--log", dest="logLevel", default='INFO',
                            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help="Set the logging level")
        parser.add_argument('-no_update_trends', '--no_update_trends', dest='no_update_trends', action="store_true",
                            help='Option to avoid that the trend history is updated. If specified the trend will not update the historic statistics')
        parser.add_argument('-o', '--output_file', dest='output_file',
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
        parser.add_argument('-threads', '--threads', dest='threads',
                            type=int, required=False, default=10, help='Number of concurrent k2 api calls. Default: 10')
        parser.add_argument('-t', '--trusted_advisor', dest='trusted_advisor', action="store_true",
                            help='Run the Trusted Advisor checks for the accounts.')
        """
        #Send mail report, ready to be implemented in case of a host running in batch for multiple customers.
        parser.add_argument('-to', '--to', dest='email_address',
                            type=str, required=False, default=getpass.getuser() + '@amazon.com',
                            help='Email address to send the CWCB report. Default: ' + getpass.getuser() + '@amazon.com.')
        """

        input_args = parser.parse_args()

        input_args.output_dir = tempfile.mkdtemp()
        input_args.tempdirzip = tempfile.mkdtemp()

        logging.basicConfig(level=getattr(logging, input_args.logLevel))

        if input_args.accounts_file:
            with open(input_args.accounts_file) as f:
                input_args.account_id = f.read().splitlines()

        if input_args.customer_domain:
            input_args.payers_id = None
            input_args.account_id = None
            input_args.output_dir = input_args.output_dir + '/' + input_args.customer_domain + '.report.' + now.strftime('%Y-%m-%d') + '/'
            input_args.s3_key_path = 'tatool/' + input_args.customer_domain + '/'
        elif input_args.payers_id:
            input_args.account_id = None
            input_args.output_dir = input_args.output_dir + '/' + 'payer_' + input_args.payers_id[0] + '.report.' + now.strftime(
                '%Y-%m-%d') + '/'
            input_args.s3_key_path = 'tatool/' + 'payer_' + input_args.payers_id[0] + '/'
        elif input_args.account_id:
            first_account_of_the_list = input_args.account_id[0]
            if len(input_args.account_id) > 1:
                input_args.output_dir = input_args.output_dir + '/' + first_account_of_the_list + '_and_others.report.' + now.strftime('%Y-%m-%d') + '/'
                input_args.s3_key_path = 'tatool/' + first_account_of_the_list + '_and_others.report' + '/'
            else:
                input_args.output_dir = input_args.output_dir + '/' + first_account_of_the_list + '.report.' + now.strftime('%Y-%m-%d') + '/'
                input_args.s3_key_path = 'tatool/' + first_account_of_the_list + '.report' + '/'
        elif not input_args.account_id:
            logging.info("Please specify domain, payer-id or account-id to run the script!")
            return(0)

        if input_args.generateaccountslistonly is False:
            if not input_args.trusted_advisor and not input_args.support_cases:
                logging.info("Please specify -t for Trusted Advisor and/or -s for Support Cases!")
                return(0)

            if input_args.ta_checks_pdf and not input_args.trusted_advisor:
                logging.info("Please specify -t for Trusted Advisor and -pdf for PDF file generation")
                return(0)

            if input_args.s3bucket is None:
                logging.error('Please specify a valid S3 bucket to upload the data!')
                return(0)
    
        if input_args.ta_checks_pdf:
            environment = platform.system()
            if environment == "Windows":
                if not os.path.isfile("C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe"):
                    logging.info("Please install wkhtmltopdf (https://wkhtmltopdf.org/) before using -pdf parameter")
                    return(0)
            elif environment == "Darwin":
                if not os.path.isfile("/usr/local/bin/wkhtmltopdf"):
                    logging.info("Please install wkhtmltopdf (https://wkhtmltopdf.org/) before using -pdf parameter")
                    return(0)
            elif environment == "Linux":
                if not os.path.isfile("/usr/bin/wkhtmltopdf"):
                    logging.info("Please install wkhtmltopdf (sudo apt-get install wkhtmltopdf) before using -pdf parameter")
                    return(0)

        input_args.unfiltered_folder = input_args.output_dir + 'unfiltered/'
        if not os.path.exists(input_args.unfiltered_folder):
            os.makedirs(input_args.unfiltered_folder)
        input_args.relevant_savings_folder = input_args.output_dir + 'relevant_savings_folder/'
        if not os.path.exists(input_args.relevant_savings_folder):
            os.makedirs(input_args.relevant_savings_folder)
        input_args.isSuppressed_folder = input_args.output_dir + 'isSuppressed_filter/'
        if not os.path.exists(input_args.isSuppressed_folder):
            os.makedirs(input_args.isSuppressed_folder)
        if input_args.filter_file_ta is not None:
            input_args.filtered_folder = input_args.output_dir + 'filtered/'
            if not os.path.exists(input_args.filtered_folder):
                os.makedirs(input_args.filtered_folder)

        if input_args.displayformat != 'accountid':
            if input_args.displayformat != 'name':
                input_args.displayformat = 'email'

        if input_args.support_cases:
            input_args.cases_end_time = dateparser.parse(input_args.cases_end_time)
            input_args.cases_end_time = input_args.cases_end_time.strftime('%Y-%m-%dT23:59:59.999Z')
            input_args.cases_start_time = dateparser.parse(input_args.cases_start_time)
            input_args.cases_start_time = input_args.cases_start_time.strftime('%Y-%m-%dT00:00:00.000Z')
            input_args.support_cases_folder = input_args.output_dir + 'support_cases/'
            if not os.path.exists(input_args.support_cases_folder):
                os.makedirs(input_args.support_cases_folder)

        if input_args.ta_checks_pdf:
            input_args.ta_checks_pdf_folder = input_args.output_dir + 'ta_checks_pdf/'
            if not os.path.exists(input_args.ta_checks_pdf_folder):
                os.makedirs(input_args.ta_checks_pdf_folder)

        return input_args

    #----------------------------------------------------------------------------------------------------------------------------------------------
    def params_parser( self, p_args):
        now = datetime.now()
        date_120_days_ago = dateparser.parse('120 days ago')
        input_args = p_args.parse_args()
        

        input_args.output_dir = tempfile.mkdtemp()
        input_args.tempdirzip = tempfile.mkdtemp()

        logging.basicConfig(level=getattr(logging, input_args.logLevel))

        if input_args.accounts_file:
            with open(input_args.accounts_file) as f:
                input_args.account_id = f.read().splitlines()

        if input_args.customer_domain:
            input_args.payers_id = None
            input_args.account_id = None
            input_args.output_dir = input_args.output_dir + '/' + input_args.customer_domain + '.report.' + now.strftime('%Y-%m-%d') + '/'
            input_args.s3_key_path = 'tatool/' + input_args.customer_domain + '/'
        elif input_args.payers_id:
            input_args.account_id = None
            input_args.output_dir = input_args.output_dir + '/' + 'payer_' + input_args.payers_id[0] + '.report.' + now.strftime(
                '%Y-%m-%d') + '/'
            input_args.s3_key_path = 'tatool/' + 'payer_' + input_args.payers_id[0] + '/'
        elif input_args.account_id:
            first_account_of_the_list = input_args.account_id[0]
            if len(input_args.account_id) > 1:
                input_args.output_dir = input_args.output_dir + '/' + first_account_of_the_list + '_and_others.report.' + now.strftime('%Y-%m-%d') + '/'
                input_args.s3_key_path = 'tatool/' + first_account_of_the_list + '_and_others.report' + '/'
            else:
                input_args.output_dir = input_args.output_dir + '/' + first_account_of_the_list + '.report.' + now.strftime('%Y-%m-%d') + '/'
                input_args.s3_key_path = 'tatool/' + first_account_of_the_list + '.report' + '/'
        elif not input_args.account_id:
            logging.info("Please specify domain, payer-id or account-id to run the script!")
            return(0)

        if input_args.generateaccountslistonly is False:
            if not input_args.trusted_advisor and not input_args.support_cases:
                logging.info("Please specify -t for Trusted Advisor and/or -s for Support Cases!")
                return(0)

            if input_args.ta_checks_pdf and not input_args.trusted_advisor:
                logging.info("Please specify -t for Trusted Advisor and -pdf for PDF file generation")
                return(0)

            if input_args.s3bucket is None:
                logging.error('Please specify a valid S3 bucket to upload the data!')
                return(0)
    
        if input_args.ta_checks_pdf:
            environment = platform.system()
            if environment == "Windows":
                if not os.path.isfile("C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe"):
                    logging.info("Please install wkhtmltopdf (https://wkhtmltopdf.org/) before using -pdf parameter")
                    return(0)
            elif environment == "Darwin":
                if not os.path.isfile("/usr/local/bin/wkhtmltopdf"):
                    logging.info("Please install wkhtmltopdf (https://wkhtmltopdf.org/) before using -pdf parameter")
                    return(0)
            elif environment == "Linux":
                if not os.path.isfile("/usr/bin/wkhtmltopdf"):
                    logging.info("Please install wkhtmltopdf (sudo apt-get install wkhtmltopdf) before using -pdf parameter")
                    return(0)

        input_args.unfiltered_folder = input_args.output_dir + 'unfiltered/'
        if not os.path.exists(input_args.unfiltered_folder):
            os.makedirs(input_args.unfiltered_folder)
        input_args.relevant_savings_folder = input_args.output_dir + 'relevant_savings_folder/'
        if not os.path.exists(input_args.relevant_savings_folder):
            os.makedirs(input_args.relevant_savings_folder)
        input_args.isSuppressed_folder = input_args.output_dir + 'isSuppressed_filter/'
        if not os.path.exists(input_args.isSuppressed_folder):
            os.makedirs(input_args.isSuppressed_folder)
        if input_args.filter_file_ta is not None:
            input_args.filtered_folder = input_args.output_dir + 'filtered/'
            if not os.path.exists(input_args.filtered_folder):
                os.makedirs(input_args.filtered_folder)

        if input_args.displayformat != 'accountid':
            if input_args.displayformat != 'name':
                input_args.displayformat = 'email'

        if input_args.support_cases:
            input_args.cases_end_time = dateparser.parse(input_args.cases_end_time)
            input_args.cases_end_time = input_args.cases_end_time.strftime('%Y-%m-%dT23:59:59.999Z')
            input_args.cases_start_time = dateparser.parse(input_args.cases_start_time)
            input_args.cases_start_time = input_args.cases_start_time.strftime('%Y-%m-%dT00:00:00.000Z')
            input_args.support_cases_folder = input_args.output_dir + 'support_cases/'
            if not os.path.exists(input_args.support_cases_folder):
                os.makedirs(input_args.support_cases_folder)

        if input_args.ta_checks_pdf:
            input_args.ta_checks_pdf_folder = input_args.output_dir + 'ta_checks_pdf/'
            if not os.path.exists(input_args.ta_checks_pdf_folder):
                os.makedirs(input_args.ta_checks_pdf_folder)

        return input_args

    #----------------------------------------------------------------------------------------------------------------------------------------------
    def get_active_accounts_and_display_option_tuples_list(self, input_args):

        active_accounts_list = []
        acc = aws_account(input_args)

        if input_args.customer_domain:
            payers_list = acc.get_customer_payer_accounts(input_args.customer_domain, "WEB_DOMAIN")
            scope = "WEB_DOMAIN"
        elif input_args.payers_id:
            payers_list = acc.get_customer_payer_accounts(input_args.payers_id, "ACCOUNT_ID")
            scope = "payerId"
        elif input_args.account_id:
            payers_list = acc.get_customer_payer_accounts(input_args.account_id, "ACCOUNT_ID")
            scope = "accountId"
        active_accounts_list = acc.get_linked_accounts(payers_list, scope)

        if input_args.displayformat == 'accountid':
            active_accounts_and_display_option_tuples_list = acc.display_accountid(active_accounts_list)
        elif input_args.displayformat == 'name':
            active_accounts_and_display_option_tuples_list = acc.kick_parallel_get_name(active_accounts_list)
        else: active_accounts_and_display_option_tuples_list = acc.kick_parallel_get_email(active_accounts_list)

        clean_active_accounts_and_display_option_tuples_list = acc.check_duplicates(active_accounts_and_display_option_tuples_list)

        if input_args.generateaccountslistonly is not False:
            acc.dump_list_to_file(clean_active_accounts_and_display_option_tuples_list)
            return(0)
        else:
            return clean_active_accounts_and_display_option_tuples_list

    #----------------------------------------------------------------------------------------------------------------------------------------------
    # payers_id, account_id, customer_domain, bcareason, output_file, output_dir, tempdirzip, s3_key_path, no_update_trends, generateaccountslistonly, trusted_advisor, refresh_ta_checks, filter_file_ta, ta_checks_pdf, graphs_ta, ri_opportunities,support_cases
    def run( self, p_args):
        startTime = datetime.now()
        input_args = self.params_parser( p_args)
        print(str(input_args))

        #if sys.version_info[0] > 2:
        #    logging.error('\033[31m' + "Please run the script with Python 2 and check requirements!")
        #    return(1)

        k2 = k2workbench()
        midway_check = k2.check_midway_cookies()
        bca = BCA(input_args)
        bca.work_bca_reason()
        bca.submit_bca_request()

        if not input_args.generateaccountslistonly:
            s3 = S3Handler(input_args)
            def_con = Config()
            bucket_true = s3.check_bucket_exists()
            if bucket_true == False:
                logging.error('S3 Bucket not found! Please check the command!')
                return(1)

        clean_active_accounts_and_display_option_tuples_list = self.get_active_accounts_and_display_option_tuples_list(input_args)
        if clean_active_accounts_and_display_option_tuples_list == 0:
            return
        if input_args.trusted_advisor:
            json_trends_file = s3.get_json_file()
            if json_trends_file == False:
                json_trends_dict = def_con.default_json_dict()
                logging.warning("Values trends json file not found in the S3 path, using the default one.")
            else:
                logging.info("Downloaded trend file from S3.")
                json_trends_dict = json.loads(json_trends_file)
                json_trends_dict = def_con.check_trend_dict_updated(json_trends_dict)

            ta = TrustedAdvisor(input_args)
            check_account_detail_tuple_list = ta.kick_parallel_Describe_Check( clean_active_accounts_and_display_option_tuples_list)

            if input_args.refresh_ta_checks:
                ta.refresh_ta_checks(check_account_detail_tuple_list)

            ta.kick_parallel_getCheckDetail(check_account_detail_tuple_list)

            ta.write_unfiltered_output_file()

            ta.unfiltered_split_by_account()

            ta.unfiltered_split_by_checkname()

            ta.write_relevant_savings()

            ta.generate_isSuppressed()
            ta.not_suppressed_split_by_account()
            ta.not_suppressed_split_by_check_name()

            if input_args.filter_file_ta is not None:
                ta.filter_ta_file()
                ta.filtered_split_by_account()
                ta.filtered_split_by_checkname()
        
            if input_args.ta_checks_pdf is not None and input_args.ta_checks_pdf is not False:
                from app_classes.ta_checks_pdf_writer import TAChecksPdfWriter
                tapdf = TAChecksPdfWriter(input_args)
                tapdf.write_ta_check_pdfs()

            if input_args.graphs_ta:
                x = excel_graphs_data(input_args)
                graphs_data_dict = x.create_graphs_data_dict()

                write = global_excel_graphs_writer(input_args)
                write.create_global_charts(graphs_data_dict)

                ut = Update_Trends()
                json_trends_dict = ut.update_trends_stats(graphs_data_dict, json_trends_dict)

                xt = global_excel_trends_graphs_writer(input_args)
                xt.create_global_trends_charts(json_trends_dict)

                ag = Account_Level_Graphs(input_args)
                ag.create_details_chart(graphs_data_dict)

            if input_args.ri_opportunities:
                ri = Reserved_Instances(input_args)
                ri.write_ri_detail_file()
                ri_info_folder, one_year_first_five_savings_opportunity, three_year_first_five_savings_opportunity = ri.create_graph_data()
                rixls = ri_excel_graphs_writer(input_args)
                rixls.create_ri_graphs(ri_info_folder, one_year_first_five_savings_opportunity,
                                   three_year_first_five_savings_opportunity)

            json_string = json.dumps(json_trends_dict)

            values_trends_filename = input_args.output_dir + '/' + 'values_trends.json'

            try:
                with open(values_trends_filename, mode="w") as f:
                    f.write(json_string)
            except Exception as e:
                print(e)


        if input_args.support_cases:
            sc = SupportCases(input_args)
            cases_list = sc.kick_parallel_searchCases(clean_active_accounts_and_display_option_tuples_list)
            sc.write_support_cases_file(cases_list)
            if input_args.graphs_ta:
                sc.create_support_cases_graph_dict()
                sc.get_cases_monthly_data_for_graphs()
                sc.create_support_cases_charts()
    
        Zip = Zipper(input_args)
        temp_zipfile = Zip.zipfolder()
        logging.info("Generated temporary zip file: " + temp_zipfile)

        now = datetime.now()
        if input_args.customer_domain:
            filename = input_args.tempdirzip + '/' + input_args.customer_domain + '_' + now.strftime('%Y-%m-%d')
        elif input_args.payers_id:
            payer_list_string = "-".join(input_args.payers_id)
            filename = input_args.tempdirzip + '/' + payer_list_string + '_' + now.strftime('%Y-%m-%d')
        else:
            first_account_of_the_list = input_args.account_id[0]
            if len(input_args.account_id) > 1:
                filename = input_args.tempdirzip + '/' + first_account_of_the_list + '_and_others_' + now.strftime('%Y-%m-%d')
            else: filename = input_args.tempdirzip + '/' + first_account_of_the_list + '_' + now.strftime('%Y-%m-%d')

        if input_args.trusted_advisor:
            filename = filename + '_TA'
        if input_args.support_cases:
            filename = filename + '_SC'
        filename = filename + '.zip'

        copyfile(temp_zipfile, filename)

        if not input_args.generateaccountslistonly:
            run_folder = input_args.s3_key_path + now.strftime('%Y-%m-%d')
            zip_file_on_s3 = s3.upload_file_s3(filename, run_folder)
            if zip_file_on_s3 == False:
                logging.error('Failed to upload the Zip file to S3!!!')
            else: logging.info('Zip File uploaded on S3. Location: ' + zip_file_on_s3)

        if input_args.no_update_trends:
            logging.info('No Update Trends specified, the history json file on S3 has not be updated with this run!')
        elif input_args.trusted_advisor:
            run_folder = input_args.s3_key_path
            values_trends_file_on_s3 = s3.upload_file_s3(values_trends_filename, run_folder)
            if values_trends_file_on_s3 == False:
                logging.error('Failed to upload the values_trends file to S3!!!')
            else: logging.info('values_trends File uploaded to S3. Location: ' + values_trends_file_on_s3)

        if input_args.output_file is not None:
            copyfile(temp_zipfile, input_args.output_file)
            logger.info('File {} saved locally.'.format(input_args.output_file))

        """
        # Send mail report, ready to be implemented in case of a host running in batch for multiple customers.
        if input_args.send_mail:
            mail = Mailsend(input_args.email_address)
            mail.build_header()
            mail.build_content()
            mail.attach_file(temp_zipfile)
            mail.send_mail()
        """

        shutil.rmtree(input_args.output_dir)
        shutil.rmtree(input_args.tempdirzip)

        logger.info('Tatool Script Execution Time: ' + str((datetime.now() - startTime)))

if __name__ == "__main__":
    input_args = tatool.cmdline_parser()
    if (input_args):
         tatool.run(input_args)
    else:
        print(input_args)
