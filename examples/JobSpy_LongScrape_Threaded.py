import concurrent.futures
import time
from jobspy import scrape_jobs
import pandas as pd

def scrape_and_append_threaded(offset, results_in_segment, all_jobs):
    try:
        print(f"Scraping jobs from offset {offset}")
        jobs = scrape_jobs(
            site_name=["indeed"],
            search_term="software engineer",
            location="Los Angeles, CA",
            results_wanted=results_in_segment,
            country_indeed="USA",
            offset=offset,
        )

        all_jobs.extend(jobs.to_dict("records"))
        print(f"Scraped {len(jobs)} jobs from offset {offset}")

    except Exception as e:
        print(f"Error at offset {offset}: {e}")

def main():
    results_wanted = 500
    results_in_each_iteration = 100
    offset = 0
    all_jobs = []
    segments = results_wanted//results_in_each_iteration

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for i in range(segments):
            offset = i * results_in_each_iteration
            futures.append(executor.submit(scrape_and_append_threaded, offset, results_in_each_iteration, all_jobs))

        for future in concurrent.futures.as_completed(futures):
            error = future.exception()
            if error:
                print(f"Error: {error}")

        # delay to avoid rate limiting
        time.sleep(2)

    # DataFrame from the collected job data
    jobs_df = pd.DataFrame(all_jobs)

    # Formatting
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    pd.set_option("display.width", None)
    pd.set_option("display.max_colwidth", 50)

    print(jobs_df)

    # Output to CSV
    csv_filename = "jobs.csv"
    jobs_df.to_csv(csv_filename, index=False)
    print(f"Outputted to {csv_filename}")

if __name__ == "__main__":
    main()
