import xlsxwriter
import logging

logger = logging.getLogger(__name__)

class global_excel_trends_graphs_writer:
    def __init__(self, input_args):
        self.input_args = input_args

    def create_global_trends_charts(self, json_trends_dict):

        for run, values in json_trends_dict.items():

            if run == 'filtered' and self.input_args.filter_file_ta is not None:
                workdir = self.input_args.filtered_folder
            elif run == 'filtered' and self.input_args.filter_file_ta == None:
                continue
            elif run == 'isSuppressed':
                workdir = self.input_args.isSuppressed_folder
            else: workdir = self.input_args.unfiltered_folder

            logging.info("Generating trend charts in the directory " + workdir)

            workbook = xlsxwriter.Workbook(workdir + run + '_TrustedAdvisorGlobalTrendsGraphs.xlsx')

            dates_list = []
            warnings_list = []
            errors_list = []

            for graph_type, historical_run in values.items():
                if graph_type == 'global_error':
                    for value in historical_run:
                        dates_list.append(value[0])
                        warnings_list.append(int(value[1]))
                        errors_list.append(int(value[2]))

            worksheet = workbook.add_worksheet()
            bold = workbook.add_format({'bold': 1})

            # Add the worksheet data that the charts will refer to.
            headings = ['Date', 'Warning', 'Error']
            data = [
                dates_list,
                warnings_list,
                errors_list,
            ]

            worksheet.write_row('A1', headings, bold)
            worksheet.write_column('A2', data[0])
            worksheet.write_column('B2', data[1])
            worksheet.write_column('C2', data[2])

            # Create a new chart object. In this case an embedded chart.
            chart1 = workbook.add_chart({'type': 'line'})

            # Configure the first series.
            chart1.add_series({
                'name': '=Sheet1!$B$1',
                'categories': '=Sheet1!$A$2:$A$13',
                'values': '=Sheet1!$B$2:$B$13',
                'line': {'color': '#f4d742'}
            })

            # Configure second series. Note use of alternative syntax to define ranges.
            chart1.add_series({
                'name': '=Sheet1!$B$1',
                'categories': '=Sheet1!$A$2:$A$13',
                'values': '=Sheet1!$C$2:$C$13',
                'line': {'color': 'red'}
            })

            # Add a chart title and some axis labels.
            chart1.set_title({'name': 'Warnings and Errors trend'})
            chart1.set_x_axis({'name': 'date'})
            chart1.set_y_axis({'name': 'Number of checks'})

            # Set an Excel chart style. Colors with white outline and shadow.
            chart1.set_style(10)

            # Insert the chart into the worksheet (with an offset).
            worksheet.insert_chart('D2', chart1, {'x_offset': 25, 'y_offset': 10})

            # MFA ON ROOT ACCOUNT

            worksheet = workbook.add_worksheet()
            bold = workbook.add_format({'bold': 1})

            dates_list = []
            errors_list = []
            for graph_type, historical_run in values.items():
                if graph_type == 'mfa_on_root_account':
                    for value in historical_run:
                        dates_list.append(value[0])
                        errors_list.append(int(value[1]))

            # Add the worksheet data that the charts will refer to.
            headings = ['Date', 'Error']
            data = [
                dates_list,
                errors_list,
            ]

            worksheet.write_row('A1', headings, bold)
            worksheet.write_column('A2', data[0])
            worksheet.write_column('B2', data[1])

            # Create a new chart object. In this case an embedded chart.
            chart2 = workbook.add_chart({'type': 'line'})

            # Configure the first series.
            chart2.add_series({
                'name': '=Sheet2!$B$1',
                'categories': '=Sheet2!$A$2:$A$13',
                'values': '=Sheet2!$B$2:$B$13',
            })

            # Add a chart title and some axis labels.
            chart2.set_title({'name': 'MFA on Root Account Errors trend'})
            chart2.set_x_axis({'name': 'date'})
            chart2.set_y_axis({'name': 'Number of errors'})

            # Set an Excel chart style. Colors with white outline and shadow.
            chart2.set_style(10)

            # Insert the chart into the worksheet (with an offset).
            worksheet.insert_chart('D2', chart2, {'x_offset': 25, 'y_offset': 10})

            # NO ELB Backend Instances

            worksheet = workbook.add_worksheet()
            bold = workbook.add_format({'bold': 1})

            dates_list = []
            warnings_list = []
            for graph_type, historical_run in values.items():
                if graph_type == 'no_backend_ELB':
                    for value in historical_run:
                        dates_list.append(value[0])
                        warnings_list.append(int(value[1]))

            # Add the worksheet data that the charts will refer to.
            headings = ['Date', 'Warning']
            data = [
                dates_list,
                warnings_list,
            ]

            worksheet.write_row('A1', headings, bold)
            worksheet.write_column('A2', data[0])
            worksheet.write_column('B2', data[1])

            # Create a new chart object. In this case an embedded chart.
            chart3= workbook.add_chart({'type': 'line'})

            # Configure the first series.
            chart3.add_series({
                'name': '=Sheet3!$B$1',
                'categories': '=Sheet3!$A$2:$A$13',
                'values': '=Sheet3!$B$2:$B$13',
            })

            # Add a chart title and some axis labels.
            chart3.set_title({'name': 'Number of ELB with no back-end instances'})
            chart3.set_x_axis({'name': 'date'})
            chart3.set_y_axis({'name': 'Number of ELB'})

            # Set an Excel chart style. Colors with white outline and shadow.
            chart3.set_style(10)

            # Insert the chart into the worksheet (with an offset).
            worksheet.insert_chart('D2', chart3, {'x_offset': 25, 'y_offset': 10})


            # Chart4 ELB SG Problems

            dates_list = []
            warnings_list = []
            errors_list = []

            for graph_type, historical_run in values.items():
                if graph_type == 'ELB_sg_problems':
                    for value in historical_run:
                        dates_list.append(value[0])
                        warnings_list.append(int(value[1]))
                        errors_list.append(int(value[2]))

            worksheet = workbook.add_worksheet()
            bold = workbook.add_format({'bold': 1})

            # Add the worksheet data that the charts will refer to.
            headings = ['Date', 'Warning', 'Error']
            data = [
                dates_list,
                warnings_list,
                errors_list,
            ]

            worksheet.write_row('A1', headings, bold)
            worksheet.write_column('A2', data[0])
            worksheet.write_column('B2', data[1])
            worksheet.write_column('C2', data[2])

            # Create a new chart object. In this case an embedded chart.
            chart4 = workbook.add_chart({'type': 'line'})

            # Configure the first series.
            chart4.add_series({
                'name': '=Sheet4!$B$1',
                'categories': '=Sheet4!$A$2:$A$13',
                'values': '=Sheet4!$B$2:$B$13',
                'line': {'color': '#f4d742'}
            })

            # Configure second series. Note use of alternative syntax to define ranges.
            chart4.add_series({
                'name': ['Sheet4', 0, 2],
                'categories': ['Sheet4', 1, 0, 12, 0],
                'values': ['Sheet4', 1, 2, 12, 2],
                'line': {'color': 'red'}
            })

            # Add a chart title and some axis labels.
            chart4.set_title({'name': 'ELB Security Groups Warnings and Errors trend'})
            chart4.set_x_axis({'name': 'date'})
            chart4.set_y_axis({'name': 'Number of checks'})

            # Set an Excel chart style. Colors with white outline and shadow.
            chart4.set_style(10)

            # Insert the chart into the worksheet (with an offset).
            worksheet.insert_chart('D2', chart4, {'x_offset': 25, 'y_offset': 10})

            # Chart5 IAM_access_key_rotation

            dates_list = []
            warnings_list = []
            errors_list = []

            for graph_type, historical_run in values.items():
                if graph_type == 'IAM_access_key_rotation':
                    for value in historical_run:
                        dates_list.append(value[0])
                        warnings_list.append(int(value[1]))
                        errors_list.append(int(value[2]))

            worksheet = workbook.add_worksheet()
            bold = workbook.add_format({'bold': 1})

            # Add the worksheet data that the charts will refer to.
            headings = ['Date', 'Warning', 'Error']
            data = [
                dates_list,
                warnings_list,
                errors_list,
            ]

            worksheet.write_row('A1', headings, bold)
            worksheet.write_column('A2', data[0])
            worksheet.write_column('B2', data[1])
            worksheet.write_column('C2', data[2])

            # Create a new chart object. In this case an embedded chart.
            chart5 = workbook.add_chart({'type': 'line'})

            # Configure the first series.
            chart5.add_series({
                'name': '=Sheet5!$B$1',
                'categories': '=Sheet5!$A$2:$A$13',
                'values': '=Sheet5!$B$2:$B$13',
                'line': {'color': '#f4d742'}
            })

            # Configure second series. Note use of alternative syntax to define ranges.
            chart5.add_series({
                'name': ['Sheet5', 0, 2],
                'categories': ['Sheet5', 1, 0, 12, 0],
                'values': ['Sheet5', 1, 2, 12, 2],
                'line': {'color': 'red'}
            })

            # Add a chart title and some axis labels.
            chart5.set_title({'name': 'IAM Access Key Rotation Warnings and Errors trend'})
            chart5.set_x_axis({'name': 'date'})
            chart5.set_y_axis({'name': 'Number of checks'})

            # Set an Excel chart style. Colors with white outline and shadow.
            chart5.set_style(10)

            # Insert the chart into the worksheet (with an offset).
            worksheet.insert_chart('D2', chart5, {'x_offset': 25, 'y_offset': 10})

            # Chart6 IAM_password_policy

            dates_list = []
            warnings_list = []
            errors_list = []

            for graph_type, historical_run in values.items():
                if graph_type == 'IAM_password_policy':
                    for value in historical_run:
                        dates_list.append(value[0])
                        warnings_list.append(int(value[1]))
                        errors_list.append(int(value[2]))

            worksheet = workbook.add_worksheet()
            bold = workbook.add_format({'bold': 1})

            # Add the worksheet data that the charts will refer to.
            headings = ['Date', 'Warning', 'Error']
            data = [
                dates_list,
                warnings_list,
                errors_list,
            ]

            worksheet.write_row('A1', headings, bold)
            worksheet.write_column('A2', data[0])
            worksheet.write_column('B2', data[1])
            worksheet.write_column('C2', data[2])

            # Create a new chart object. In this case an embedded chart.
            chart6 = workbook.add_chart({'type': 'line'})

            # Configure the first series.
            chart6.add_series({
                'name': '=Sheet6!$B$1',
                'categories': '=Sheet6!$A$2:$A$13',
                'values': '=Sheet6!$B$2:$B$13',
                'line': {'color': '#f4d742'}
            })

            # Configure second series. Note use of alternative syntax to define ranges.
            chart6.add_series({
                'name': ['Sheet6', 0, 2],
                'categories': ['Sheet6', 1, 0, 12, 0],
                'values': ['Sheet6', 1, 2, 12, 2],
                'line': {'color': 'red'}
            })

            # Add a chart title and some axis labels.
            chart6.set_title({'name': 'IAM Password Policy Warnings and Errors trend'})
            chart6.set_x_axis({'name': 'date'})
            chart6.set_y_axis({'name': 'Number of checks'})

            # Set an Excel chart style. Colors with white outline and shadow.
            chart6.set_style(10)

            # Insert the chart into the worksheet (with an offset).
            worksheet.insert_chart('D2', chart6, {'x_offset': 25, 'y_offset': 10})

            # Idle DB connection +14 days

            worksheet = workbook.add_worksheet()
            bold = workbook.add_format({'bold': 1})

            dates_list = []
            errors_list = []
            for graph_type, historical_run in values.items():
                if graph_type == 'RDS_idle_db_connection_14_plus':
                    for value in historical_run:
                        dates_list.append(value[0])
                        errors_list.append(int(value[1]))

            # Add the worksheet data that the charts will refer to.
            headings = ['Date', 'Number of RDS Instances']
            data = [
                dates_list,
                errors_list,
            ]

            worksheet.write_row('A1', headings, bold)
            worksheet.write_column('A2', data[0])
            worksheet.write_column('B2', data[1])

            # Create a new chart object. In this case an embedded chart.
            chart7 = workbook.add_chart({'type': 'line'})

            # Configure the first series.
            chart7.add_series({
                'name': '=Sheet7!$B$1',
                'categories': '=Sheet7!$A$2:$A$13',
                'values': '=Sheet7!$B$2:$B$13',
            })

            # Add a chart title and some axis labels.
            chart7.set_title({'name': 'Idle RDS DB connection +14 days trend'})
            chart7.set_x_axis({'name': 'date'})
            chart7.set_y_axis({'name': 'Number of RDS Instances'})

            # Set an Excel chart style. Colors with white outline and shadow.
            chart7.set_style(10)

            # Insert the chart into the worksheet (with an offset).
            worksheet.insert_chart('D2', chart7, {'x_offset': 25, 'y_offset': 10})

            # RDS No Backups

            worksheet = workbook.add_worksheet()
            bold = workbook.add_format({'bold': 1})

            dates_list = []
            errors_list = []
            for graph_type, historical_run in values.items():
                if graph_type == 'RDS_no_backups':
                    for value in historical_run:
                        dates_list.append(value[0])
                        errors_list.append(int(value[1]))

            # Add the worksheet data that the charts will refer to.
            headings = ['Date', 'Number of RDS DBs']
            data = [
                dates_list,
                errors_list,
            ]

            worksheet.write_row('A1', headings, bold)
            worksheet.write_column('A2', data[0])
            worksheet.write_column('B2', data[1])

            # Create a new chart object. In this case an embedded chart.
            chart8 = workbook.add_chart({'type': 'line'})

            # Configure the first series.
            chart8.add_series({
                'name': '=Sheet8!$B$1',
                'categories': '=Sheet8!$A$2:$A$13',
                'values': '=Sheet8!$B$2:$B$13',
            })

            # Add a chart title and some axis labels.
            chart8.set_title({'name': 'RDS DB having NO backups'})
            chart8.set_x_axis({'name': 'date'})
            chart8.set_y_axis({'name': 'Number of RDS DBs'})

            # Set an Excel chart style. Colors with white outline and shadow.
            chart8.set_style(10)

            # Insert the chart into the worksheet (with an offset).
            worksheet.insert_chart('D2', chart8, {'x_offset': 25, 'y_offset': 10})

            # Chart9 RDS Security Groups Risk

            dates_list = []
            warnings_list = []
            errors_list = []

            for graph_type, historical_run in values.items():
                if graph_type == 'RDS_sg_risk':
                    for value in historical_run:
                        dates_list.append(value[0])
                        warnings_list.append(int(value[1]))
                        errors_list.append(int(value[2]))

            worksheet = workbook.add_worksheet()
            bold = workbook.add_format({'bold': 1})

            # Add the worksheet data that the charts will refer to.
            headings = ['Date', 'Warning', 'Error']
            data = [
                dates_list,
                warnings_list,
                errors_list,
            ]

            worksheet.write_row('A1', headings, bold)
            worksheet.write_column('A2', data[0])
            worksheet.write_column('B2', data[1])
            worksheet.write_column('C2', data[2])

            # Create a new chart object. In this case an embedded chart.
            chart9 = workbook.add_chart({'type': 'line'})

            # Configure the first series.
            chart9.add_series({
                'name': '=Sheet9!$B$1',
                'categories': '=Sheet9!$A$2:$A$13',
                'values': '=Sheet9!$B$2:$B$13',
                'line': {'color': '#f4d742'}
            })

            # Configure second series. Note use of alternative syntax to define ranges.
            chart9.add_series({
                'name': ['Sheet9', 0, 2],
                'categories': ['Sheet9', 1, 0, 12, 0],
                'values': ['Sheet9', 1, 2, 12, 2],
                'line': {'color': 'red'}
            })

            # Add a chart title and some axis labels.
            chart9.set_title({'name': 'RDS Security Groups Risk - Warnings and Errors trend'})
            chart9.set_x_axis({'name': 'date'})
            chart9.set_y_axis({'name': 'Number of checks'})

            # Set an Excel chart style. Colors with white outline and shadow.
            chart9.set_style(10)

            # Insert the chart into the worksheet (with an offset).
            worksheet.insert_chart('D2', chart9, {'x_offset': 25, 'y_offset': 10})

            # Chart10 S3 Bucket logging

            dates_list = []
            warnings_list = []
            errors_list = []
            ok_list = []

            for graph_type, historical_run in values.items():
                if graph_type == 'S3_bucket_logging':
                    for value in historical_run:
                        dates_list.append(value[0])
                        warnings_list.append(int(value[1]))
                        errors_list.append(int(value[2]))
                        ok_list.append(int(value[3]))

            worksheet = workbook.add_worksheet()
            bold = workbook.add_format({'bold': 1})

            # Add the worksheet data that the charts will refer to.
            headings = ['Date', 'Warning', 'Error', 'ok']
            data = [
                dates_list,
                warnings_list,
                errors_list,
                ok_list
            ]

            worksheet.write_row('A1', headings, bold)
            worksheet.write_column('A2', data[0])
            worksheet.write_column('B2', data[1])
            worksheet.write_column('C2', data[2])
            worksheet.write_column('D2', data[3])

            # Create a new chart object. In this case an embedded chart.
            chart10 = workbook.add_chart({'type': 'line'})

            # Configure the first series.
            chart10.add_series({
                'name': '=Sheet10!$B$1',
                'categories': '=Sheet10!$A$2:$A$13',
                'values': '=Sheet10!$B$2:$B$13',
                'line': {'color': '#f4d742'}
            })

            # Configure second series. Note use of alternative syntax to define ranges.
            chart10.add_series({
                'name': '=Sheet10!$C$1',
                'categories': '=Sheet10!$A$2:$A$13',
                'values': '=Sheet10!$C$2:$C$13',
                'line': {'color': 'red'}
            })

            # Configure third series. Note use of alternative syntax to define ranges.
            chart10.add_series({
                'name': '=Sheet10!$D$1',
                'categories': '=Sheet10!$A$2:$A$13',
                'values': '=Sheet10!$D$2:$D$13',
                'line': {'color': '#62f442'}
            })

            # Add a chart title and some axis labels.
            chart10.set_title({'name': 'S3 Bucket logging trend'})
            chart10.set_x_axis({'name': 'date'})
            chart10.set_y_axis({'name': 'Number of checks'})

            # Set an Excel chart style. Colors with white outline and shadow.
            chart10.set_style(10)

            # Insert the chart into the worksheet (with an offset).
            worksheet.insert_chart('E2', chart10, {'x_offset': 25, 'y_offset': 10})

            # Chart11 S3 Bucket permissions

            dates_list = []
            warnings_list = []
            errors_list = []

            for graph_type, historical_run in values.items():
                if graph_type == 'S3_bucket_permissions':
                    for value in historical_run:
                        dates_list.append(value[0])
                        warnings_list.append(int(value[1]))
                        errors_list.append(int(value[2]))

            worksheet = workbook.add_worksheet()
            bold = workbook.add_format({'bold': 1})

            # Add the worksheet data that the charts will refer to.
            headings = ['Date', 'Warning', 'Error']
            data = [
                dates_list,
                warnings_list,
                errors_list,
            ]

            worksheet.write_row('A1', headings, bold)
            worksheet.write_column('A2', data[0])
            worksheet.write_column('B2', data[1])
            worksheet.write_column('C2', data[2])

            # Create a new chart object. In this case an embedded chart.
            chart11 = workbook.add_chart({'type': 'line'})

            # Configure the first series.
            chart11.add_series({
                'name': '=Sheet11!$B$1',
                'categories': '=Sheet11!$A$2:$A$13',
                'values': '=Sheet11!$B$2:$B$13',
                'line': {'color': '#f4d742'}
            })

            # Configure second series. Note use of alternative syntax to define ranges.
            chart11.add_series({
                'name': '=Sheet11!$C$1',
                'categories': '=Sheet11!$A$2:$A$13',
                'values': '=Sheet11!$C$2:$C$13',
                'line': {'color': 'red'}
            })

            # Add a chart title and some axis labels.
            chart11.set_title({'name': 'S3 Bucket permissions trend'})
            chart11.set_x_axis({'name': 'date'})
            chart11.set_y_axis({'name': 'Number of checks'})

            # Set an Excel chart style. Colors with white outline and shadow.
            chart11.set_style(10)

            # Insert the chart into the worksheet (with an offset).
            worksheet.insert_chart('E2', chart11, {'x_offset': 25, 'y_offset': 10})

            # Chart12 S3 Bucket versioning enabled

            dates_list = []
            warnings_list = []

            for graph_type, historical_run in values.items():
                if graph_type == 'S3_bucket_versioning':
                    for value in historical_run:
                        dates_list.append(value[0])
                        warnings_list.append(int(value[1]))

            worksheet = workbook.add_worksheet()
            bold = workbook.add_format({'bold': 1})

            # Add the worksheet data that the charts will refer to.
            headings = ['Date', 'Warning']
            data = [
                dates_list,
                warnings_list,
            ]

            worksheet.write_row('A1', headings, bold)
            worksheet.write_column('A2', data[0])
            worksheet.write_column('B2', data[1])

            # Create a new chart object. In this case an embedded chart.
            chart12 = workbook.add_chart({'type': 'line'})

            # Configure the first series.
            chart12.add_series({
                'name': '=Sheet12!$B$1',
                'categories': '=Sheet12!$A$2:$A$13',
                'values': '=Sheet12!$B$2:$B$13',
                'line': {'color': '#f4d742'}
            })

            # Add a chart title and some axis labels.
            chart12.set_title({'name': 'S3 Bucket with versioning NOT enabled - trend'})
            chart12.set_x_axis({'name': 'date'})
            chart12.set_y_axis({'name': 'Number of Buckets'})

            # Set an Excel chart style. Colors with white outline and shadow.
            chart12.set_style(10)

            # Insert the chart into the worksheet (with an offset).
            worksheet.insert_chart('E2', chart12, {'x_offset': 25, 'y_offset': 10})

            workbook.close()