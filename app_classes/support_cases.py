import json
import logging
import datetime
import csv
import xlsxwriter
from multiprocessing.dummy import Pool as ThreadPool
from app_classes.k2helper import k2workbench

logger = logging.getLogger(__name__)


class SupportCases:

    def __init__(self, input_args):
        self.input_args = input_args
        self.k2 = k2workbench()
        self.cases_list = []

    def kick_parallel_searchCases(self, active_accounts_and_display_option_tuples_list):
        self.cases_list.append(
            "accountId,DisplayFormat,issueType,serviceCode,severityCode,submittedBy,subject,timeCreated,caseDirectionType,status,InternalCaseId,ExternalCaseId,categoryCode,contact_method,NumberOfRatings,NumberOf_1_Stars,NumberOf_2_Stars,NumberOf_3_Stars,NumberOf_4_Stars,NumberOf_5_Stars,Paragon_Link")
        pool = ThreadPool(self.input_args.threads)
        pool.map(self.searchCases, active_accounts_and_display_option_tuples_list)
        pool.close()
        pool.join()
        return self.cases_list

    def searchCases(self, active_accounts_and_display_option_tuples_list):
        accountid = active_accounts_and_display_option_tuples_list[0]
        account_display_name = active_accounts_and_display_option_tuples_list[1]
        logging.info(
            "Getting the support cases for the account " + account_display_name + " from " + self.input_args.cases_start_time + " to " + self.input_args.cases_end_time + "...")
        marker = None
        # pagination enabled (token marker)
        while marker != 'page_end':
            payload = {"apiName": "support.searchCases",
                       "args": {'filterBy': {
                           'createdBy': [{'accountId': accountid}],
                           "status": "resolved",
                           "afterTime": self.input_args.cases_start_time,
                           "beforeTime": self.input_args.cases_end_time},
                           "nextToken": marker}}

            r = self.k2.post(payload)

            try:
                searchCases_result = json.loads(r.text)
                cases = searchCases_result['cases']
                for case in cases:
                    number_of_ratings = 0
                    number_of_1_stars = 0
                    number_of_2_stars = 0
                    number_of_3_stars = 0
                    number_of_4_stars = 0
                    number_of_5_stars = 0
                    contact_method = "Email"
                    payload = {"apiName": "support.describeCase", "args": {'caseId': case['caseId']}}
                    r = self.k2.post(payload)
                    describeCase_result = json.loads(r.text)
                    for communication in describeCase_result['caseDetails']['recentCommunications']['communications']:
                        if communication['rating'] is not None:
                            number_of_ratings += 1
                            if communication['rating'] == 1:
                                number_of_1_stars += 1
                            elif communication['rating'] == 2:
                                number_of_2_stars += 1
                            elif communication['rating'] == 3:
                                number_of_3_stars += 1
                            elif communication['rating'] == 4:
                                number_of_4_stars += 1
                            elif communication['rating'] == 5:
                                number_of_5_stars += 1
                for annotation in describeCase_result['annotations']:
                    if annotation['body'].startswith('ClicktoCall'):
                        contact_method = "Phone"
                    elif annotation['body'].startswith('Click-to-Chat'):
                        contact_method = "Chat"
                    self.cases_list.append(
                            accountid + ',' + account_display_name + ',' + describeCase_result['caseDetails'][
                            'issueType'] + ',' +
                            describeCase_result['caseDetails'][
                            'serviceCode'] + ',' + describeCase_result['caseDetails']['severityCode'] + ',' +
                            describeCase_result['caseDetails'][
                            'submittedBy'] + ',\"' + describeCase_result['caseDetails']['subject'].replace('\"', '') + '\",' +
                            describeCase_result['caseDetails'][
                            'timeCreated'] + ',' + describeCase_result['caseDetails']['caseDirectionType'] + ',' + \
                            describeCase_result['caseDetails']['status'] + ',' + describeCase_result['caseDetails'][
                            'caseId'] + ',' + \
                            describeCase_result['caseDetails']['displayId'] + ',' + describeCase_result['caseDetails'][
                            'categoryCode'] + ',' + contact_method + ',' + str(number_of_ratings) + ',' + str(number_of_1_stars) + ',' + str(
                            number_of_2_stars) + ',' + str(number_of_3_stars) + ',' + str(
                            number_of_4_stars) + ',' + str(
                            number_of_5_stars) + ',' + 'https://paragon-na.amazon.com/hz/view-case?caseId=' +
                            describeCase_result['caseDetails']['displayId'])
            except Exception as e:
                logging.info("Apparently no K2 support cases for the account " + account_display_name)
                marker = 'page_end'
                continue
            page = searchCases_result['nextToken']
            if page == None:
                marker = 'page_end'
            else:
                marker = page

    def write_support_cases_file(self, cases_list):
        logging.info("Writing the support cases csv file...")
        file_data = "\n".join(cases_list).encode('utf-8').strip()
        try:
            with open(self.input_args.support_cases_folder + 'support_cases.csv', mode="w") as f:
                f.write(file_data)
        except Exception as e:
            logging.error(e)

    def create_support_cases_graph_dict(self):
        self.support_cases_dict = {}
        self.support_cases_dict['total'] = {}
        self.support_cases_dict['total']['category'] = {}
        self.support_cases_dict['total']['ratings'] = {}
        self.support_cases_dict['total']['severity'] = {}
        self.support_cases_dict['total']['service'] = {}
        self.support_cases_dict['total']['account_display'] = {}
        self.support_cases_dict['total']['ratings']['1_stars'] = 0
        self.support_cases_dict['total']['ratings']['2_stars'] = 0
        self.support_cases_dict['total']['ratings']['3_stars'] = 0
        self.support_cases_dict['total']['ratings']['4_stars'] = 0
        self.support_cases_dict['total']['ratings']['5_stars'] = 0
        self.support_cases_dict['total']['severity']['low'] = 0
        self.support_cases_dict['total']['severity']['normal'] = 0
        self.support_cases_dict['total']['severity']['high'] = 0
        self.support_cases_dict['total']['severity']['urgent'] = 0
        self.support_cases_dict['total']['severity']['critical'] = 0
        with open(self.input_args.support_cases_folder + 'support_cases.csv', mode="r") as f:
            next(f)
            reader = csv.reader(f)
            for line in reader:
                year = line[7].split('-')[0]
                month = line[7].split('-')[1]
                day = line[7].split('-')[2].split('T')[0]
                account_display_format = line[1]
                issue_type = line[2]
                service_code = line[3]
                severity_code = line[4]
                case_category_code = line[12]
                number_of_ratings_per_case = int(line[14])
                number_of_1_star_per_case = int(line[15])
                number_of_2_star_per_case = int(line[16])
                number_of_3_star_per_case = int(line[17])
                number_of_4_star_per_case = int(line[18])
                number_of_5_star_per_case = int(line[19])

                self.support_cases_dict['total']['category'][case_category_code] = ((
                    self.support_cases_dict.get('total', {}).get('category', {}).get(case_category_code) + 1 if (
                            self.support_cases_dict.get('total', {}).get('category', {}).get(
                                case_category_code) is not None) else 1))
                self.support_cases_dict['total']['service'][service_code] = ((
                    self.support_cases_dict.get('total', {}).get('service', {}).get(service_code) + 1 if (
                            self.support_cases_dict.get('total', {}).get('service', {}).get(
                                service_code) is not None) else 1))
                self.support_cases_dict['total']['account_display'][account_display_format] = ((
                    self.support_cases_dict.get('total', {}).get('account_display', {}).get(account_display_format) + 1 if (
                            self.support_cases_dict.get('total', {}).get('account_display', {}).get(
                                account_display_format) is not None) else 1))
                self.support_cases_dict['total']['ratings']['1_stars'] = (
                        self.support_cases_dict.get('total', {}).get('ratings', {}).get(
                            '1_stars') + number_of_1_star_per_case)
                self.support_cases_dict['total']['ratings']['2_stars'] = (
                        self.support_cases_dict.get('total', {}).get('ratings', {}).get(
                            '2_stars') + number_of_2_star_per_case)
                self.support_cases_dict['total']['ratings']['3_stars'] = (
                        self.support_cases_dict.get('total', {}).get('ratings', {}).get(
                            '3_stars') + number_of_3_star_per_case)
                self.support_cases_dict['total']['ratings']['4_stars'] = (
                        self.support_cases_dict.get('total', {}).get('ratings', {}).get(
                            '4_stars') + number_of_4_star_per_case)
                self.support_cases_dict['total']['ratings']['5_stars'] = (
                        self.support_cases_dict.get('total', {}).get('ratings', {}).get(
                            '5_stars') + number_of_5_star_per_case)
                self.support_cases_dict['total']['severity'][severity_code] = (
                        self.support_cases_dict.get('total', {}).get('severity', {}).get(severity_code) + 1)

                if self.support_cases_dict.get(year) is None:
                    self.support_cases_dict[year] = {}

                if self.support_cases_dict.get(year).get(month) is None:
                    self.support_cases_dict[year][month] = {}
                    self.support_cases_dict[year][month]['total_number_of_monthly_cases'] = 1
                    self.support_cases_dict[year][month]['total_number_of_monthly_ratings'] = number_of_ratings_per_case
                    self.support_cases_dict[year][month][
                        'total_number_of_1_star_per_month'] = number_of_1_star_per_case
                    self.support_cases_dict[year][month][
                        'total_number_of_2_star_per_month'] = number_of_2_star_per_case
                    self.support_cases_dict[year][month][
                        'total_number_of_3_star_per_month'] = number_of_3_star_per_case
                    self.support_cases_dict[year][month][
                        'total_number_of_4_star_per_month'] = number_of_4_star_per_case
                    self.support_cases_dict[year][month][
                        'total_number_of_5_star_per_month'] = number_of_5_star_per_case
                    self.support_cases_dict[year][month]['category'] = {}
                    self.support_cases_dict[year][month]['category'][case_category_code] = 1
                    self.support_cases_dict[year][month]['issue_type'] = {}
                    self.support_cases_dict[year][month]['issue_type'][issue_type] = 1
                    self.support_cases_dict[year][month]['service_code'] = {}
                    self.support_cases_dict[year][month]['service_code'][service_code] = 1
                    self.support_cases_dict[year][month]['severity'] = {}
                    self.support_cases_dict[year][month]['severity'][severity_code] = 1
                    self.support_cases_dict[year][month]['account_display'] = {}
                    self.support_cases_dict[year][month]['account_display'][account_display_format] = 1
                else:
                    self.support_cases_dict[year][month][
                        'total_number_of_monthly_cases'] = self.support_cases_dict.get(year, {}).get(month, {}).get(
                        'total_number_of_monthly_cases') + 1
                    self.support_cases_dict[year][month][
                        'total_number_of_monthly_ratings'] = self.support_cases_dict.get(year,
                                                                                         {}).get(
                        month, {}).get('total_number_of_monthly_ratings') + number_of_ratings_per_case
                    self.support_cases_dict[year][month][
                        'total_number_of_1_star_per_month'] = self.support_cases_dict.get(year,
                                                                                          {}).get(
                        month, {}).get('total_number_of_1_star_per_month') + number_of_1_star_per_case
                    self.support_cases_dict[year][month][
                        'total_number_of_2_star_per_month'] = self.support_cases_dict.get(year,
                                                                                          {}).get(
                        month, {}).get('total_number_of_2_star_per_month') + number_of_2_star_per_case
                    self.support_cases_dict[year][month][
                        'total_number_of_3_star_per_month'] = self.support_cases_dict.get(year,
                                                                                          {}).get(
                        month, {}).get('total_number_of_3_star_per_month') + number_of_3_star_per_case
                    self.support_cases_dict[year][month][
                        'total_number_of_4_star_per_month'] = self.support_cases_dict.get(year,
                                                                                          {}).get(
                        month, {}).get('total_number_of_4_star_per_month') + number_of_4_star_per_case
                    self.support_cases_dict[year][month][
                        'total_number_of_5_star_per_month'] = self.support_cases_dict.get(year,
                                                                                          {}).get(
                        month, {}).get('total_number_of_5_star_per_month') + number_of_5_star_per_case
                    self.support_cases_dict[year][month]['category'][case_category_code] = ((
                        self.support_cases_dict.get(year, {}).get(month, {}).get('category', {}).get(
                            case_category_code) + 1 if (
                                self.support_cases_dict.get(year, {}).get(month, {}).get('category', {}).get(
                                    case_category_code) is not None) else 1))
                    self.support_cases_dict[year][month]['issue_type'][case_category_code] = ((
                        self.support_cases_dict.get(year, {}).get(month, {}).get('issue_type', {}).get(
                            issue_type) + 1 if (
                                self.support_cases_dict.get(year, {}).get(month, {}).get('issue_type', {}).get(
                                    issue_type) is not None) else 1))
                    self.support_cases_dict[year][month]['service_code'][service_code] = ((
                        self.support_cases_dict.get(year, {}).get(month, {}).get('service_code', {}).get(
                            service_code) + 1 if (
                                self.support_cases_dict.get(year, {}).get(month, {}).get('service_code', {}).get(
                                    service_code) is not None) else 1))
                    self.support_cases_dict[year][month]['severity'][severity_code] = ((
                        self.support_cases_dict.get(year, {}).get(month, {}).get('severity', {}).get(
                            severity_code) + 1 if (
                                self.support_cases_dict.get(year, {}).get(month, {}).get('severity', {}).get(
                                    severity_code) is not None) else 1))
                    self.support_cases_dict[year][month]['account_display'][account_display_format] = ((
                        self.support_cases_dict.get(year, {}).get(month, {}).get('account_display', {}).get(
                            account_display_format) + 1 if (
                                self.support_cases_dict.get(year, {}).get(month, {}).get('account_display', {}).get(
                                    account_display_format) is not None) else 1))

    def get_cases_monthly_data_for_graphs(self):
        self.total_number_of_category_cases_list = []
        self.total_number_of_ratings_list = []
        self.total_number_of_cases_by_severity_list = []
        self.total_number_of_service_cases_list = []
        self.total_number_of_account_cases_list = []
        self.month_and_number_of_cases_list = []
        self.month_and_ratings_12345_list = []
        self.month_and_severity_list = []
        self.month_and_number_of_category_cases_list = []
        self.month_and_number_of_service_cases_list = []
        self.month_and_number_of_account_cases_list = []

        for category, value in self.support_cases_dict['total']['category'].items():
            self.total_number_of_category_cases_list.append((category, value))

        for service, value in self.support_cases_dict['total']['service'].items():
            self.total_number_of_service_cases_list.append((service, value))

        for account, value in self.support_cases_dict['total']['account_display'].items():
            self.total_number_of_account_cases_list.append((account, value))

        self.total_number_of_ratings_list.append(self.support_cases_dict['total']['ratings']['1_stars'])
        self.total_number_of_ratings_list.append(self.support_cases_dict['total']['ratings']['2_stars'])
        self.total_number_of_ratings_list.append(self.support_cases_dict['total']['ratings']['3_stars'])
        self.total_number_of_ratings_list.append(self.support_cases_dict['total']['ratings']['4_stars'])
        self.total_number_of_ratings_list.append(self.support_cases_dict['total']['ratings']['5_stars'])

        self.total_number_of_cases_by_severity_list.append(self.support_cases_dict['total']['severity']['low'])
        self.total_number_of_cases_by_severity_list.append(self.support_cases_dict['total']['severity']['normal'])
        self.total_number_of_cases_by_severity_list.append(self.support_cases_dict['total']['severity']['high'])
        self.total_number_of_cases_by_severity_list.append(self.support_cases_dict['total']['severity']['urgent'])
        self.total_number_of_cases_by_severity_list.append(self.support_cases_dict['total']['severity']['critical'])

        for year, month_values in self.support_cases_dict.items():
            if year == 'total':
                continue
            else:
                for month, values in month_values.items():
                    self.month_and_number_of_cases_list.append(
                        ((year + '-' + month), str(values['total_number_of_monthly_cases'])))
                    temp_month_and_number_of_category_cases_list = []
                    temp_month_and_number_of_service_cases_list = []
                    temp_month_and_number_of_account_display_cases_list = []
                    temp_month_and_ratings_12345_list = []
                    temp_month_and_severity_list = []
                    temp_month_and_number_of_category_cases_list.append((year + '-' + month))
                    temp_month_and_number_of_service_cases_list.append((year + '-' + month))
                    temp_month_and_number_of_account_display_cases_list.append((year + '-' + month))
                    temp_month_and_ratings_12345_list.append((year + '-' + month))
                    temp_month_and_severity_list.append((year + '-' + month))
                    temp_month_and_ratings_12345_list.append(values['total_number_of_1_star_per_month'])
                    temp_month_and_ratings_12345_list.append(values['total_number_of_2_star_per_month'])
                    temp_month_and_ratings_12345_list.append(values['total_number_of_3_star_per_month'])
                    temp_month_and_ratings_12345_list.append(values['total_number_of_4_star_per_month'])
                    temp_month_and_ratings_12345_list.append(values['total_number_of_5_star_per_month'])
                    try:
                        temp_month_and_severity_list.append(values['severity']['low'])
                    except:
                        temp_month_and_severity_list.append(0)
                    try:
                        temp_month_and_severity_list.append(values['severity']['normal'])
                    except:
                        temp_month_and_severity_list.append(0)
                    try:
                        temp_month_and_severity_list.append(values['severity']['high'])
                    except:
                        temp_month_and_severity_list.append(0)
                    try:
                        temp_month_and_severity_list.append(values['severity']['urgent'])
                    except:
                        temp_month_and_severity_list.append(0)
                    try:
                        temp_month_and_severity_list.append(values['severity']['critical'])
                    except:
                        temp_month_and_severity_list.append(0)
                    for category_code, number_of_cat_code_cases in values['category'].items():
                        temp_month_and_number_of_category_cases_list.append((category_code, number_of_cat_code_cases))
                    for service_code, number_of_service_code_cases in values['service_code'].items():
                        temp_month_and_number_of_service_cases_list.append((service_code, number_of_service_code_cases))
                    for account, number_of_account_cases in values['account_display'].items():
                        temp_month_and_number_of_account_display_cases_list.append((account, number_of_account_cases))
                    self.month_and_number_of_category_cases_list.append(temp_month_and_number_of_category_cases_list)
                    self.month_and_number_of_service_cases_list.append(temp_month_and_number_of_service_cases_list)
                    self.month_and_number_of_account_cases_list.append(temp_month_and_number_of_account_display_cases_list)
                    self.month_and_ratings_12345_list.append(temp_month_and_ratings_12345_list)
                    self.month_and_severity_list.append(temp_month_and_severity_list)

    def create_support_cases_charts(self):
        workbook = xlsxwriter.Workbook(self.input_args.support_cases_folder + 'SupportCasesGraphs.xlsx')
        worksheet = workbook.add_worksheet()
        bold = workbook.add_format({'bold': 1})

        month_list = []
        number_of_cases_list = []

        for key in sorted(self.month_and_number_of_cases_list):
            month_list.append(key[0])
            number_of_cases_list.append(int(key[1]))

        headings = ['Month', 'Number of Cases']

        data = []
        data.append(month_list)
        data.append(number_of_cases_list)

        worksheet.write_row('A1', headings, bold)
        worksheet.write_column('A2', data[0])
        worksheet.write_column('B2', data[1])

        chart1 = workbook.add_chart({'type': 'column'})

        chart1.add_series({
            'name': '=Sheet1!$B$1',
            'categories': '=Sheet1!$A$2:$A$' + str(len(month_list) + 1),
            'values': '=Sheet1!$B$2:$B$' + str(len(month_list) + 1),
        })

        chart1.set_title({'name': 'Number of cases opened by month'})
        chart1.set_x_axis({'name': 'Month'})
        chart1.set_y_axis({'name': 'Number of cases'})

        chart1.set_style(2)

        worksheet.insert_chart('D2', chart1, {'x_offset': 25, 'y_offset': 10})

        ################ Sheet 2 ################

        worksheet = workbook.add_worksheet()
        bold = workbook.add_format({'bold': 1})

        category_list = []
        number_of_category_cases_list = []

        for key in self.total_number_of_category_cases_list:
            category_list.append(key[0])
            number_of_category_cases_list.append(int(key[1]))

        headings = ['Category', 'Number of Cases']

        data = []
        data.append(category_list)
        data.append(number_of_category_cases_list)

        worksheet.write_row('A1', headings, bold)
        worksheet.write_column('A2', data[0])
        worksheet.write_column('B2', data[1])

        chart2 = workbook.add_chart({'type': 'column'})

        chart2.add_series({
            'name': '=Sheet2!$B$1',
            'categories': '=Sheet2!$A$2:$A$' + str(len(category_list) + 1),
            'values': '=Sheet2!$B$2:$B$' + str(len(category_list) + 1),
        })

        chart2.set_title({'name': 'Number of cases by category list opened for the whole selected time period '})
        chart2.set_x_axis({'name': 'Category'})
        chart2.set_y_axis({'name': 'Number of cases'})

        chart2.set_style(2)

        worksheet.insert_chart('D2', chart2, {'x_offset': 25, 'y_offset': 10})

        ################ Sheet 3 ################

        worksheet = workbook.add_worksheet()
        bold = workbook.add_format({'bold': 1})

        # Add the worksheet data that the charts will refer to.
        headings = ['Date', '1_Stars', '2_Stars', '3_Stars', '4_Stars', '5_Stars']

        dates_list =[]
        stars1_list = []
        stars2_list = []
        stars3_list = []
        stars4_list = []
        stars5_list = []

        for month in sorted(self.month_and_ratings_12345_list):
            dates_list.append(month[0])
            stars1_list.append(month[1])
            stars2_list.append(month[2])
            stars3_list.append(month[3])
            stars4_list.append(month[4])
            stars5_list.append(month[5])


        data = [
            dates_list,
            stars1_list,
            stars2_list,
            stars3_list,
            stars4_list,
            stars5_list
        ]

        worksheet.write_row('A1', headings, bold)
        worksheet.write_column('A2', data[0])
        worksheet.write_column('B2', data[1])
        worksheet.write_column('C2', data[2])
        worksheet.write_column('D2', data[3])
        worksheet.write_column('E2', data[4])
        worksheet.write_column('F2', data[5])

        # Create a new chart object. In this case an embedded chart.
        chart3 = workbook.add_chart({'type': 'line'})

        # Configure the first series.
        chart3.add_series({
            'name': '=Sheet3!$B$1',
            'categories': '=Sheet3!$A$2:$A$' + str(len(self.month_and_ratings_12345_list) + 1),
            'values': '=Sheet3!$B$2:$B$' + str(len(self.month_and_ratings_12345_list) + 1),
            'line': {'color': '#ff4545'}
        })

        chart3.add_series({
            'name': '=Sheet3!$C$1',
            'categories': '=Sheet3!$A$2:$A$' + str(len(self.month_and_ratings_12345_list) + 1),
            'values': '=Sheet3!$C$2:$C$' + str(len(self.month_and_ratings_12345_list) + 1),
            'line': {'color': '#ffa534'}
        })

        chart3.add_series({
            'name': '=Sheet3!$D$1',
            'categories': '=Sheet3!$A$2:$A$' + str(len(self.month_and_ratings_12345_list) + 1),
            'values': '=Sheet3!$D$2:$D$' + str(len(self.month_and_ratings_12345_list) + 1),
            'line': {'color': '#ffe234'}
        })

        chart3.add_series({
            'name': '=Sheet3!$E$1',
            'categories': '=Sheet3!$A$2:$A$' + str(len(self.month_and_ratings_12345_list) + 1),
            'values': '=Sheet3!$E$2:$E$' + str(len(self.month_and_ratings_12345_list) + 1),
            'line': {'color': '#b7dd29'}
        })

        chart3.add_series({
            'name': '=Sheet3!$F$1',
            'categories': '=Sheet3!$A$2:$A$' + str(len(self.month_and_ratings_12345_list) + 1),
            'values': '=Sheet3!$F$2:$F$' + str(len(self.month_and_ratings_12345_list) + 1),
            'line': {'color': '#57e32c'}
        })

        # Add a chart title and some axis labels.
        chart3.set_title({'name': 'Cases rating trend for the time period selected'})
        chart3.set_x_axis({'name': 'date'})
        chart3.set_y_axis({'name': 'Number of Ratings'})

        # Set an Excel chart style. Colors with white outline and shadow.
        chart3.set_style(10)

        # Insert the chart into the worksheet (with an offset).
        worksheet.insert_chart('H7', chart3, {'x_offset': 25, 'y_offset': 10})

        ################ Sheet 4 ################

        worksheet = workbook.add_worksheet()
        bold = workbook.add_format({'bold': 1})

        month_list = []
        number_of_cases_list = []
        general_guidance_list = []

        for key in sorted(self.month_and_number_of_cases_list):
            month_list.append(key[0])
            number_of_cases_list.append(int(key[1]))

        for month in sorted(self.month_and_number_of_category_cases_list):
            categories_tuple_list = month

            a = [tup for tup in categories_tuple_list if tup[0] == 'general-guidance']
            try:
                general_guidance_list.append(a[0][1])
            except: general_guidance_list.append(0)

        headings = ['Month', 'Number of Cases', 'General Guidance Cases']

        data = []
        data.append(month_list)
        data.append(number_of_cases_list)
        data.append(general_guidance_list)

        worksheet.write_row('A1', headings, bold)
        worksheet.write_column('A2', data[0])
        worksheet.write_column('B2', data[1])
        worksheet.write_column('C2', data[2])

        chart4 = workbook.add_chart({'type': 'column'})

        chart4.add_series({
            'name': '=Sheet4!$B$1',
            'categories': '=Sheet4!$A$2:$A$' + str(len(month_list) + 1),
            'values': '=Sheet4!$B$2:$B$' + str(len(month_list) + 1),
        })

        chart4.add_series({
            'name': '=Sheet4!$C$1',
            'categories': '=Sheet4!$A$2:$A$' + str(len(month_list) + 1),
            'values': '=Sheet4!$C$2:$C$' + str(len(month_list) + 1),
        })

        chart4.set_title({'name': 'Number of cases opened by month vs General Guidance Cases'})
        chart4.set_x_axis({'name': 'Month'})
        chart4.set_y_axis({'name': 'Number of cases'})

        chart4.set_style(2)

        worksheet.insert_chart('D2', chart4, {'x_offset': 25, 'y_offset': 10})

        ################ Sheet 5 ################

        worksheet = workbook.add_worksheet()
        bold = workbook.add_format({'bold': 1})

        ratings = ['1','2','3','4','5']

        headings = ['Rating', 'Number of Cases']

        data = []
        data.append(ratings)
        data.append(self.total_number_of_ratings_list)

        worksheet.write_row('A1', headings, bold)
        worksheet.write_column('A2', data[0])
        worksheet.write_column('B2', data[1])

        chart5 = workbook.add_chart({'type': 'column'})

        chart5.add_series({
            'name': '=Sheet5!$B$1',
            'categories': '=Sheet5!$A$2:$A$6',
            'values': '=Sheet5!$B$2:$B$6',
        })

        chart5.set_title({'name': 'Number of cases rated across the whole period selected'})
        chart5.set_x_axis({'name': 'Rating'})
        chart5.set_y_axis({'name': 'Number of cases'})

        chart5.set_style(2)

        worksheet.insert_chart('D2', chart5, {'x_offset': 25, 'y_offset': 10})

        ################ Sheet 6 ################

        worksheet = workbook.add_worksheet()
        bold = workbook.add_format({'bold': 1})

        severities = ['Low', 'Normal', 'High', 'Urgent', 'Critical']

        headings = ['Severity', 'Number of Cases']

        data = []
        data.append(severities)
        data.append(self.total_number_of_cases_by_severity_list)

        worksheet.write_row('A1', headings, bold)
        worksheet.write_column('A2', data[0])
        worksheet.write_column('B2', data[1])

        chart6 = workbook.add_chart({'type': 'column'})

        chart6.add_series({
            'name': '=Sheet6!$B$1',
            'categories': '=Sheet6!$A$2:$A$6',
            'values': '=Sheet6!$B$2:$B$6',
        })

        chart6.set_title({'name': 'Number of cases by Severity across the whole period selected'})
        chart6.set_x_axis({'name': 'Severity'})
        chart6.set_y_axis({'name': 'Number of cases'})

        chart6.set_style(2)

        worksheet.insert_chart('D2', chart6, {'x_offset': 25, 'y_offset': 10})

        ################ Sheet 7 ################

        worksheet = workbook.add_worksheet()
        bold = workbook.add_format({'bold': 1})

        service_list = []
        number_of_service_cases_list = []

        for key in self.total_number_of_service_cases_list:
            service_list.append(key[0])
            number_of_service_cases_list.append(int(key[1]))

        headings = ['Service', 'Number of Cases']

        data = []
        data.append(service_list)
        data.append(number_of_service_cases_list)

        worksheet.write_row('A1', headings, bold)
        worksheet.write_column('A2', data[0])
        worksheet.write_column('B2', data[1])

        chart2 = workbook.add_chart({'type': 'column'})

        chart2.add_series({
            'name': '=Sheet7!$B$1',
            'categories': '=Sheet7!$A$2:$A$' + str(len(service_list) + 1),
            'values': '=Sheet7!$B$2:$B$' + str(len(service_list) + 1),
        })

        chart2.set_title({'name': 'Number of cases by service opened for the whole selected time period '})
        chart2.set_x_axis({'name': 'Service'})
        chart2.set_y_axis({'name': 'Number of cases'})

        chart2.set_style(2)

        worksheet.insert_chart('D2', chart2, {'x_offset': 25, 'y_offset': 10})

        ################ Sheet 8 ################

        worksheet = workbook.add_worksheet()
        bold = workbook.add_format({'bold': 1})

        account_list = []
        number_of_account_cases_list = []

        for key in self.total_number_of_account_cases_list:
            account_list.append(key[0])
            number_of_account_cases_list.append(int(key[1]))

        headings = ['Service', 'Number of Cases']

        data = []
        data.append(account_list)
        data.append(number_of_account_cases_list)

        worksheet.write_row('A1', headings, bold)
        worksheet.write_column('A2', data[0])
        worksheet.write_column('B2', data[1])

        chart2 = workbook.add_chart({'type': 'column'})

        chart2.add_series({
            'name': '=Sheet8!$B$1',
            'categories': '=Sheet8!$A$2:$A$' + str(len(account_list) + 1),
            'values': '=Sheet8!$B$2:$B$' + str(len(account_list) + 1),
        })

        chart2.set_title({'name': 'Number of cases by account opened for the whole selected time period '})
        chart2.set_x_axis({'name': 'Account'})
        chart2.set_y_axis({'name': 'Number of cases'})

        chart2.set_style(2)

        worksheet.insert_chart('D2', chart2, {'x_offset': 25, 'y_offset': 10})

        ################ Sheet Group Preparation ################

        sheet_number = 8

        ################ Sheet Group 1 Categories by Month ################

        for month in sorted(self.month_and_number_of_category_cases_list):
            categories_tuple_list = month
            year_month_graph = categories_tuple_list[0]
            del categories_tuple_list[0]
            sheet_number += 1
            worksheet = workbook.add_worksheet()
            bold = workbook.add_format({'bold': 1})

            category_list = []
            number_of_category_cases_list = []

            for key in categories_tuple_list:
                category_list.append(key[0])
                number_of_category_cases_list.append(int(key[1]))

            headings = ['Category', 'Number of Cases']

            data = []
            data.append(category_list)
            data.append(number_of_category_cases_list)

            worksheet.write_row('A1', headings, bold)
            worksheet.write_column('A2', data[0])
            worksheet.write_column('B2', data[1])

            chart = workbook.add_chart({'type': 'column'})

            chart.add_series({
                'name': '=Sheet' + str(sheet_number) + '!$B$1',
                'categories': '=Sheet' + str(sheet_number) + '!$A$2:$A$' + str(len(category_list) + 1),
                'values': '=Sheet' + str(sheet_number) + '!$B$2:$B$' + str(len(category_list) + 1),
            })

            chart.set_title({'name': 'Number of cases by category list opened the ' + year_month_graph})
            chart.set_x_axis({'name': 'Category'})
            chart.set_y_axis({'name': 'Number of cases'})

            chart.set_style(2)

            worksheet.insert_chart('D2', chart, {'x_offset': 25, 'y_offset': 10})

        ################ Sheet Group 2 Ratings by Month ################

        for month in sorted(self.month_and_ratings_12345_list):
            monthly_rating_12345_list = month
            year_month_graph = monthly_rating_12345_list[0]
            del monthly_rating_12345_list[0]
            sheet_number += 1
            worksheet = workbook.add_worksheet()
            bold = workbook.add_format({'bold': 1})

            ratings_list = ["1","2","3","4","5"]

            headings = ['Rating', 'Number of Ratings']

            data = []
            data.append(ratings_list)
            data.append(monthly_rating_12345_list)

            worksheet.write_row('A1', headings, bold)
            worksheet.write_column('A2', data[0])
            worksheet.write_column('B2', data[1])

            chart = workbook.add_chart({'type': 'column'})

            chart.add_series({
                'name': '=Sheet' + str(sheet_number) + '!$B$1',
                'categories': '=Sheet' + str(sheet_number) + '!$A$2:$A$' + str(len(ratings_list) + 1),
                'values': '=Sheet' + str(sheet_number) + '!$B$2:$B$' + str(len(ratings_list) + 1),
            })

            chart.set_title({'name': 'Number of cases by rating for the month ' + year_month_graph})
            chart.set_x_axis({'name': 'Rating value'})
            chart.set_y_axis({'name': 'Number of cases'})

            chart.set_style(2)

            worksheet.insert_chart('D2', chart, {'x_offset': 25, 'y_offset': 10})

        ################ Sheet Group 3 Severity by Month ################

        for month in sorted(self.month_and_severity_list):
            monthly_severity_list = month
            year_month_graph = monthly_severity_list[0]
            del monthly_severity_list[0]
            sheet_number += 1
            worksheet = workbook.add_worksheet()
            bold = workbook.add_format({'bold': 1})

            severities = ['Low', 'Normal', 'High', 'Urgent', 'Critical']

            headings = ['Severity', 'Number of Cases']

            data = []
            data.append(severities)
            data.append(monthly_severity_list)

            worksheet.write_row('A1', headings, bold)
            worksheet.write_column('A2', data[0])
            worksheet.write_column('B2', data[1])

            chart = workbook.add_chart({'type': 'column'})

            chart.add_series({
                'name': '=Sheet' + str(sheet_number) + '!$B$1',
                'categories': '=Sheet' + str(sheet_number) + '!$A$2:$A$6',
                'values': '=Sheet' + str(sheet_number) + '!$B$2:$B$6',
            })

            chart.set_title({'name': 'Number of cases by Severity for the month ' + year_month_graph})
            chart.set_x_axis({'name': 'Severity'})
            chart.set_y_axis({'name': 'Number of cases'})

            chart.set_style(2)

            worksheet.insert_chart('D2', chart, {'x_offset': 25, 'y_offset': 10})

        ################ Sheet Group 4 Services by Month ################

        for month in sorted(self.month_and_number_of_service_cases_list):
            services_tuple_list = month
            year_month_graph = services_tuple_list[0]
            del services_tuple_list[0]
            sheet_number += 1
            worksheet = workbook.add_worksheet()
            bold = workbook.add_format({'bold': 1})

            service_list = []
            number_of_service_cases_list = []

            for key in services_tuple_list:
                service_list.append(key[0])
                number_of_service_cases_list.append(int(key[1]))

            headings = ['Service', 'Number of Cases']

            data = []
            data.append(service_list)
            data.append(number_of_service_cases_list)

            worksheet.write_row('A1', headings, bold)
            worksheet.write_column('A2', data[0])
            worksheet.write_column('B2', data[1])

            chart = workbook.add_chart({'type': 'column'})

            chart.add_series({
                'name': '=Sheet' + str(sheet_number) + '!$B$1',
                'categories': '=Sheet' + str(sheet_number) + '!$A$2:$A$' + str(len(service_list) + 1),
                'values': '=Sheet' + str(sheet_number) + '!$B$2:$B$' + str(len(service_list) + 1),
            })

            chart.set_title({'name': 'Number of cases by service opened the ' + year_month_graph})
            chart.set_x_axis({'name': 'Service'})
            chart.set_y_axis({'name': 'Number of cases'})

            chart.set_style(2)

            worksheet.insert_chart('D2', chart, {'x_offset': 25, 'y_offset': 10})

        ################ Sheet Group 5 Accounts by Month ################

        for month in sorted(self.month_and_number_of_account_cases_list):
            services_tuple_list = month
            year_month_graph = services_tuple_list[0]
            del services_tuple_list[0]
            sheet_number += 1
            worksheet = workbook.add_worksheet()
            bold = workbook.add_format({'bold': 1})

            account_list = []
            number_of_account_cases_list = []

            for key in services_tuple_list:
                account_list.append(key[0])
                number_of_account_cases_list.append(int(key[1]))

            headings = ['Account', 'Number of Cases']

            data = []
            data.append(account_list)
            data.append(number_of_account_cases_list)

            worksheet.write_row('A1', headings, bold)
            worksheet.write_column('A2', data[0])
            worksheet.write_column('B2', data[1])

            chart = workbook.add_chart({'type': 'column'})

            chart.add_series({
                'name': '=Sheet' + str(sheet_number) + '!$B$1',
                'categories': '=Sheet' + str(sheet_number) + '!$A$2:$A$' + str(len(account_list) + 1),
                'values': '=Sheet' + str(sheet_number) + '!$B$2:$B$' + str(len(account_list) + 1),
            })

            chart.set_title({'name': 'Number of cases by account opened the ' + year_month_graph})
            chart.set_x_axis({'name': 'Account'})
            chart.set_y_axis({'name': 'Number of cases'})

            chart.set_style(2)

            worksheet.insert_chart('D2', chart, {'x_offset': 25, 'y_offset': 10})

        workbook.close()
