import operator
import xlsxwriter
import logging
import datetime

logger = logging.getLogger(__name__)

class ri_excel_graphs_writer:
    def __init__(self, input_args):
        self.input_args = input_args

    def create_ri_graphs(self, ri_info_folder, one_year_first_five_savings_opportunity, three_year_first_five_savings_opportunity):

        one_year_first_five_savings_opportunity_keys_list = []
        one_year_first_five_savings_opportunity_values_list = []

        for k, v in one_year_first_five_savings_opportunity:
            one_year_first_five_savings_opportunity_keys_list.append(k)
            one_year_first_five_savings_opportunity_values_list.append(v)

        workbook = xlsxwriter.Workbook(ri_info_folder + 'RiOpportunitiesGraphs.xlsx')
        worksheet = workbook.add_worksheet()
        bold = workbook.add_format({'bold': 1})

        headings = ['Opportunity', 'Savings']

        data = []
        data.append(one_year_first_five_savings_opportunity_values_list)
        data.append(one_year_first_five_savings_opportunity_keys_list)

        worksheet.write_row('A1', headings, bold)
        worksheet.write_column('A2', data[0])
        worksheet.write_column('B2', data[1])

        chart1 = workbook.add_chart({'type': 'column'})

        chart1.add_series({
            'name': '=Sheet1!$B$1',
            'categories': '=Sheet1!$A$2:$A$6',
            'values': '=Sheet1!$B$2:$B$6',
        })

        chart1.set_title({'name': 'Top 5 One Year Reservation Monthly Savings Opportunities'})
        chart1.set_x_axis({'name': 'Opportunity'})
        chart1.set_y_axis({'name': 'Monthly Savings'})

        chart1.set_style(8)

        worksheet.insert_chart('D2', chart1, {'x_offset': 25, 'y_offset': 10})

        ###### Chart2 Three years

        three_year_first_five_savings_opportunity_keys_list = []
        three_year_first_five_savings_opportunity_values_list = []

        for k, v in three_year_first_five_savings_opportunity:
            three_year_first_five_savings_opportunity_keys_list.append(k)
            three_year_first_five_savings_opportunity_values_list.append(v)

        worksheet = workbook.add_worksheet()
        bold = workbook.add_format({'bold': 1})

        headings = ['Opportunity', 'Savings']

        data2 = []
        data2.append(three_year_first_five_savings_opportunity_values_list)
        data2.append(three_year_first_five_savings_opportunity_keys_list)

        worksheet.write_row('A1', headings, bold)
        worksheet.write_column('A2', data2[0])
        worksheet.write_column('B2', data2[1])

        chart2 = workbook.add_chart({'type': 'column'})

        chart2.add_series({
            'name': '=Sheet2!$B$1',
            'categories': '=Sheet2!$A$2:$A$6',
            'values': '=Sheet2!$B$2:$B$6',
        })

        chart2.set_title({'name': 'Top 5 Three Years Reservation Monthly Savings Opportunities'})
        chart2.set_x_axis({'name': 'Opportunity'})
        chart2.set_y_axis({'name': 'Monthly Savings'})

        chart2.set_style(8)

        worksheet.insert_chart('D2', chart2, {'x_offset': 25, 'y_offset': 10})

        workbook.close()