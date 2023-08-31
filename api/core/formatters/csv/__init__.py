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
    def fetch_job_urls(credentials: Any) -> set:
        """
        Fetches all the job urls from the google sheet to prevent duplicates
        :param credentials:
        :return: urls
        """
        try:
            gc = gspread.authorize(credentials)
            sh = gc.open(GSHEET_NAME)

            worksheet = sh.get_worksheet(0)
            data = worksheet.get_all_values()
            job_urls = set()
            for row in data[1:]:
                job_urls.add(row[3])
            return job_urls
        except Exception as e:
            raise e

    @staticmethod
    def upload_to_google_sheet(csv_data: str):
        """
        Appends rows to google sheet
        :param csv_data:
        :return:
        """
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

            job_urls = CSVFormatter.fetch_job_urls(credentials)

            rows = list(reader)

            for i, row in enumerate(rows):
                if i == 0:
                    continue
                if row[4] in job_urls:
                    continue

                row[6] = format(int(row[6]), ",d") if row[6] else ""
                row[7] = format(int(row[7]), ",d") if row[7] else ""
                worksheet.append_row(row)
        except Exception as e:
            raise e

    @staticmethod
    def generate_filename() -> str:
        """
        Adds a timestamp to the filename header
        :return: filename
        """
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
            "Title",
            "Company Name",
            "City",
            "State",
            "Job Type",
            "Pay Cycle",
            "Min Amount",
            "Max Amount",
            "Date Posted",
            "Description",
            "Job URL",
        ]
        writer.writerow(headers)

        for site, job_response in jobs.dict().items():
            if isinstance(job_response, dict) and job_response.get("success"):
                for job in job_response["jobs"]:
                    writer.writerow(
                        [
                            job["title"],
                            job["company_name"],
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
                            job.get("date_posted", ""),
                            job["description"],
                            job["job_url"],
                        ]
                    )

        output.seek(0)
        return output
