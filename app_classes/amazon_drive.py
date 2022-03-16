import base64
import httplib
import os
import time
import urllib
import logging
import ssl


logger = logging.getLogger(__name__)


class AmazonDrive(object):
    """ Class to upload the CWCB file to Amazon drive."""

    ENDPOINT = 'drive.corp.amazon.com'
    DRIVE_BASE_URL = "https://drive.corp.amazon.com/view/"
    DRIVE_ROOT = '/mnt/'
    HTTP_SUCCESS_CODES = [200, 201]
    HTTP_BAD_REQ_CODE = [400]
    HTTP_NOT_AUTH_CODE = [401]
    HTTP_NOT_FOUND_CODE = [404]
    HTTP_REDIRECT_CODES = [301, 307]
    RETRIES = 4
    SECONDS_TO_WAIT = 5

    def build_auth_headers(self, username, password):
        """Build the authorization headers to be used during requests to the Drive API.

        Arguments:
        :param username (str): Username to use for the requests
        :param password (str): Password of the username declared above

        :return headers (dict): Header dictionary
        """
        auth = base64.b64encode('{}:{}'.format(username, password))
        self.headers = {'Authorization': 'Basic {}'.format(auth)}
        return self.headers

    def _perform_upload(self, local_file, target_dir, location, body=None):
        """Perform an HTTP upload request to the API.

        Arguments:
        :param location (str): Path of location to request
        :param body (str): Body to be sent with the request
        """
        location = urllib.quote(AmazonDrive.DRIVE_ROOT + location)
        upload_attempt = 1
        connection = httplib.HTTPSConnection(AmazonDrive.ENDPOINT, context=ssl._create_unverified_context())
        seconds_to_wait = AmazonDrive.SECONDS_TO_WAIT
        while upload_attempt < AmazonDrive.RETRIES:
            try:
                connection.request('PUT', location, headers=self.headers, body=body)
                response = connection.getresponse()
                connection.close()
                if response.status in self.HTTP_SUCCESS_CODES:
                    logger.info('File successfully uploaded to the Amazon Drive: {}'.format(location))
                    drive_file_url = AmazonDrive.DRIVE_BASE_URL + target_dir + "/" + \
                                          local_file.split("/")[-1] + "?download=true"
                    return drive_file_url
                else: logger.error('Upload to Amazon Drive Failed! HTTP Error: {}'.format(response.status))
                return False
            except Exception as e:
                logger.warning(e)
                logger.warning('Unable to perform the upload the file to Amazon Drive! Retrying ... number {}'.format(upload_attempt))
                upload_attempt +=1
                time.sleep(seconds_to_wait)
                seconds_to_wait = AmazonDrive.SECONDS_TO_WAIT * 2
                connection.close()
        logger.error('Upload to Amazon Drive Failed!')
        return False

    def upload_file(self, local_file, target_dir):
        """Upload file to target Amazon Drive directory.

        Arguments:
        :param local_file (str): Full path of file to upload.
        :param target_dir (str): Full path of Amazon Drive target directory.

        :return request_result (str): Result of command execution.
        """
        with open(local_file) as f:
            filename = os.path.basename(local_file)
            target_file = target_dir + '/' + filename
            return self._perform_upload(local_file, target_dir, target_file, f.read())

    def get_json_file(self, drive_folder):
        try:
            connection = httplib.HTTPSConnection(AmazonDrive.ENDPOINT, context=ssl._create_unverified_context())
            connection.request("GET", "/view/" + drive_folder + "/values_trends.json?download=true", headers=self.headers)
            response = connection.getresponse()
            if response.status in self.HTTP_REDIRECT_CODES:
                url = response.getheader('Location')
                new_url_list = url.split('/')
                new_host = new_url_list[2]
                del new_url_list[0:3]
                new_path = '/'+"".join(new_url_list)
                connection.close()
                try:
                    connection = httplib.HTTPSConnection(new_host, context=ssl._create_unverified_context())
                    connection.request("GET", new_path)
                    response = connection.getresponse()
                    json_file = response.read()
                    connection.close()
                    return json_file
                except Exception as e:
                    logger.warning(e)
                    logger.warning('Unable to perform the get of the trends values file!')
            elif response.status in self.HTTP_NOT_FOUND_CODE:
                logger.warning('Unable to find the trends values file!')
                return False
            elif response.status in self.HTTP_BAD_REQ_CODE or response.status in self.HTTP_NOT_AUTH_CODE:
                logger.error('Unable to connect to Amazon Drive! Return code: {} {}'.format(response.status, response.reason))
                return None
        except Exception as e:
            logger.warning(e)
            logger.warning('Unable to perform the get of the trends values file!')