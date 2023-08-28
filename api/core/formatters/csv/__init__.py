import gspread
from oauth2client.service_account import ServiceAccountCredentials

import csv
from io import StringIO
from datetime import datetime

from ...jobs import *
from ...scrapers import *
from settings import *


class CSVFormatter:
    @staticmethod
    def upload_to_google_sheet(csv_data: str):
        try:
            scope = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive.file",
                "https://www.googleapis.com/auth/drive",
            ]
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                "client_secret.json", scope
            )
            gc = gspread.authorize(credentials)
            sh = gc.open(GSHEET_NAME)

            worksheet = sh.get_worksheet(0)
            data_string = csv_data.getvalue()
            reader = csv.reader(StringIO(data_string))

            rows = list(reader)

            for i, row in enumerate(rows):
                if i == 0:
                    continue
                worksheet.append_row(row)
        except Exception as e:
            raise e

    @staticmethod
    def generate_filename() -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"JobSpy_results_{timestamp}.csv"

    @staticmethod
    def generate_filename() -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"JobSpy_results_{timestamp}.csv"

    @staticmethod
    def format(jobs: CommonResponse) -> StringIO:
        """
        Transfomr the jobs objects into csv
        :param jobs:
        :return: csv
        """
        output = StringIO()
        writer = csv.writer(output)

        headers = [
            "Site",
            "Title",
            "Company Name",
            "Job URL",
            "Country",
            "City",
            "State",
            "Job Type",
            "Compensation Interval",
            "Min Amount",
            "Max Amount",
            "Currency",
            "Date Posted",
            "Description",
        ]
        writer.writerow(headers)

        for site, job_response in jobs.dict().items():
            if isinstance(job_response, dict) and job_response.get("success"):
                for job in job_response["jobs"]:
                    writer.writerow(
                        [
                            site,
                            job["title"],
                            job["company_name"],
                            job["job_url"],
                            job["location"]["country"],
                            job["location"]["city"],
                            job["location"]["state"],
                            job["job_type"].value if job.get("job_type") else "",
                            job["compensation"]["interval"].value
                            if job["compensation"]
                            else "",
                            job["compensation"]["min_amount"]
                            if job["compensation"]
                            else "",
                            job["compensation"]["max_amount"]
                            if job["compensation"]
                            else "",
                            job["compensation"]["currency"]
                            if job["compensation"]
                            else "",
                            job.get("date_posted", ""),
                            job["description"],
                        ]
                    )

        output.seek(0)
        return output
