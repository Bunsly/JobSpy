from jobspy import scrape_jobs
import time
import certifi
import pandas as pd
import csv
from datetime import datetime
from typing import Optional, List

def filter_clearance_jobs(df: pd.DataFrame) -> pd.DataFrame:
    """Filter out jobs requiring security clearance"""
    clearance_keywords = [
        'clearance', 'security clearance', 'secret', 'top secret', 
        'ts/sci', 'sci', 'classified', 'poly', 'polygraph',
        'public trust', 'security+', 'security plus'
    ]
    
    # Create a pattern matching any clearance keyword
    pattern = '|'.join(clearance_keywords)
    
    # Filter out jobs where title or description contains clearance keywords
    mask = ~(
        df['title'].str.lower().str.contains(pattern, na=False) |
        df['description'].str.lower().str.contains(pattern, na=False)
    )
    
    return df[mask]

def search_tech_jobs(
    search_sites: List[str] = ["indeed", "linkedin"],
    exclude_clearance: bool = False
) -> Optional[pd.DataFrame]:
    
    # Search configuration
    search_config = {
        'search_term': 'IT Engineer',
        'location': 'Lone Tree, CO',
        'distance': 25,
        'results_wanted': 50,
        'job_type': 'fulltime',
        'hours_old': 72
    }

    try:
        print(f"Searching for: {search_config['search_term']} in {search_config['location']}")
        print(f"Distance: {search_config['distance']} miles")
        print(f"Job Type: {search_config['job_type']}")
        print(f"Posts from last: {search_config['hours_old']} hours")
        print(f"Excluding clearance jobs: {exclude_clearance}")
        print(f"Searching on: {', '.join(search_sites)}")

        jobs = scrape_jobs(
            site_name=search_sites,
            search_term=search_config['search_term'],
            location=search_config['location'],
            distance=search_config['distance'],
            results_wanted=search_config['results_wanted'],
            job_type=search_config['job_type'],
            hours_old=search_config['hours_old'],
            country_indeed="USA",
            description_format="markdown",
            verbose=2
        )

        if isinstance(jobs, pd.DataFrame) and not jobs.empty:
            print(f"\nInitial jobs found: {len(jobs)}")
            
            if exclude_clearance:
                original_count = len(jobs)
                jobs = filter_clearance_jobs(jobs)
                filtered_count = len(jobs)
                print(f"Removed {original_count - filtered_count} jobs requiring clearance")
            
            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"it_jobs_{timestamp}.csv"
            
            # Print job summary
            print("\nJob Listings Found:")
            print("-------------------")
            for idx, job in jobs.iterrows():
                print(f"\n{idx + 1}. {job.get('title', 'No title')}")
                print(f"   Company: {job.get('company', 'No company')}")
                print(f"   Location: {job.get('location', 'No location')}")
                print(f"   Source: {job.get('site', 'No source')}")
                print(f"   Date Posted: {job.get('date_posted', 'No date')}")
            
            jobs.to_csv(csv_filename, index=False)
            print(f"\nResults saved to: {csv_filename}")
            return jobs
            
        print("No jobs found with current search parameters.")
        return None

    except Exception as e:
        print(f"\nError during search:")
        print(f"Error details: {str(e)}")
        return None

if __name__ == "__main__":
    print("Starting job search...")
    jobs = search_tech_jobs(exclude_clearance=True)
    
    if jobs is not None and not jobs.empty:
        print("\nSearch completed successfully!")
        print(f"Total jobs found: {len(jobs)}")
        print("\nJobs by source:")
        print(jobs['site'].value_counts())
    else:
        print("\nNo results found. Try adjusting search parameters.")