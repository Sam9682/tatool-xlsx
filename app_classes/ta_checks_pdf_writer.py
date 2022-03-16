import csv
import json
import logging
import os
import pdfkit
import platform

logger = logging.getLogger(__name__)

class TAChecksPdfWriter:
    
    def __init__(self, input_args):
        self.input_args = input_args
    
    def get_ta_checks_pdf_columns(self, checkname):
        if checkname == 'Low Utilization Amazon EC2 Instances':
                return ["Account-Id","Region","Instance-Id","InstanceName", "daysUnderUtilized", "Average Monthly Cost"]
        elif checkname == 'Idle Load Balancers':
                return ["Account-Id", "Region", "ELBName", "Reason", "MonthlyCostSaving"]
        elif checkname == 'Underutilized Amazon EBS Volumes':
                return ["Account-Id", "Region", "volumeId", "volumeName", "volumeSize", "currentMonthlyCost"]
        elif checkname == 'Unassociated Elastic IP Addresses':
                return ["Account-Id", "Account Display Name", "Region", "IPAddress"]
        elif checkname == 'Security Groups - Specific Ports Unrestricted':
                return ["Account-Id", "Region", "SGName", "Protocol", "Port", "Status"]
        elif checkname == 'Security Groups - Unrestricted Access':
                return ["Account-Id", "SGName", "Protocol", "Port", "Addresses", "Status"]
        elif checkname == 'IAM Use':
                return ["Account-Id", "Account Display Name"]
        elif checkname == 'Amazon S3 Bucket Permissions':
                return ["Account-Id", "regionDisplayName", "bucketName", "Status"]
        elif checkname == 'MFA on Root Account':
                return ["Account-Id", "Account Display Name"]
        elif checkname == 'IAM Password Policy':
                return ["Account-Id", "Account Display Name", "Status"]
        elif checkname == 'Amazon RDS Security Group Access Risk':
                return ["Account-Id", "Regions", "RDS Security Group Name"]
        elif checkname == 'Amazon EBS Snapshots':
                return ["Account-Id","Region","Volume-Id","VolumeName","Status","Reason"]
        elif checkname == 'Amazon EC2 Availability Zone Balance':
                return ["Account-Id","Region","Status","Reason"]
        elif checkname == 'Load Balancer Optimization ':
                return ["Account-Id","Region","ELBName","Status","Reason"]
        elif checkname == 'VPN Tunnel Redundancy':
                return ["Account-Id","Region","VPNId","VPCId","tunnelCount"]
        elif checkname == 'High Utilization Amazon EC2 Instances':
                return ["Account-Id","Region","Instance-Id","InstanceName", "14DAvgCPUUtil%","daysOverUtilized"]
        elif checkname == 'Auto Scaling Group Resources':
                return ["Account-Id", "Region", "aSGName", "Status"]
        elif checkname == 'Amazon RDS Backups':
                return ["Account-Id", "Region", "RDS Instance-Id", "Status"]
        elif checkname == 'Amazon RDS Multi-AZ':
                return ["Account-Id", "Region", "Availability Zone", "RDS Instance-Name"]
        elif checkname == 'Auto Scaling Group Health Check':
                return ["Account-Id", "Region", "aSGName", "ELB Active", "healthCheckType"]
        elif checkname == 'Service Limits':
                return ["Account-Id","Region","Service","LimitName","Limit","Usage"]
        elif checkname == 'Amazon S3 Bucket Logging':
                return ["Account-Id","Region","bucketName","Status","Reason"]
        elif checkname == 'Amazon EBS Provisioned IOPS (SSD) Volume Attachment Configuration':
                return ["Account-Id","Region","Volume-Id","Instance-Id"]
        elif checkname == 'Large Number of Rules in an EC2 Security Group':
                return ["Account-Id", "Region", "GroupName", "InboundRulesCount", "OutboundRulesCount"]
        elif checkname == 'Large Number of EC2 Security Group Rules Applied to an Instance':
                return ["Account-Id","Region","instanceId","Instance-Name","vpcId","inboundRuleCount","outboundRuleCount"]
        elif checkname == 'Amazon RDS Idle DB Instances':
                return ["Account-Id",  "Region", "RDS Instance-Name", "Days Since Last Connection", "Estimated Monthly Savings"]
        elif checkname == 'Amazon Route 53 Alias Resource Record Sets':
                return ["Account-Id",  "resourceRecordSetName", "resourceRecordSetType", "aliasTarget"]
        elif checkname == 'Amazon Route 53 Name Server Delegations':
                return ["Account-Id", "hostedZoneName", "hostedZoneId", "configuredDelegationCount"]
        elif checkname == 'Amazon Route 53 High TTL Resource Record Sets':
                return ["Account-Id",  "hostedZoneName", "hostedZoneId", "resourceRecordSetName", "resourceRecordSetType"]
        elif checkname == 'Overutilized Amazon EBS Magnetic Volumes':
                return ["Account-Id", "Region", "volumeId", "Name"]
        elif checkname == 'CloudFront Content Delivery Optimization':
                return ["Account-Id", "Region", "bucketName", "StorageSize", "transferSize", "Status"]
        elif checkname == 'Amazon Route 53 Latency Resource Record Sets':
                return ["Account-Id", "hostedZoneName", "hostedZoneId", "resourceRecordSetName", "resourceRecordSetType"]
        elif checkname == 'Amazon Route 53 MX Resource Record Sets and Sender Policy Framework':
                return ["Account-Id", "hostedZoneName", "hostedZoneId", "resourceRecordSetName"]
        elif checkname == 'Amazon Route 53 Failover Resource Record Sets':
                return ["Account-Id", "hostedZoneName", "hostedZoneId", "resourceRecordSetName", "resourceRecordSetType"]
        elif checkname == 'Amazon Route 53 Deleted Health Checks':
                return ["Account-Id", "hostedZoneName", "hostedZoneId", "resourceRecordSetName", "resourceRecordSetType"]
        elif checkname == 'AWS CloudTrail Logging':
                return ["Account-Id","Account Display Name","Region","Status"]
        elif checkname == 'Amazon EC2 Reserved Instances Optimization':
                return ["Account-Id","Account Display Name","Availability Zone","Instance-Type"]
        elif checkname == 'ELB Listener Security':
                return ["Account-Id","Region","ELBName","Status"]
        elif checkname == 'ELB Security Groups':
                return ["Account-Id","Region","ELBName","Status"]
        elif checkname == 'ELB Cross-Zone Load Balancing':
                return ["Account-Id","Region","ELBName", "Reason"]
        elif checkname == 'ELB Connection Draining':
                return ["Account-Id","Region","ELBName", "Reason"]
        elif checkname == 'CloudFront Header Forwarding and Cache Hit Ratio':
                return ["Account-Id", "distributionDomainName", "cacheBehaviorPath", "inefficientHeaders"]
        elif checkname == 'CloudFront Custom SSL Certificates in the IAM Certificate Store':
                return ["Account-Id", "distributionDomainName", "certificateName", "Reason"]
        elif checkname == 'CloudFront SSL Certificate on the Origin Server':
                return ["Account-Id", "distributionDomainName", "originName", "Reason"]
        elif checkname == 'Amazon EC2 to EBS Throughput Optimization':
                return ["Account-Id", "Region", "Instance-Id", "Instance-Type"]
        elif checkname == 'CloudFront Alternate Domain Names':
                return ["Account-Id", "distributionDomainName", "CNAME", "Status", "Reason"]
        elif checkname == 'IAM Access Key Rotation':
                return ["Account-Id","iamUser","IAMAccessKey","Status"]
        elif checkname == 'Exposed Access Keys':
                return ["Account-Id", "accessKey", "userName", "fraudType", "caseId", "location"]
        elif checkname == 'Underutilized Amazon Redshift Clusters':
                return ["Account-Id", "Region", "ClusterName", "Reason", "estimatedMonthlySavings"]
        elif checkname == 'Amazon EC2 Reserved Instance Lease Expiration':
                return ["Account-Id","Account Display Name","Region","Reservation-Id"]
        elif checkname == 'Amazon S3 Bucket Versioning':
                return ["Account-Id","Region","bucketName","Status","versioningStatus"]
        elif checkname == 'AWS Direct Connect Connection Redundancy':
                return ["Account-Id", "Region", "Location", "Connection ID"]
        elif checkname == 'AWS Direct Connect Location Redundancy':
                return ["Account-Id", "Region", "Location", "Connection Details"]
        elif checkname == 'AWS Direct Connect Virtual Interface Redundancy':
                return ["Account-Id", "Region", "Gateway ID", "Location for VIF", "Connection ID for VIF"]
        elif checkname == 'Amazon Aurora DB Instance Accessibility':
                return ["Account-Id", "Region", "Cluster", "Public DB Instances", "Private DB Instances"]
        elif checkname == 'PV Driver Version for EC2 Windows Instances':
                return ["Account-Id","Region","Instance-id","ConfigStatus"]
        elif checkname == 'EC2Config Service for EC2 Windows Instances':
                return ["Account-Id","Region","Instance-id","ConfigStatus"]
        elif checkname == 'Amazon EBS Public Snapshots':
                return ["Account-Id", "Region", "Volume ID", "Snapshot ID"]
        elif checkname == 'Amazon RDS Public Snapshots':
                return ["Account-Id", "Region", "DB Instance or Cluster ID", "Snapshot ID"]
        elif checkname == 'EC2 On-Demand Instances':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'SES Daily Sending Quota':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'EBS Provisioned IOPS (SSD) Volume Aggregate IOPS':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'EBS Provisioned IOPS SSD (io1) Volume Storage':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'EBS Active Volumes':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'EBS Active Snapshots':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'EBS General Purpose SSD (gp2) Volume Storage':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'EBS Magnetic (standard) Volume Storage':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'EC2 Elastic IP Addresses':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'EC2 Reserved Instance Leases':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'Kinesis Shards per Region':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'CloudFormation Stacks':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'Auto Scaling Launch Configurations':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'Auto Scaling Groups':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'VPC':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'VPC Internet Gateways':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'VPC Elastic IP Address':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'IAM Instance Profiles':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'IAM Roles':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'IAM Policies':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'IAM Users':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'IAM Server Certificates':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'IAM Group':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'ELB Active Load Balancers':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'RDS Cluster Roles':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'RDS Cluster Parameter Groups':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'RDS Clusters':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'RDS Reserved Instances':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'RDS Subnets per Subnet Group':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'RDS Subnet Groups':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'RDS Option Groups':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'RDS Event Subscriptions':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'RDS DB Snapshots Per User':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'RDS Total Storage Quota':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'RDS DB Parameter Groups':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'RDS Read Replicas per Master':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'RDS DB Security Groups':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'RDS DB Instances':
                return ["Account-Id"]
        elif checkname == 'RDS Max Auths per Security Group':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'EBS Throughput Optimized HDD (st1) Volume Storage':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'EBS Cold HDD (sc1) Volume Storage':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'DynamoDB Read Capacity':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'DynamoDB Write Capacity':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'Route 53 Hosted Zones':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'Route 53 Max Health Checks':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'Route 53 Reusable Delegation Sets':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'Route 53 Traffic Policies':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'Route 53 Traffic Policy Instances':
                return ["Account-Id", "Region", "Service", "Limit_Checked", "Limit", "Usage"]
        elif checkname == 'ENA Driver Version for EC2 Windows Instances':
                return ["Account-Id", "Region", "Last_Time_Driver_Loaded", "InstanceId", "Reason"]
        elif checkname == 'NVMe Driver Version for EC2 Windows Instances':
                return ["Account-Id", "Region", "Last_Time_Driver_Loaded", "InstanceId", "Reason"]

    def get_ta_check_descriptions(self):
        checks_description = {}
        with open('resources/describe-trusted-advisor-checks.json') as f:
                checks = json.load(f)
                for item in checks['checks']:
                        checks_description[item['name']] = item['description']
        return checks_description

    def get_ta_check_categories(self):
        checks_categories = {}
        with open('resources/describe-trusted-advisor-checks.json') as f:
                checks = json.load(f)
                for item in checks['checks']:
                        checks_categories[item['name']] = item['category']
        return checks_categories

    def convert_html_to_pdf(self, input_filename, output_filename):
        print("   -- Generation of %s" % output_filename)
        environment = platform.system()
        if environment == "Windows":
                config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
        elif environment == "Darwin":
                config = pdfkit.configuration(wkhtmltopdf="/usr/local/bin/wkhtmltopdf")
        elif environment == "Linux":
                config = pdfkit.configuration(wkhtmltopdf="/usr/bin/wkhtmltopdf")
        pdfkit.from_file(input_filename, output_filename, configuration=config)

    def write_ta_check_pdfs(self):
        logging.info("Writing the pdf file...")
        checks_descriptions = self.get_ta_check_descriptions()
        checks_categories = self.get_ta_check_categories()
        files = os.listdir(self.input_args.unfiltered_folder + 'unfiltered_split_by_checkname/')
        for name in files:
                try:
                        check_name = str(name).replace(".csv","")
                        if check_name in checks_descriptions.keys():
                                catergory_name = checks_categories[check_name]
                                category_path = "%s/%s" % (self.input_args.ta_checks_pdf_folder, catergory_name)
                                with open("%s/%s" % (self.input_args.unfiltered_folder + 'unfiltered_split_by_checkname', name), mode="r") as csvfile:
                                        has_content = False
                                        if not os.path.exists(category_path):
                                                os.makedirs(category_path)
                                        with open("%s/%s.html" % (category_path, check_name), 'w') as myFile:
                                                myFile.write('<html><head><style>body {font-family: arial; background-color: #ffffff;}</style></head><body><h1>%s</h1><p>%s</p><b>Check Summary</b><br />' % (check_name, checks_descriptions[check_name]))
                                                myFile.write('<table border="1"><tr>')
                                                for column in self.get_ta_checks_pdf_columns(check_name):
                                                        myFile.write('<th>%s</th>' % column)
                                                myFile.write('</tr>')
                                                reader = csv.DictReader(csvfile)
                                                for row in reader:
                                                        if 'Status External' in row.keys() and row['Status External'] == 'ok':
                                                                continue
                                                        elif 'Status' in row.keys() and row['Status'] == 'Green':
                                                                continue
                                                        else:
                                                                has_content = True
                                                                myFile.write('<tr>')
                                                                for column in self.get_ta_checks_pdf_columns(check_name):
                                                                        try:
                                                                                myFile.write('<td>%s</td>' % row[column])
                                                                        except KeyError:
                                                                                myFile.write('<td>%s</td>' % 'Error - Not Found')
                                                                myFile.write('</tr>')
                                                myFile.write('</table></body></html>')
                                        if has_content:
                                                self.convert_html_to_pdf("%s/%s.html" % (category_path, check_name),"%s/%s.pdf" % (category_path, check_name))
                                        os.remove("%s/%s.html" % (category_path, check_name))
                        else:
                                logging.warning('Check: %s was not found in describe-trusted-advisor-checks.json. Please update that file with the following command' % check_name)
                                logging.warning('aws support describe-trusted-advisor-checks --language en --region us-east-1 > describe-trusted-advisor-checks.json"')
                except(TypeError, KeyError):
                        pass
