import os
import logging
import smtplib
import getpass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import timedelta, datetime
from email.mime.base import MIMEBase
from email import encoders

logger = logging.getLogger(__name__)

class Mailsend:

    """
    Class to build and send a capacity report email.
    We build the email header and content and send the email
    """

    _FROM_ADD = getpass.getuser()
    _SMTP_HOST = 'localhost'

    def __init__(self, to):
        """
        Initialize Object
        :param to: email address to send to
        :type to: str
        """
        self._to_mail = to
        self._outer = MIMEMultipart()
        self._inner_html = MIMEMultipart('alternative')

    def build_header(self):
        logger.info("Building the email header...")
        now_epoch = datetime.utcnow() - timedelta(hours=0)
        date_str = now_epoch.strftime('%Y-%m-%d')
        self._outer['Subject'] = "Tatool report generation"
        self._outer['From'] = self._FROM_ADD
        self._outer['To'] = self._to_mail
        self._outer.preamble = 'You will not see this in a MIME-aware mail reader.\n'
        logger.info("Completed the email header.")

    def build_content(self):
        logger.info("Build the content of the email...")
        mail_text = "Generated the Tatool file report."
        self._inner_html.attach(MIMEText(mail_text, 'html'))
        logger.info("Content built.")

    def attach_file(self, file):
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(file, "rb").read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename={}'.format(file.split("/")[-1]))
        self._outer.attach(part)

    def send_mail(self):
        logger.info("Sending email...")
        to_address_list = self._to_mail
        recipient_list = to_address_list
        self._outer.attach(self._inner_html)
        composed = self._outer.as_string()
        s = smtplib.SMTP(self._SMTP_HOST)
        s.sendmail(self._FROM_ADD, recipient_list, composed)
        s.quit()
        logger.info("Email sent!")
