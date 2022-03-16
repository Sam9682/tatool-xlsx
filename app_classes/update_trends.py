import logging
import datetime

logger = logging.getLogger(__name__)

class Update_Trends:
    def __init__(self):
        self.now = datetime.datetime.now()

    def update_trends_stats(self, graphs_data_dict, json_trends_dict):
        json_trends_dict = self.update_aggregated_global_count(graphs_data_dict, json_trends_dict)
        json_trends_dict = self.update_mfa_on_root_account(graphs_data_dict, json_trends_dict)
        json_trends_dict = self.update_no_backend_ELB(graphs_data_dict, json_trends_dict)
        json_trends_dict = self.ELB_sg_problems(graphs_data_dict, json_trends_dict)
        json_trends_dict = self.IAM_access_key_rotation(graphs_data_dict, json_trends_dict)
        json_trends_dict = self.IAM_password_policy(graphs_data_dict, json_trends_dict)
        json_trends_dict = self.RDS_idle_db_connection_14_plus(graphs_data_dict, json_trends_dict)
        json_trends_dict = self.RDS_no_backups(graphs_data_dict, json_trends_dict)
        json_trends_dict = self.RDS_sg_risk(graphs_data_dict, json_trends_dict)
        json_trends_dict = self.S3_bucket_logging(graphs_data_dict, json_trends_dict)
        json_trends_dict = self.S3_bucket_permissions(graphs_data_dict, json_trends_dict)
        json_trends_dict = self.S3_bucket_versioning(graphs_data_dict, json_trends_dict)
        return json_trends_dict

    def update_aggregated_global_count(self, graphs_data_dict, json_trends_dict):
        for run in graphs_data_dict:
            new_run_list = []
            new_run_list.append(self.now.strftime('%Y-%m-%d'))
            new_run_list.append(graphs_data_dict[run]['aggregated_global_count']['warning'] if (graphs_data_dict.get(run).get('aggregated_global_count').get('warning') is not None) else 0)
            new_run_list.append(graphs_data_dict[run]['aggregated_global_count']['error'] if (graphs_data_dict.get(run).get('aggregated_global_count').get('error') is not None) else 0)
            lista = json_trends_dict[run]['global_error']
            del lista[0]
            lista.append(new_run_list)
            json_trends_dict[run]['global_error'] = lista
        return json_trends_dict

    def update_mfa_on_root_account(self, graphs_data_dict, json_trends_dict):
        for run in graphs_data_dict:
            new_run_list = []
            new_run_list.append(self.now.strftime('%Y-%m-%d'))
            new_run_list.append(graphs_data_dict[run]['mfa_on_root_account']['error'] if (
            graphs_data_dict.get(run).get('mfa_on_root_account').get('error') is not None) else 0)
            lista = json_trends_dict[run]['mfa_on_root_account']
            del lista[0]
            lista.append(new_run_list)
            json_trends_dict[run]['mfa_on_root_account'] = lista
        return json_trends_dict

    def update_no_backend_ELB(self, graphs_data_dict, json_trends_dict):
        for run in graphs_data_dict:
            new_run_list = []
            new_run_list.append(self.now.strftime('%Y-%m-%d'))
            new_run_list.append(graphs_data_dict[run]['no_backend_ELB']['warning'] if (
            graphs_data_dict.get(run).get('no_backend_ELB').get('warning') is not None) else 0)
            lista = json_trends_dict[run]['no_backend_ELB']
            del lista[0]
            lista.append(new_run_list)
            json_trends_dict[run]['no_backend_ELB'] = lista
        return json_trends_dict

    def ELB_sg_problems(self, graphs_data_dict, json_trends_dict):
        for run in graphs_data_dict:
            new_run_list = []
            new_run_list.append(self.now.strftime('%Y-%m-%d'))
            new_run_list.append(graphs_data_dict[run]['ELB_sg_problems']['Yellow'] if (graphs_data_dict.get(run).get('ELB_sg_problems').get('Yellow') is not None) else 0)
            new_run_list.append(graphs_data_dict[run]['ELB_sg_problems']['Red'] if (graphs_data_dict.get(run).get('ELB_sg_problems').get('Red') is not None) else 0)
            lista = json_trends_dict[run]['ELB_sg_problems']
            del lista[0]
            lista.append(new_run_list)
            json_trends_dict[run]['ELB_sg_problems'] = lista
        return json_trends_dict

    def IAM_access_key_rotation(self, graphs_data_dict, json_trends_dict):
        for run in graphs_data_dict:
            new_run_list = []
            new_run_list.append(self.now.strftime('%Y-%m-%d'))
            new_run_list.append(graphs_data_dict[run]['IAM_access_key_rotation']['Yellow'] if (graphs_data_dict.get(run).get('IAM_access_key_rotation').get('Yellow') is not None) else 0)
            new_run_list.append(graphs_data_dict[run]['IAM_access_key_rotation']['Red'] if (graphs_data_dict.get(run).get('IAM_access_key_rotation').get('Red') is not None) else 0)
            lista = json_trends_dict[run]['IAM_access_key_rotation']
            del lista[0]
            lista.append(new_run_list)
            json_trends_dict[run]['IAM_access_key_rotation'] = lista
        return json_trends_dict

    def IAM_password_policy(self, graphs_data_dict, json_trends_dict):
        for run in graphs_data_dict:
            new_run_list = []
            new_run_list.append(self.now.strftime('%Y-%m-%d'))
            new_run_list.append(graphs_data_dict[run]['IAM_password_policy']['Yellow'] if (graphs_data_dict.get(run).get('IAM_password_policy').get('Yellow') is not None) else 0)
            new_run_list.append(graphs_data_dict[run]['IAM_password_policy']['Red'] if (graphs_data_dict.get(run).get('IAM_password_policy').get('Red') is not None) else 0)
            lista = json_trends_dict[run]['IAM_password_policy']
            del lista[0]
            lista.append(new_run_list)
            json_trends_dict[run]['IAM_password_policy'] = lista
        return json_trends_dict

    def RDS_idle_db_connection_14_plus(self, graphs_data_dict, json_trends_dict):
        for run in graphs_data_dict:
            new_run_list = []
            new_run_list.append(self.now.strftime('%Y-%m-%d'))
            new_run_list.append(graphs_data_dict[run]['RDS_idle_db_connection']['14+'] if (
            graphs_data_dict.get(run).get('RDS_idle_db_connection').get('14+') is not None) else 0)
            lista = json_trends_dict[run]['RDS_idle_db_connection_14_plus']
            del lista[0]
            lista.append(new_run_list)
            json_trends_dict[run]['RDS_idle_db_connection_14_plus'] = lista
        return json_trends_dict

    def RDS_no_backups(self, graphs_data_dict, json_trends_dict):
        for run in graphs_data_dict:
            new_run_list = []
            new_run_list.append(self.now.strftime('%Y-%m-%d'))
            new_run_list.append(graphs_data_dict[run]['RDS_no_backups']['error'] if (
            graphs_data_dict.get(run).get('RDS_no_backups').get('error') is not None) else 0)
            lista = json_trends_dict[run]['RDS_no_backups']
            del lista[0]
            lista.append(new_run_list)
            json_trends_dict[run]['RDS_no_backups'] = lista
        return json_trends_dict

    def RDS_sg_risk(self, graphs_data_dict, json_trends_dict):
        for run in graphs_data_dict:
            new_run_list = []
            new_run_list.append(self.now.strftime('%Y-%m-%d'))
            new_run_list.append(graphs_data_dict[run]['RDS_sg_risk']['Yellow'] if (graphs_data_dict.get(run).get('RDS_sg_risk').get('Yellow') is not None) else 0)
            new_run_list.append(graphs_data_dict[run]['RDS_sg_risk']['Red'] if (graphs_data_dict.get(run).get('RDS_sg_risk').get('Red') is not None) else 0)
            lista = json_trends_dict[run]['RDS_sg_risk']
            del lista[0]
            lista.append(new_run_list)
            json_trends_dict[run]['RDS_sg_risk'] = lista
        return json_trends_dict

    def S3_bucket_logging(self, graphs_data_dict, json_trends_dict):
        for run in graphs_data_dict:
            new_run_list = []
            new_run_list.append(self.now.strftime('%Y-%m-%d'))
            new_run_list.append(graphs_data_dict[run]['S3_bucket_logging']['Yellow'] if (graphs_data_dict.get(run).get('S3_bucket_logging').get('Yellow') is not None) else 0)
            new_run_list.append(graphs_data_dict[run]['S3_bucket_logging']['Red'] if (graphs_data_dict.get(run).get('S3_bucket_logging').get('Red') is not None) else 0)
            new_run_list.append(graphs_data_dict[run]['S3_bucket_logging']['Green'] if (graphs_data_dict.get(run).get('S3_bucket_logging').get('Green') is not None) else 0)
            lista = json_trends_dict[run]['S3_bucket_logging']
            del lista[0]
            lista.append(new_run_list)
            json_trends_dict[run]['S3_bucket_logging'] = lista
        return json_trends_dict

    def S3_bucket_permissions(self, graphs_data_dict, json_trends_dict):
        for run in graphs_data_dict:
            new_run_list = []
            new_run_list.append(self.now.strftime('%Y-%m-%d'))
            new_run_list.append(graphs_data_dict[run]['S3_bucket_permissions']['Yellow'] if (graphs_data_dict.get(run).get('S3_bucket_permissions').get('Yellow') is not None) else 0)
            new_run_list.append(graphs_data_dict[run]['S3_bucket_permissions']['Red'] if (graphs_data_dict.get(run).get('S3_bucket_permissions').get('Red') is not None) else 0)
            lista = json_trends_dict[run]['S3_bucket_permissions']
            del lista[0]
            lista.append(new_run_list)
            json_trends_dict[run]['S3_bucket_permissions'] = lista
        return json_trends_dict

    def S3_bucket_versioning(self, graphs_data_dict, json_trends_dict):
        for run in graphs_data_dict:
            new_run_list = []
            new_run_list.append(self.now.strftime('%Y-%m-%d'))
            new_run_list.append(graphs_data_dict[run]['S3_bucket_versioning']['Yellow'] if (graphs_data_dict.get(run).get('S3_bucket_versioning').get('Yellow') is not None) else 0)
            lista = json_trends_dict[run]['S3_bucket_versioning']
            del lista[0]
            lista.append(new_run_list)
            json_trends_dict[run]['S3_bucket_versioning'] = lista
        return json_trends_dict