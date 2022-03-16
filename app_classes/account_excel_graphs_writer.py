import os
import operator
import xlsxwriter
import logging

logger = logging.getLogger(__name__)

class Account_Level_Graphs:
    def __init__(self, input_args):
        self.input_args = input_args

    def create_details_chart(self, graphs_data_dict):

        for run, values in graphs_data_dict.items():

            if run == 'filtered':
                workdir = self.input_args.filtered_folder
            elif run == 'isSuppressed':
                workdir = self.input_args.isSuppressed_folder
            else: workdir = self.input_args.unfiltered_folder

            graph_dir = workdir + 'account_detail_graphs/'
            if not os.path.exists(graph_dir):
                os.makedirs(graph_dir)

            account_specific_detail_dict = values['account_specific_detail']

            for account, values in account_specific_detail_dict.items():
                error_detail_dict = values['errors']
                warnings_detail_dict = values['warnings']
                first_five_errors_by_account_dict = sorted(error_detail_dict.items(), key=operator.itemgetter(1), reverse=True)[:5]
                first_five_warnings_by_account_dict = sorted(warnings_detail_dict.items(), key=operator.itemgetter(1), reverse=True)[:5]

                # Top 5 Errors sheet

                data = []
                error = []
                number = []
                for k, v in first_five_errors_by_account_dict:
                    error.append(k)
                    number.append(v)

                data.append(error)
                data.append(number)

                workbook = xlsxwriter.Workbook(graph_dir + account + '_TrustedAdvisorGraphs' + '.xlsx')
                worksheet = workbook.add_worksheet()
                bold = workbook.add_format({'bold': 1})

                headings = ['TA Check', 'Number of Errors']

                worksheet.write_row('A1', headings, bold)
                worksheet.write_column('A2', data[0])
                worksheet.write_column('B2', data[1])

                chart1 = workbook.add_chart({'type': 'column'})

                chart1.add_series({
                    'name': '=Sheet1!$B$1',
                    'categories': '=Sheet1!$A$2:$A$6',
                    'values': '=Sheet1!$B$2:$B$6',
                })

                chart1.set_title({'name': 'Top 5 Trusted Advisor Errors Account ' + account})
                chart1.set_x_axis({'name': 'Check Name'})
                chart1.set_y_axis({'name': 'Number of checks'})

                chart1.set_style(2)

                worksheet.insert_chart('D2', chart1, {'x_offset': 25, 'y_offset': 10})

                # Top 5 Warnings sheet

                data = []
                warning = []
                number = []
                for k, v in first_five_warnings_by_account_dict:
                    warning.append(k)
                    number.append(v)

                data.append(warning)
                data.append(number)

                worksheet = workbook.add_worksheet()
                bold = workbook.add_format({'bold': 1})

                headings = ['TA Check', 'Number of Warnings']

                worksheet.write_row('A1', headings, bold)
                worksheet.write_column('A2', data[0])
                worksheet.write_column('B2', data[1])

                chart2 = workbook.add_chart({'type': 'column'})

                chart2.add_series({
                    'name': '=Sheet2!$B$1',
                    'categories': '=Sheet2!$A$2:$A$6',
                    'values': '=Sheet2!$B$2:$B$6',
                })

                chart2.set_title({'name': 'Top 5 Trusted Advisor Warnings Account ' + account})
                chart2.set_x_axis({'name': 'Check Name'})
                chart2.set_y_axis({'name': 'Number of checks'})

                chart2.set_style(2)

                worksheet.insert_chart('D2', chart2, {'x_offset': 25, 'y_offset': 10})

                workbook.close()