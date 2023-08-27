import csv
from io import StringIO
from datetime import datetime

from ...jobs import *
from ...scrapers import *


def generate_filename() -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"JobSpy_results_{timestamp}.csv"


class CSVFormatter:
    @staticmethod
    def format(jobs: ScraperResponse) -> StringIO:
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
            if job_response and job_response.get("success"):
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
