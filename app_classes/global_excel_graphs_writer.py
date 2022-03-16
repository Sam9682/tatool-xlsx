import xlsxwriter
import logging

logger = logging.getLogger(__name__)

class global_excel_graphs_writer:
    def __init__(self, input_args):
        self.input_args = input_args

    def create_global_charts(self, graphs_data_dict):

        for run, values in graphs_data_dict.items():

            if run == 'filtered' and self.input_args.filtered_folder is not None:
                workdir = self.input_args.filtered_folder
            elif run == 'isSuppressed':
                workdir = self.input_args.isSuppressed_folder
            else: workdir = self.input_args.unfiltered_folder

            logging.info("Generating global charts in the directory " + workdir)

            aggregated_global_count_dict = graphs_data_dict.get(run).get('aggregated_global_count')
            aggregated_global_count_dict_keys_list = []
            aggregated_global_count_dict_values_list = []

            aggregated_global_count_dict_keys_list.append("warning")
            aggregated_global_count_dict_keys_list.append("ok")
            aggregated_global_count_dict_keys_list.append("error")
            aggregated_global_count_dict_values_list.append(aggregated_global_count_dict['warning'] if (aggregated_global_count_dict.get('warning') is not None) else 0)
            aggregated_global_count_dict_values_list.append(aggregated_global_count_dict['ok'] if (aggregated_global_count_dict.get('ok') is not None) else 0)
            aggregated_global_count_dict_values_list.append(aggregated_global_count_dict['error'] if (aggregated_global_count_dict.get('error') is not None) else 0)

            workbook = xlsxwriter.Workbook(workdir + run + '_TrustedAdvisorGlobalGraphs.xlsx')
            worksheet = workbook.add_worksheet()
            bold = workbook.add_format({'bold': 1})

            headings = ['Status', 'Number of checks']

            data = []
            data.append(aggregated_global_count_dict_keys_list)
            data.append(aggregated_global_count_dict_values_list)

            worksheet.write_row('A1', headings, bold)
            worksheet.write_column('A2', data[0])
            worksheet.write_column('B2', data[1])

            chart1 = workbook.add_chart({'type': 'column'})

            chart1.add_series({
                'name': '=Sheet1!$B$1',
                'categories': '=Sheet1!$A$2:$A$4',
                'values': '=Sheet1!$B$2:$B$4',
            })

            chart1.set_title({'name': 'Global number of checks and Status'})
            chart1.set_x_axis({'name': 'Result'})
            chart1.set_y_axis({'name': 'Number of checks'})

            chart1.set_style(8)

            worksheet.insert_chart('D2', chart1, {'x_offset': 25, 'y_offset': 10})

            category_list = []

            category_list.append('performance')
            category_list.append('security')
            category_list.append('fault_tolerance')
            category_list.append('cost_optimizing')

            aggregated_global_category_count_dict = graphs_data_dict.get(run).get('aggregated_global_category_count')

            performance_dict = (aggregated_global_category_count_dict['performance'] if (
            aggregated_global_category_count_dict.get('performance') is not None) else {})
            security_dict = (aggregated_global_category_count_dict['security'] if (
            aggregated_global_category_count_dict.get('security') is not None) else {})
            fault_tolerant_dict = (aggregated_global_category_count_dict['fault_tolerance'] if (
            aggregated_global_category_count_dict.get('fault_tolerance') is not None) else {})
            cost_optimization_dict = (aggregated_global_category_count_dict['cost_optimizing'] if (
            aggregated_global_category_count_dict.get('cost_optimizing') is not None) else {})

            warnings_list = []
            ok_list = []
            errors_list = []

            warnings_list.append(performance_dict['warning'] if (performance_dict.get('warning') is not None) else 0)
            warnings_list.append(security_dict['warning'] if (security_dict.get('warning') is not None) else 0)
            warnings_list.append(
                fault_tolerant_dict['warning'] if (fault_tolerant_dict.get('warning') is not None) else 0)
            warnings_list.append(
                cost_optimization_dict['warning'] if (cost_optimization_dict.get('warning') is not None) else 0)

            errors_list.append(performance_dict['error'] if (performance_dict.get('error') is not None) else 0)
            errors_list.append(security_dict['error'] if (security_dict.get('error') is not None) else 0)
            errors_list.append(fault_tolerant_dict['error'] if (fault_tolerant_dict.get('error') is not None) else 0)
            errors_list.append(
                cost_optimization_dict['error'] if (cost_optimization_dict.get('error') is not None) else 0)

            ok_list.append(performance_dict['ok'] if (performance_dict.get('ok') is not None) else 0)
            ok_list.append(security_dict['ok'] if (security_dict.get('ok') is not None) else 0)
            ok_list.append(fault_tolerant_dict['ok'] if (fault_tolerant_dict.get('ok') is not None) else 0)
            ok_list.append(cost_optimization_dict['ok'] if (cost_optimization_dict.get('ok') is not None) else 0)

            worksheet = workbook.add_worksheet()
            bold = workbook.add_format({'bold': 1})

            # Add the worksheet data that the charts will refer to.
            headings = ['Category', 'Warnings', 'Errors', 'OK']
            data2 = []
            data2.append(category_list)
            data2.append(warnings_list)
            data2.append(errors_list)
            data2.append(ok_list)

            worksheet.write_row('A1', headings, bold)
            worksheet.write_column('A2', data2[0])
            worksheet.write_column('B2', data2[1])
            worksheet.write_column('C2', data2[2])
            worksheet.write_column('D2', data2[3])

            ###### New Sheet!
            chart2 = workbook.add_chart({'type': 'column'})

            # Configure the first series.
            chart2.add_series({
                'name': '=Sheet2!$B$1',
                'categories': '=Sheet2!$A$2:$A$5',
                'values': '=Sheet2!$B$2:$B$5',
            })

            # Configure a second series. Note use of alternative syntax to define ranges.
            chart2.add_series({
                'name': ['Sheet2', 0, 2],
                'categories': ['Sheet2', 1, 0, 4, 0],
                'values': ['Sheet2', 1, 2, 4, 2],
            })

            # Configure a second series. Note use of alternative syntax to define ranges.
            chart2.add_series({
                'name': ['Sheet2', 0, 3],
                'categories': ['Sheet2', 1, 0, 4, 0],
                'values': ['Sheet2', 1, 3, 4, 3],
            })

            # Add a chart title and some axis labels.
            chart2.set_title({'name': 'Number of checks by category'})
            chart2.set_x_axis({'name': 'Check categories'})
            chart2.set_y_axis({'name': 'Number of checks'})

            # Set an Excel chart style.
            chart2.set_style(2)

            # Insert the chart into the worksheet (with an offset).
            worksheet.insert_chart('E2', chart2, {'x_offset': 25, 'y_offset': 10})

            first_five_accounts_by_error_tup_list = graphs_data_dict.get(run).get('first_five_accounts_by_error_tup_list')

            first_five_accounts_by_error_dict_keys_list = []
            first_five_accounts_by_error_dict_values_list = []

            for account in first_five_accounts_by_error_tup_list:
                first_five_accounts_by_error_dict_keys_list.append(account[0])
                first_five_accounts_by_error_dict_values_list.append(account[1])

            worksheet = workbook.add_worksheet()
            bold = workbook.add_format({'bold': 1})

            headings = ['Account', 'Errors']

            data3 = []
            data3.append(first_five_accounts_by_error_dict_keys_list)
            data3.append(first_five_accounts_by_error_dict_values_list)

            worksheet.write_row('A1', headings, bold)
            worksheet.write_column('A2', data3[0])
            worksheet.write_column('B2', data3[1])

            chart3 = workbook.add_chart({'type': 'column'})

            chart3.add_series({
                'name': '=Sheet3!$B$1',
                'categories': '=Sheet3!$A$2:$A$6',
                'values': '=Sheet3!$B$2:$B$6',
            })

            chart3.set_title({'name': 'Top 5 accounts per TA errors'})
            chart3.set_x_axis({'name': 'Account-Id'})
            chart3.set_y_axis({'name': 'Number of errors'})

            chart3.set_style(8)

            worksheet.insert_chart('D2', chart3, {'x_offset': 25, 'y_offset': 10})

            first_five_accounts_by_warning_tup_list = graphs_data_dict.get(run).get(
                'first_five_accounts_by_warning_tup_list')

            first_five_accounts_by_warning_dict_keys_list = []
            first_five_accounts_by_warning_dict_values_list = []

            for account in first_five_accounts_by_warning_tup_list:
                first_five_accounts_by_warning_dict_keys_list.append(account[0])
                first_five_accounts_by_warning_dict_values_list.append(account[1])

            worksheet = workbook.add_worksheet()
            bold = workbook.add_format({'bold': 1})

            headings = ['Account', 'Warnings']

            data4 = []
            data4.append(first_five_accounts_by_warning_dict_keys_list)
            data4.append(first_five_accounts_by_warning_dict_values_list)

            worksheet.write_row('A1', headings, bold)
            worksheet.write_column('A2', data4[0])
            worksheet.write_column('B2', data4[1])

            chart4 = workbook.add_chart({'type': 'column'})

            chart4.add_series({
                'name': '=Sheet4!$B$1',
                'categories': '=Sheet4!$A$2:$A$6',
                'values': '=Sheet4!$B$2:$B$6',
            })

            chart4.set_title({'name': 'Top 5 accounts per TA warnings'})
            chart4.set_x_axis({'name': 'Account-Id'})
            chart4.set_y_axis({'name': 'Number of warnings'})

            chart4.set_style(8)

            worksheet.insert_chart('D2', chart4, {'x_offset': 25, 'y_offset': 10})


            # Sheet 5 IAM Password Policy

            IAM_password_policy_detail_dict = graphs_data_dict.get(run).get('IAM_password_policy_detail')

            category_list = []
            category_list.append('passwordPolicyEnabled')
            category_list.append('requireUppercase')
            category_list.append('requireLowercase')
            category_list.append('requireNumbers')
            category_list.append('requireSymbols')

            values_list = []
            values_list.append(IAM_password_policy_detail_dict['passwordPolicyEnabled'] if (
            IAM_password_policy_detail_dict.get('passwordPolicyEnabled') is not None) else 0)
            values_list.append(IAM_password_policy_detail_dict['requireUppercase'] if (
            IAM_password_policy_detail_dict.get('requireUppercase') is not None) else 0)
            values_list.append(IAM_password_policy_detail_dict['requireLowercase'] if (
            IAM_password_policy_detail_dict.get('requireLowercase') is not None) else 0)
            values_list.append(IAM_password_policy_detail_dict['requireNumbers'] if (
            IAM_password_policy_detail_dict.get('requireNumbers') is not None) else 0)
            values_list.append(IAM_password_policy_detail_dict['requireSymbols'] if (
            IAM_password_policy_detail_dict.get('requireSymbols') is not None) else 0)

            worksheet = workbook.add_worksheet()
            bold = workbook.add_format({'bold': 1})

            # Add the worksheet data that the charts will refer to.
            headings = ['Category', 'Number']
            data5 = []
            data5.append(category_list)
            data5.append(values_list)

            worksheet.write_row('A1', headings, bold)
            worksheet.write_column('A2', data5[0])
            worksheet.write_column('B2', data5[1])

            chart5 = workbook.add_chart({'type': 'column'})

            # Configure the first series.
            chart5.add_series({
                'name': '=Sheet5!$B$1',
                'categories': '=Sheet5!$A$2:$A$6',
                'values': '=Sheet5!$B$2:$B$6',
            })

            # Add a chart title and some axis labels.
            chart5.set_title({'name': 'IAM Password Policy Detailed Status'})
            chart5.set_x_axis({'name': 'Check name'})
            chart5.set_y_axis({'name': 'Number of checks failed'})

            # Set an Excel chart style.
            chart5.set_style(2)

            # Insert the chart into the worksheet (with an offset).
            worksheet.insert_chart('E2', chart5, {'x_offset': 25, 'y_offset': 10})

            # Sheet 6 RDS idle db connection

            RDS_idle_db_connection_dict = graphs_data_dict.get(run).get('RDS_idle_db_connection')

            days_list = []
            days_list.append('7')
            days_list.append('8')
            days_list.append('9')
            days_list.append('10')
            days_list.append('11')
            days_list.append('12')
            days_list.append('13')
            days_list.append('14')
            days_list.append('14+')

            values_list = []
            values_list.append(
                RDS_idle_db_connection_dict['7'] if (RDS_idle_db_connection_dict.get('7') is not None) else 0)
            values_list.append(
                RDS_idle_db_connection_dict['8'] if (RDS_idle_db_connection_dict.get('8') is not None) else 0)
            values_list.append(
                RDS_idle_db_connection_dict['9'] if (RDS_idle_db_connection_dict.get('9') is not None) else 0)
            values_list.append(
                RDS_idle_db_connection_dict['10'] if (RDS_idle_db_connection_dict.get('10') is not None) else 0)
            values_list.append(
                RDS_idle_db_connection_dict['11'] if (RDS_idle_db_connection_dict.get('11') is not None) else 0)
            values_list.append(
                RDS_idle_db_connection_dict['12'] if (RDS_idle_db_connection_dict.get('12') is not None) else 0)
            values_list.append(
                RDS_idle_db_connection_dict['13'] if (RDS_idle_db_connection_dict.get('13') is not None) else 0)
            values_list.append(
                RDS_idle_db_connection_dict['14'] if (RDS_idle_db_connection_dict.get('14') is not None) else 0)
            values_list.append(
                RDS_idle_db_connection_dict['14+'] if (RDS_idle_db_connection_dict.get('14+') is not None) else 0)

            worksheet = workbook.add_worksheet()
            bold = workbook.add_format({'bold': 1})

            # Add the worksheet data that the charts will refer to.
            headings = ['Days', 'Number of Instances']
            data6 = []
            data6.append(days_list)
            data6.append(values_list)

            worksheet.write_row('A1', headings, bold)
            worksheet.write_column('A2', data6[0])
            worksheet.write_column('B2', data6[1])

            chart6 = workbook.add_chart({'type': 'column'})

            # Configure the first series.
            chart6.add_series({
                'name': '=Sheet6!$B$1',
                'categories': '=Sheet6!$A$2:$A$10',
                'values': '=Sheet6!$B$2:$B$10',
            })

            # Add a chart title and some axis labels.
            chart6.set_title({'name': 'Amazon RDS Idle DB Instances No Connections - Days'})
            chart6.set_x_axis({'name': 'Days'})
            chart6.set_y_axis({'name': 'Number of RDS Instances'})

            # Set an Excel chart style.
            chart6.set_style(2)

            # Insert the chart into the worksheet (with an offset).
            worksheet.insert_chart('E2', chart6, {'x_offset': 25, 'y_offset': 10})

            # Sheet 7 S3 bucket logging

            S3_bucket_logging_dict = graphs_data_dict.get(run).get('S3_bucket_logging')

            status_list = []
            status_list.append('ok')
            status_list.append('warning')
            status_list.append('error')

            values_list = []
            values_list.append(
                S3_bucket_logging_dict['Green'] if (S3_bucket_logging_dict.get('Green') is not None) else 0)
            values_list.append(
                S3_bucket_logging_dict['Yellow'] if (S3_bucket_logging_dict.get('Yellow') is not None) else 0)
            values_list.append(
                S3_bucket_logging_dict['Red'] if (S3_bucket_logging_dict.get('Red') is not None) else 0)

            worksheet = workbook.add_worksheet()
            bold = workbook.add_format({'bold': 1})

            # Add the worksheet data that the charts will refer to.
            headings = ['Status', 'Number of S3 Buckets']
            data7 = []
            data7.append(status_list)
            data7.append(values_list)

            worksheet.write_row('A1', headings, bold)
            worksheet.write_column('A2', data7[0])
            worksheet.write_column('B2', data7[1])

            chart7 = workbook.add_chart({'type': 'column'})

            # Configure the first series.
            chart7.add_series({
                'name': '=Sheet7!$B$1',
                'categories': '=Sheet7!$A$2:$A$5',
                'values': '=Sheet7!$B$2:$B$5',
            })

            # Add a chart title and some axis labels.
            chart7.set_title({'name': 'Amazon S3 Bucket Logging'})
            chart7.set_x_axis({'name': 'Status'})
            chart7.set_y_axis({'name': 'Number of S3 Buckets'})

            # Set an Excel chart style.
            chart7.set_style(2)

            # Insert the chart into the worksheet (with an offset).
            worksheet.insert_chart('E2', chart7, {'x_offset': 25, 'y_offset': 10})

            # Sheet 8 S3 Bucket permissions

            S3_bucket_permissions_dict = graphs_data_dict.get(run).get('S3_bucket_permissions')

            category_list = []
            category_list.append('has Global List Access')
            category_list.append('has Global Upload Delete Access')
            category_list.append('vulnerable bucket policy')

            values_list = []
            values_list.append(
                S3_bucket_permissions_dict['hasGlobalListAccess_yes'] if (
                S3_bucket_permissions_dict.get('hasGlobalListAccess_yes') is not None) else 0)
            values_list.append(
                S3_bucket_permissions_dict['hasGlobalUploadDeleteAccess_yes'] if (
                S3_bucket_permissions_dict.get('hasGlobalUploadDeleteAccess_yes') is not None) else 0)
            values_list.append(
                S3_bucket_permissions_dict['vulnerable_policy_yes'] if (
                S3_bucket_permissions_dict.get('vulnerable_policy_yes') is not None) else 0)

            worksheet = workbook.add_worksheet()
            bold = workbook.add_format({'bold': 1})

            # Add the worksheet data that the charts will refer to.
            headings = ['Issue', 'Number of Buckets']
            data8 = []
            data8.append(category_list)
            data8.append(values_list)

            worksheet.write_row('A1', headings, bold)
            worksheet.write_column('A2', data8[0])
            worksheet.write_column('B2', data8[1])

            chart8 = workbook.add_chart({'type': 'column'})

            # Configure the first series.
            chart8.add_series({
                'name': '=Sheet8!$B$1',
                'categories': '=Sheet8!$A$2:$A$4',
                'values': '=Sheet8!$B$2:$B$4',
            })

            # Add a chart title and some axis labels.
            chart8.set_title({'name': 'Amazon S3 Bucket permissions'})
            chart8.set_x_axis({'name': 'Issue'})
            chart8.set_y_axis({'name': 'Number of S3 Buckets'})

            # Set an Excel chart style.
            chart8.set_style(2)

            # Insert the chart into the worksheet (with an offset).
            worksheet.insert_chart('E2', chart8, {'x_offset': 25, 'y_offset': 10})

            # Sheet 9 Service Limits

            service_limits_dict = graphs_data_dict.get(run).get('ServiceLimits')

            status_list = []
            status_list.append('ok')
            status_list.append('warning')
            status_list.append('error')

            values_list = []
            values_list.append(
                service_limits_dict['Green'] if (service_limits_dict.get('Green') is not None) else 0)
            values_list.append(
                service_limits_dict['Yellow'] if (service_limits_dict.get('Yellow') is not None) else 0)
            values_list.append(
                service_limits_dict['Red'] if (service_limits_dict.get('Red') is not None) else 0)

            worksheet = workbook.add_worksheet()
            bold = workbook.add_format({'bold': 1})

            # Add the worksheet data that the charts will refer to.
            headings = ['Status', 'Number of Service Limits']
            data9 = []
            data9.append(status_list)
            data9.append(values_list)

            worksheet.write_row('A1', headings, bold)
            worksheet.write_column('A2', data9[0])
            worksheet.write_column('B2', data9[1])

            chart9 = workbook.add_chart({'type': 'column'})

            # Configure the first series.
            chart9.add_series({
                'name': '=Sheet9!$B$1',
                'categories': '=Sheet9!$A$2:$A$5',
                'values': '=Sheet9!$B$2:$B$5',
            })

            # Add a chart title and some axis labels.
            chart9.set_title({'name': 'Service Limits'})
            chart9.set_x_axis({'name': 'Status'})
            chart9.set_y_axis({'name': 'Number of Service Limits'})

            # Set an Excel chart style.
            chart9.set_style(2)

            # Insert the chart into the worksheet (with an offset).
            worksheet.insert_chart('E2', chart9, {'x_offset': 25, 'y_offset': 10})

            workbook.close()