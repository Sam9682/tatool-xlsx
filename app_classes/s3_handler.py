import sys
import boto3
import botocore
import logging
from os.path import normpath, basename
from app_classes.s3_progress_bytes import ProgressBytes

logger = logging.getLogger(__name__)

class S3Handler(object):
    def __init__(self, input_args):
        self.input_args = input_args

        if self.input_args.s3accesskey != None and self.input_args.s3secretkey != None:
            self.s3 = boto3.client('s3',
                aws_access_key_id=self.input_args.s3accesskey,
                aws_secret_access_key=self.input_args.s3secretkey
            )
        else:
            self.s3 = boto3.client('s3')

    def check_bucket_exists(self):
        try:
            self.s3.head_bucket(Bucket=self.input_args.s3bucket)
            return True
        except botocore.exceptions.ClientError as e:
            error_code = int(e.response['Error']['Code'])
            if error_code == 404:
                return False
        except Exception as e:
            logging.error('Unable to determine if bucket exists! Check the credentials and connection!\nPlease make sure you have configured a valid credential source (aws cli or environment variable) or just pass the accesskey/secretkey using the script options.')
            sys.exit(1)

    def get_json_file(self):
        s3_key = self.input_args.s3_key_path + 'values_trends.json'
        try:
            obj = self.s3.get_object(Bucket=self.input_args.s3bucket, Key=s3_key)
            return obj['Body'].read()
        except:
            return False

    def upload_file_s3(self, filename, run_folder):
        keyname = basename(normpath(filename))
        try:
            self.s3.upload_file(filename, self.input_args.s3bucket, self.input_args.s3_key_path + keyname,
                            Callback=ProgressBytes(keyname))
            return self.input_args.s3bucket + '/' + self.input_args.s3_key_path + keyname
        except:
            return False
