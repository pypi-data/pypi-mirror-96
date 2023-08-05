# Copyright 2019-2021 Siemens AG
# SPDX-License-Identifier: MIT

import logging
import re
import time
from typing import Tuple

from tenacity import TryAgain, retry, retry_if_exception_type, stop_after_attempt

from fossology.exceptions import AuthorizationError, FossologyApiError
from fossology.obj import ReportFormat, Upload, get_options

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Report:
    """Class dedicated to all "report" related endpoints"""

    @retry(retry=retry_if_exception_type(TryAgain), stop=stop_after_attempt(3))
    def generate_report(
        self, upload: Upload, report_format: ReportFormat = None, group: str = None
    ):
        """Generate a report for a given upload

        API Endpoint: GET /report

        :param upload: the upload which report will be generated
        :param format: the report format (default: ReportFormat.READMEOSS)
        :param group: the group name to choose while generating the report (default: None)
        :type upload: Upload
        :type format: ReportFormat
        :type group: string
        :return: the report id
        :rtype: int
        :raises FossologyApiError: if the REST call failed
        :raises AuthorizationError: if the user can't access the group
        """
        headers = {"uploadId": str(upload.id)}
        if report_format:
            headers["reportFormat"] = report_format.value
        else:
            headers["reportFormat"] = "readmeoss"
        if group:
            headers["groupName"] = group

        response = self.session.get(f"{self.api}/report", headers=headers)

        if response.status_code == 201:
            report_id = re.search("[0-9]*$", response.json()["message"])
            return report_id[0]

        elif response.status_code == 403:
            description = f"Generating report for upload {upload.id} {get_options(group)}not authorized"
            raise AuthorizationError(description, response)

        elif response.status_code == 503:
            wait_time = response.headers["Retry-After"]
            logger.debug(f"Retry generate report after {wait_time} seconds")
            time.sleep(int(wait_time))
            raise TryAgain

        else:
            description = f"Report generation for upload {upload.uploadname} failed"
            raise FossologyApiError(description, response)

    @retry(retry=retry_if_exception_type(TryAgain), stop=stop_after_attempt(3))
    def download_report(self, report_id: int, group: str = None) -> Tuple[str, str]:
        """Download a report

        API Endpoint: GET /report/{id}

        :Example:

        >>> from fossology.api import Fossology
        >>>
        >>> foss = Fossology(FOSS_URL, FOSS_TOKEN, username)
        >>>
        >>> # Generate a report for upload 1
        >>> report_id = foss.generate_report(foss.detail_upload(1))
        >>> report_content, report_name = foss.download_report(report_id)
        >>> with open(report_name, "wb") as report_file:
        >>>     report_file.write(report_content)

        :param report_id: the id of the generated report
        :param group: the group name to choose while downloading a specific report (default: None)
        :type report_id: int
        :type group: string
        :return: the report content and the report name
        :rtype: Tuple[str, str]
        :raises FossologyApiError: if the REST call failed
        :raises AuthorizationError: if the user can't access the group
        :raises TryAgain: if the report generation timed out after 3 retries
        """
        headers = dict()
        if group:
            headers["groupName"] = group

        response = self.session.get(f"{self.api}/report/{report_id}", headers=headers)
        if response.status_code == 200:
            content = response.headers["Content-Disposition"]
            report_name_pattern = '(^attachment; filename=")(.*)("$)'
            report_name = re.match(report_name_pattern, content).group(2)
            return response.content, report_name
        elif response.status_code == 403:
            description = (
                f"Getting report {report_id} {get_options(group)}not authorized"
            )
            raise AuthorizationError(description, response)
        elif response.status_code == 503:
            wait_time = response.headers["Retry-After"]
            logger.debug(f"Retry get report after {wait_time} seconds")
            time.sleep(int(wait_time))
            raise TryAgain
        else:
            description = f"Download of report {report_id} failed"
            raise FossologyApiError(description, response)
