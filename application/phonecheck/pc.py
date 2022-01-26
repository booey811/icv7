import os, subprocess

import pydf
import requests
import json

from . import config


class PhonecheckManager:
    """Object that will manage interactions with the Phonecheck database"""

    DEFECTS_DICT = config.standard_checks

    def __init__(self):
        self.api_key = os.environ['PHONECHECK']
        self.headers = {
            'content-type': 'multipart/form-data'
        }
        # self.pdf = PDFCreator()

    def get_info(self, imei: str):
        """Fetches all transactions related to a given IMEI"""
        url = 'https://clientapiv2.phonecheck.com/cloud/cloudDB/GetDeviceInfo'
        data = {
            'apiKey': (None, self.api_key),
            'user_name': (None, 'icorrect4'),
            'imei': (None, imei)
        }
        response = requests.request(method='POST', url=url, files=data)

        if response.status_code == 200:
            # Success, return report info
            return json.loads(response.text)
        elif response.status_code == 404:
            # No reports found with the given IMEI
            raise CannotFindReportThroughIMEI()
        else:
            # Unknown error
            raise Exception('Get Phonecheck Info raised an unknown error')

    def get_certificate(self, report_id: str):
        """Retrieves the A4 report with a given ID (taken from Phonecheck.get_info()) in HTML format"""
        url = 'https://clientapiv2.phonecheck.com/cloud/cloudDB/A4Report'
        data = {
            'apiKey': (None, self.api_key),
            'username': (None, 'icorrect4'),
            'report_id': (None, report_id)
        }

        response = requests.request(method='POST', url=url, files=data)

        if response.status_code == 200:
            # Report fetch complete
            return response.text
        else:
            # Unknown Error
            raise Exception(f'Phonecheck.get_certificate returned an invalid response: '
                            f'{response.status_code}: {response.text})')

    # def convert_to_pdf(self, html_string, report_id):
    #     pdf = self.pdf.make_pdf(html_string)
    #     with open(f'tmp/pc_reports/report-{report_id}.pdf', 'wb') as f:
    #         f.write(pdf)
    #     return f'tmp/pc_reports/report-{report_id}.pdf'

    @staticmethod
    def new_convert_to_pdf(html_string, report_id):
        if os.environ["ENV"] == "devlocal":
            # Cannot create PDFs locally (whktopdf package is fiddly)
            return False
        pdf = pydf.generate_pdf(html_string)
        with open(f'tmp/pc_reports/report-{report_id}.pdf', 'wb') as f:
            f.write(pdf)
        return f'tmp/pc_reports/report-{report_id}.pdf'


class CannotFindReportThroughIMEI(Exception):
    def __init__(self):
        pass


phonecheck = PhonecheckManager()
