import operator
import logging

logger = logging.getLogger(__name__)

class excel_graphs_data:
    def __init__(self, input_args):
        self.input_args = input_args

    def create_graphs_data_dict(self):
        data_files_dict = {}
        graphs_data_dict = {}
        data_files_dict['unfiltered'] = self.input_args.unfiltered_folder + 'full_report_with_resource-ids.csv'
        data_files_dict['isSuppressed'] = self.input_args.isSuppressed_folder + 'NOT_Suppressed_with_resource-ids.csv'
        if self.input_args.filter_file_ta is not None:
            data_files_dict['filtered'] = self.input_args.filtered_folder + 'filtered_report_with_resource-ids.csv'

        for run_type, csv_filename in data_files_dict.items():
            file_in_list = []
            with open(csv_filename, 'r') as f:
                next(f)
                for line in f:
                    file_in_list.append(line)

            # Organize single data
            aggregated_global_count_dict = self.get_aggregated_global_count_dict(file_in_list)
            aggregated_global_category_count_dict = self.get_aggregated_global_category_count_dict(file_in_list)
            aggregated_global_check_name_count_dict = self.get_aggregated_global_check_name_count_dict(file_in_list)
            account_no_details_dict = self.get_account_no_details_dict(file_in_list)
            account_details_dict = self.get_account_details_dict(file_in_list)
            first_five_accounts_by_error_tup_list = self.generate_first_five_accounts_for_error_tup_list(account_details_dict)
            first_five_accounts_by_warning_tup_list = self.generate_first_five_accounts_for_warning_tup_list(
                account_details_dict)
            specific_detail_dict = self.generate_account_detail(account_details_dict)
            mfa_on_root_account_dict = self.get_mfa_on_root_account(file_in_list)
            no_backend_ELB_dict = self.get_no_backend_ELB(file_in_list)
            ELB_sg_problems_dict = self.get_ELB_sg_problems(file_in_list)
            IAM_access_key_rotation_dict = self.get_IAM_access_key_rotation(file_in_list)
            IAM_password_policy_dict = self.IAM_password_policy(file_in_list)
            IAM_password_policy_detail_dict = self.IAM_password_policy_detail(file_in_list)
            RDS_idle_db_connection_dict = self.RDS_idle_db_connection(file_in_list)
            RDS_no_backups_dict = self.RDS_no_backups(file_in_list)
            RDS_sg_risk_dict = self.RDS_sg_risk(file_in_list)
            S3_bucket_logging_dict = self.S3_bucket_logging(file_in_list)
            S3_bucket_permissions_dict = self.S3_bucket_permissions(file_in_list)
            S3_bucket_versioning_dict = self.S3_bucket_versioning(file_in_list)
            service_limits_dict = self.get_service_limits(file_in_list)

            # Generate dictionary
            graphs_data_dict[run_type] = {}
            graphs_data_dict[run_type]['aggregated_global_count'] = aggregated_global_count_dict
            graphs_data_dict[run_type]['aggregated_global_category_count'] = aggregated_global_category_count_dict
            graphs_data_dict[run_type]['aggregated_global_check_name_count'] = aggregated_global_check_name_count_dict
            graphs_data_dict[run_type]['account_no_details'] = account_no_details_dict
            graphs_data_dict[run_type]['account_details'] = account_details_dict
            graphs_data_dict[run_type]['first_five_accounts_by_error_tup_list'] = first_five_accounts_by_error_tup_list
            graphs_data_dict[run_type]['first_five_accounts_by_warning_tup_list'] = first_five_accounts_by_warning_tup_list
            graphs_data_dict[run_type]['account_specific_detail'] = specific_detail_dict
            graphs_data_dict[run_type]['mfa_on_root_account'] = mfa_on_root_account_dict
            graphs_data_dict[run_type]['no_backend_ELB'] = no_backend_ELB_dict
            graphs_data_dict[run_type]['ELB_sg_problems'] = ELB_sg_problems_dict
            graphs_data_dict[run_type]['IAM_access_key_rotation'] = IAM_access_key_rotation_dict
            graphs_data_dict[run_type]['IAM_password_policy'] = IAM_password_policy_dict
            graphs_data_dict[run_type]['IAM_password_policy_detail'] = IAM_password_policy_detail_dict
            graphs_data_dict[run_type]['RDS_idle_db_connection'] = RDS_idle_db_connection_dict
            graphs_data_dict[run_type]['RDS_no_backups'] = RDS_no_backups_dict
            graphs_data_dict[run_type]['RDS_sg_risk'] = RDS_sg_risk_dict
            graphs_data_dict[run_type]['S3_bucket_logging'] = S3_bucket_logging_dict
            graphs_data_dict[run_type]['S3_bucket_permissions'] = S3_bucket_permissions_dict
            graphs_data_dict[run_type]['S3_bucket_versioning'] = S3_bucket_versioning_dict
            graphs_data_dict[run_type]['ServiceLimits'] = service_limits_dict

        return graphs_data_dict

    def get_aggregated_global_count_dict(self, file_in_list):
        aggregated_global_count_dict = {}
        for line in file_in_list:
            status_check = line.split(",")[4]
            aggregated_global_count_dict[status_check] = aggregated_global_count_dict.get(status_check, 0) + 1
        return aggregated_global_count_dict

    def get_aggregated_global_category_count_dict(self, file_in_list):
        aggregated_global_category_count_dict = {}
        for line in file_in_list:
            category = line.split(",")[3]
            status_check = line.split(",")[4]
            if aggregated_global_category_count_dict.get(category) == None:
                aggregated_global_category_count_dict[category] = {}
            if aggregated_global_category_count_dict.get(category, {}).get(status_check) == None:
                aggregated_global_category_count_dict[category][status_check] = 1
            else:
                a = aggregated_global_category_count_dict.get(category, {}).get(status_check)
                aggregated_global_category_count_dict[category][status_check] = a + 1
        return aggregated_global_category_count_dict

    def get_aggregated_global_check_name_count_dict(self, file_in_list):
        aggregated_global_check_name_count_dict = {}
        for line in file_in_list:
            status_check = line.split(",")[4]
            check_name = line.split(",")[5]
            if aggregated_global_check_name_count_dict.get(check_name) == None:
                aggregated_global_check_name_count_dict[check_name] = {}
            if aggregated_global_check_name_count_dict.get(check_name, {}).get(status_check) == None:
                aggregated_global_check_name_count_dict[check_name][status_check] = 1
            else:
                a = aggregated_global_check_name_count_dict.get(check_name, {}).get(status_check)
                aggregated_global_check_name_count_dict[check_name][status_check] = a + 1
        return aggregated_global_check_name_count_dict

    def get_account_no_details_dict(self, file_in_list):
        account_no_details_dict ={}
        for line in file_in_list:
            account_display_name = line.split(",")[2]
            status_check = line.split(",")[4]
            if account_no_details_dict.get(account_display_name) == None:
                account_no_details_dict[account_display_name] = {}
            if account_no_details_dict.get(account_display_name, {}).get(status_check) == None:
                account_no_details_dict[account_display_name][status_check] = 1
            else:
                a = account_no_details_dict.get(account_display_name, {}).get(status_check)
                account_no_details_dict[account_display_name][status_check] = a + 1
        return account_no_details_dict

    def get_account_details_dict(self, file_in_list):
        account_details_dict = {}
        for line in file_in_list:
            account_display_name = line.split(",")[2]
            status_check = line.split(",")[4]
            check_name = line.split(",")[5]
            if account_details_dict.get(account_display_name) == None:
                account_details_dict[account_display_name] = {}
            if account_details_dict.get(account_display_name, {}).get(check_name) == None:
                account_details_dict[account_display_name][check_name] = {}
            if account_details_dict.get(account_display_name, {}).get(check_name, {}).get(status_check) == None:
                account_details_dict[account_display_name][check_name][status_check] = 1
            else:
                a = account_details_dict.get(account_display_name, {}).get(check_name, {}).get(status_check)
                account_details_dict[account_display_name][check_name][status_check] = a + 1
        return account_details_dict

    def get_mfa_on_root_account(self, file_in_list):
        mfa_on_root_account_dict = {}
        for line in file_in_list:
            status_check = line.split(",")[4]
            check_name = line.split(",")[5]
            if status_check == 'error' and check_name == 'MFA on Root Account':
                mfa_on_root_account_dict[status_check] = mfa_on_root_account_dict.get(status_check, 0) + 1
        return mfa_on_root_account_dict

    def get_no_backend_ELB(self, file_in_list):
        no_backend_ELB_dict = {}
        for line in file_in_list:
            status_check = line.split(",")[4]
            check_name = line.split(",")[5]
            if check_name == 'Idle Load Balancers':
                try:
                    reason = line.split(",")[11]
                    if reason == '\"No active back-end instances\"':
                        no_backend_ELB_dict[status_check] = no_backend_ELB_dict.get(status_check, 0) + 1
                except:
                    continue
        return no_backend_ELB_dict

    def get_ELB_sg_problems(self, file_in_list):
        ELB_sg_problems_dict = {}
        for line in file_in_list:
            check_name = line.split(",")[5]
            if check_name == 'ELB Security Groups':
                try:
                    color = line.split(',')[11].strip('"').lstrip('"')
                    ELB_sg_problems_dict[color] = ELB_sg_problems_dict.get(color, 0) + 1
                except:
                    continue
        return ELB_sg_problems_dict

    def get_IAM_access_key_rotation(self, file_in_list):
        IAM_access_key_rotation_dict = {}
        for line in file_in_list:
            check_name = line.split(",")[5]
            if check_name == 'IAM Access Key Rotation':
                try:
                    color = line.split(',')[9].strip('"').lstrip('"')
                    IAM_access_key_rotation_dict[color] = IAM_access_key_rotation_dict.get(color, 0) + 1
                except:
                    continue
        return IAM_access_key_rotation_dict

    def IAM_password_policy(self, file_in_list):
        IAM_password_policy_dict = {}
        for line in file_in_list:
            check_name = line.split(",")[5]
            if check_name == 'IAM Password Policy':
                try:
                    color = line.split(',')[14].strip('"').lstrip('"')
                    IAM_password_policy_dict[color] = IAM_password_policy_dict.get(color, 0) + 1
                except:
                    continue
        return IAM_password_policy_dict

    def IAM_password_policy_detail(self, file_in_list):
        IAM_password_policy_detail_dict = {}
        for line in file_in_list:
            check_name = line.split(",")[5]
            if check_name == 'IAM Password Policy':
                try:
                    passwordPolicyEnabled = line.split(',')[9].strip('"').lstrip('"')
                    requireUppercase = line.split(',')[10].strip('"').lstrip('"')
                    requireLowercase = line.split(',')[11].strip('"').lstrip('"')
                    requireNumbers = line.split(',')[12].strip('"').lstrip('"')
                    requireSymbols = line.split(',')[13].strip('"').lstrip('"')
                    if passwordPolicyEnabled == 'Disabled':
                        IAM_password_policy_detail_dict['passwordPolicyEnabled'] = IAM_password_policy_detail_dict.get('passwordPolicyEnabled', 0) + 1
                    if requireUppercase == 'Disabled':
                        IAM_password_policy_detail_dict['requireUppercase'] = IAM_password_policy_detail_dict.get('requireUppercase', 0) + 1
                    if requireLowercase == 'Disabled':
                        IAM_password_policy_detail_dict['requireLowercase'] = IAM_password_policy_detail_dict.get('requireLowercase', 0) + 1
                    if requireNumbers == 'Disabled':
                        IAM_password_policy_detail_dict['requireNumbers'] = IAM_password_policy_detail_dict.get('requireNumbers', 0) + 1
                    if requireSymbols == 'Disabled':
                        IAM_password_policy_detail_dict['requireSymbols'] = IAM_password_policy_detail_dict.get('requireSymbols', 0) + 1
                except:
                    continue
        return IAM_password_policy_detail_dict

    def RDS_idle_db_connection(self, file_in_list):
        RDS_idle_db_connection_dict = {}
        for line in file_in_list:
            check_name = line.split(",")[5]
            if check_name == 'Amazon RDS Idle DB Instances':
                try:
                    days = line.split(',')[14].strip('"').lstrip('"')
                    if days == '14+' or days == '7' or days == '8' or days == '9' or days == '10' or days == '11' or days == '12' or days == '13' or days == '14':
                        RDS_idle_db_connection_dict[days] = RDS_idle_db_connection_dict.get(days, 0) + 1
                except:
                    continue
        return RDS_idle_db_connection_dict

    def RDS_no_backups(self, file_in_list):
        RDS_no_backups_dict = {}
        for line in file_in_list:
            status = line.split(",")[4]
            check_name = line.split(",")[5]
            if check_name == 'Amazon RDS Backups':
                RDS_no_backups_dict[status] = RDS_no_backups_dict.get(status, 0) + 1
        return RDS_no_backups_dict

    def RDS_sg_risk(self, file_in_list):
        RDS_sg_risk_dict = {}
        for line in file_in_list:
            check_name = line.split(",")[5]
            if check_name == 'Amazon RDS Security Group Access Risk':
                try:
                    color = line.split(',')[12].strip('"').lstrip('"')
                    RDS_sg_risk_dict[color] = RDS_sg_risk_dict.get(color, 0) + 1
                except:
                    continue
        return RDS_sg_risk_dict

    def S3_bucket_logging(self, file_in_list):
        S3_bucket_logging_dict = {}
        for line in file_in_list:
            check_name = line.split(",")[5]
            if check_name == 'Amazon S3 Bucket Logging':
                try:
                    color = line.split(',')[15].strip('"').lstrip('"')
                    S3_bucket_logging_dict[color] = S3_bucket_logging_dict.get(color, 0) + 1
                except:
                    continue
        return S3_bucket_logging_dict

    def S3_bucket_permissions(self, file_in_list):
        S3_bucket_permissions_dict = {}
        for line in file_in_list:
            check_name = line.split(",")[5]
            if check_name == 'Amazon S3 Bucket Permissions':
                try:
                    hasGlobalListAccess = line.split(',')[12].strip('"').lstrip('"')
                    hasGlobalUploadDeleteAccess = line.split(',')[13].strip('"').lstrip('"')
                    color = line.split(',')[14].strip('"').lstrip('"')
                    vulnerable_policy = line.split(',')[15].strip('"').lstrip('"')
                    S3_bucket_permissions_dict[color] = S3_bucket_permissions_dict.get(color, 0) + 1
                    if hasGlobalListAccess == 'Yes':
                        S3_bucket_permissions_dict['hasGlobalListAccess_yes'] = S3_bucket_permissions_dict.get('hasGlobalListAccess_yes', 0) + 1
                    if hasGlobalUploadDeleteAccess == 'Yes':
                        S3_bucket_permissions_dict['hasGlobalUploadDeleteAccess_yes'] = S3_bucket_permissions_dict.get('hasGlobalUploadDeleteAccess_yes', 0) + 1
                    if vulnerable_policy == 'Yes':
                        S3_bucket_permissions_dict['vulnerable_policy_yes'] = S3_bucket_permissions_dict.get('vulnerable_policy_yes', 0) + 1
                except:
                    continue
        return S3_bucket_permissions_dict

    def S3_bucket_versioning(self, file_in_list):
        S3_bucket_versioning_dict = {}
        for line in file_in_list:
            check_name = line.split(",")[5]
            if check_name == 'Amazon S3 Bucket Versioning':
                try:
                    color = line.split(',')[13].strip('"\n').lstrip('"')
                    S3_bucket_versioning_dict[color] = S3_bucket_versioning_dict.get(color, 0) + 1
                except:
                    continue
        return S3_bucket_versioning_dict

    def get_service_limits(self, file_in_list):
        service_limits_dict = {}
        for line in file_in_list:
            check_name = line.split(",")[5]
            if check_name == 'Service Limits':
                try:
                    color = line.split(',')[14].strip('"\n').lstrip('"')
                    service_limits_dict[color] = service_limits_dict.get(color, 0) + 1
                except:
                    continue
        return service_limits_dict

    def generate_first_five_accounts_for_error_tup_list(self, account_details_dict):
        account_vs_error_dict = {}
        for account, check_name_status in account_details_dict.items():
            for check_name, status in check_name_status.items():
                if status.get('error') is not None:
                    account_vs_error_dict[account] = account_vs_error_dict.get(account, 0) + status.get('error')

        first_five_accounts_by_error_dict = sorted(account_vs_error_dict.items(), key = operator.itemgetter(1), reverse=True)[:5]
        return first_five_accounts_by_error_dict

    def generate_first_five_accounts_for_warning_tup_list(self, account_details_dict):
        account_vs_warning_dict = {}
        for account, check_name_status in account_details_dict.items():
            for check_name, status in check_name_status.items():
                if status.get('warning') is not None:
                    account_vs_warning_dict[account] = account_vs_warning_dict.get(account, 0) + status.get('warning')

        first_five_accounts_by_warning_dict = sorted(account_vs_warning_dict.items(), key = operator.itemgetter(1), reverse=True)[:5]
        return first_five_accounts_by_warning_dict

    def generate_account_detail(self, account_details_dict):
        account_dict = {}
        for account, check in account_details_dict.items():
            specific_detail_account_dict = {}
            specific_detail_account_dict['errors'] = {}
            specific_detail_account_dict['warnings'] = {}
            for status, number in check.items():
                if number.get('error') is not None:
                    specific_detail_account_dict['errors'][status] = specific_detail_account_dict.get('errors').get(status, 0) + number.get('error')
                if number.get('warning') is not None:
                    specific_detail_account_dict['warnings'][status] = specific_detail_account_dict.get('warnings').get(status, 0) + number.get('warning')
            account_dict[account] = specific_detail_account_dict
        return account_dict