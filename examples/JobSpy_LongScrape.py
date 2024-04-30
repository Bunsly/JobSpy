from jobspy import scrape_jobs
import pandas as pd
import os
import time

# creates csv a new filename if the jobs.csv already exists.
csv_filename = "jobs.csv"
counter = 1
while os.path.exists(csv_filename):
    csv_filename = f"jobs_{counter}.csv"
    counter += 1

# results wanted and offset
results_wanted = 1000
offset = 0

all_jobs = []

# max retries
max_retries = 3

# nuumber of results at each iteration
results_in_each_iteration = 30

while len(all_jobs) < results_wanted:
    retry_count = 0
    while retry_count < max_retries:
        print("Doing from", offset, "to", offset + results_in_each_iteration, "jobs")
        try:
            jobs = scrape_jobs(
                site_name=["indeed"],
                search_term="software engineer",
                # New York, NY
                # Dallas, TX
                # Los Angeles, CA
                location="Los Angeles, CA",
                results_wanted=min(
                    results_in_each_iteration, results_wanted - len(all_jobs)
                ),
                country_indeed="USA",
                offset=offset,
                # proxy="http://jobspy:5a4vpWtj8EeJ2hoYzk@ca.smartproxy.com:20001",
            )

            # Add the scraped jobs to the list
            all_jobs.extend(jobs.to_dict("records"))

            # Increment the offset for the next page of results
            offset += results_in_each_iteration

            # Add a delay to avoid rate limiting (you can adjust the delay time as needed)
            print(f"Scraped {len(all_jobs)} jobs")
            print("Sleeping secs", 100 * (retry_count + 1))
            time.sleep(100 * (retry_count + 1))  # Sleep for 2 seconds between requests

            break  # Break out of the retry loop if successful
        except Exception as e:
            print(f"Error: {e}")
            retry_count += 1
            print("Sleeping secs before retry", 100 * (retry_count + 1))
            time.sleep(100 * (retry_count + 1))
            if retry_count >= max_retries:
                print("Max retries reached. Exiting.")
                break

# DataFrame from the collected job data
jobs_df = pd.DataFrame(all_jobs)

# Formatting
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", 50)

print(jobs_df)

jobs_df.to_csv(csv_filename, index=False)
print(f"Outputted to {csv_filename}")
