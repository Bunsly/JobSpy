import json
import os

from jobspy import scrape_jobs
import pandas as pd


# load location list
def read_location_list(location_file):
    with open(location_file) as f:
        location_list = [location['name'] for location in json.load(f)]
        return location_list


# formatting for pandas
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', 50)  # set to 0 to see full job url / desc

# fetch jobs for each location
# locations = read_location_list('location_seed.json')
# for location in locations:
#     try:
#         jobs: pd.DataFrame = scrape_jobs(
#             # site_name=["indeed", "linkedin", "zip_recruiter"],
#             site_name=["indeed"],
#             search_term="software engineer",
#             location=location,
#             results_wanted=30,
#             # be wary the higher it is, the more likey you'll get blocked (rotating proxy should work tho)
#             country_indeed='USA',
#             # offset=25  # start jobs from an offset (use if search failed and want to continue)
#             proxy="http://34.120.172.140:8123",
#             # proxy="http://crawler-gost-proxy.jobright-internal.com:8080",
#         )
#     except Exception as e:
#         print(f'Error when process: {location}')
#         print(e)
#         continue
#     print(f'{location}: {jobs.shape[0]} rows append.')
#     if os.path.isfile('./jobs.csv'):
#         jobs.to_csv('./jobs.csv', index=False, mode='a', header=False)
#     else:
#         jobs.to_csv('./jobs.csv', index=False, mode='a', header=True)
