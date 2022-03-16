import os
import csv
import operator


class Reserved_Instances:
    def __init__(self, input_args):
        self.input_args = input_args
        self.ri_info_folder = self.input_args.output_dir + 'ri/'
        self.ri_optimization_detail_file = self.ri_info_folder + 'ri_optimization_detail.csv'

    def write_ri_detail_file(self):
        csv_filename = self.input_args.unfiltered_folder + 'full_report_with_resource-ids.csv'

        if not os.path.exists(self.ri_info_folder):
            os.makedirs(self.ri_info_folder)

        ri_detail_list = []
        with open(csv_filename, 'r') as f:
            for line in f:
                if line.split(",")[5] == 'Amazon EC2 Reserved Instances Optimization':
                    ri_detail_list.append(line)

        file_data = "".join(ri_detail_list)

        try:
            with open(self.ri_optimization_detail_file, mode="w") as f:
                f.write(
                    "CheckId,Account-Id,Account Display Name,TA Category,Status External,TA Check Name,Status Internal,Region,---,Availability Zone,Instance Type,Operating System,Current One year RI Number,MAX/AVG/MIN Running Instances,One Year suggested instances to purchase,current monthly cost,One year upfront fee,One year optimal monthly cost,One year monthly savings,Availability Zone,Instance Type,Operating System,Current Three years RI Number,MAX/AVG/MIN Running Instances,Three Year suggested instances to purchase,current monthly cost,Three years upfront fee,Three years optimal monthly cost,Three years monthly savings\n")
                f.write(file_data)
        except Exception as e:
            print(e)

    def create_graph_data(self):
        one_year_savings_opportunity_dict = {}
        three_year_savings_opportunity_dict = {}

        with open(self.ri_optimization_detail_file, 'r') as f:
            next(f)
            csvreader = csv.reader(f, delimiter=',', quotechar='"')
            for row in csvreader:
                if row[5] == 'Amazon EC2 Reserved Instances Optimization':
                    region = row[7]
                    az = row[9]
                    instance_type = row[10]
                    instance_family = row[10].split(".")[0]
                    instance_os = row[11]
                    buy_count_1y = row[14]
                    current_monthly_cost = row[15]
                    one_year_upfront_fee = row[16]
                    one_year_optimal_monthly_cost = row[17]
                    one_year_savings = float(row[18].lstrip("-").lstrip("$").replace(",", ""))
                    buy_count_3y = row[24]
                    three_year_upfront_fee = row[26]
                    three_year_optimal_monthly_cost = row[27]
                    three_year_savings = float(row[28].lstrip("-").lstrip("$").replace(",", ""))

                    one_year_savings_opportunity_dict[one_year_savings] = az + "," + instance_type + "," + buy_count_1y
                    three_year_savings_opportunity_dict[
                        three_year_savings] = az + "," + instance_type + "," + buy_count_3y

        one_year_first_five_savings_opportunity = sorted(one_year_savings_opportunity_dict.items(),
                                                         key=operator.itemgetter(0), reverse=True)[:5]
        three_year_first_five_savings_opportunity = sorted(three_year_savings_opportunity_dict.items(),
                                                           key=operator.itemgetter(0), reverse=True)[:5]

        return self.ri_info_folder, one_year_first_five_savings_opportunity, three_year_first_five_savings_opportunity
