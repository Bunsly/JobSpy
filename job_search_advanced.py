import csv
from jobspy import scrape_jobs
from datetime import datetime
import certifi
import time
from typing import Optional, List, Dict, Any, Union
import pandas as pd
import requests
import sys
from requests import Session

def fix_linkedin_url(url: str) -> str:
    """Fix incomplete LinkedIn URLs."""
    if not url or 'linkedin' not in url:
        return url
    
    # If URL is truncated, try to reconstruct it
    if url.startswith('https://www.linkedin') and '/jobs/view/' not in url:
        # Extract the job ID if present
        job_id = url.split('/')[-1] if url.split('/')[-1].isdigit() else None
        if job_id:
            return f"https://www.linkedin.com/jobs/view/{job_id}"
    return url

def clean_job_data(jobs_df):
    """Clean and validate job data."""
    # Fix LinkedIn URLs
    jobs_df['job_url'] = jobs_df.apply(
        lambda row: fix_linkedin_url(row['job_url']) if row['site'] == 'linkedin' else row['job_url'],
        axis=1
    )
    
    # Remove rows with missing essential data
    essential_columns = ['title', 'company', 'location', 'job_url']
    jobs_df = jobs_df.dropna(subset=essential_columns)
    
    # Clean up location data
    jobs_df['location'] = jobs_df['location'].fillna('Location not specified')
    
    # Ensure description exists
    jobs_df['description'] = jobs_df['description'].fillna('No description available')
    
    return jobs_df

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

def verify_proxy(proxy: str) -> bool:
    """Enhanced proxy verification"""
    try:
        # Check multiple IP verification services
        verification_urls = [
            'http://api.ipify.org?format=json',
            'http://ip-api.com/json',
            'http://ifconfig.me/ip'
        ]
        
        # First check real IP (only first 3 digits for security)
        real_ips = []
        for url in verification_urls:
            try:
                response = requests.get(url, timeout=5)
                if response.ok:
                    ip = response.text if 'ifconfig' in url else response.json().get('ip', response.text)
                    real_ips.append(ip)
                    break
            except:
                continue
                
        if not real_ips:
            print("Could not verify real IP")
            return False
            
        real_ip = real_ips[0]
        
        # Check with proxy
        proxies = {
            'http': proxy,
            'https': proxy
        }
        
        # Configure session to handle SSL issues
        session = requests.Session()
        session.verify = False
        requests.packages.urllib3.disable_warnings()
        
        proxy_ips = []
        for url in verification_urls:
            try:
                response = session.get(url, proxies=proxies, timeout=10)
                if response.ok:
                    ip = response.text if 'ifconfig' in url else response.json().get('ip', response.text)
                    proxy_ips.append(ip)
                    break
            except:
                continue
                
        if not proxy_ips:
            print("Could not verify proxy IP")
            return False
            
        proxy_ip = proxy_ips[0]
        
        if real_ip != proxy_ip:
            print(f"\nProxy verification successful!")
            print(f"Real IP: {real_ip[:3]}... (hidden for security)")
            print(f"Proxy IP: {proxy_ip}")
            print(f"IP Verification Service: {url}")
            return True
        else:
            print("\nWarning: Proxy not working - IPs match!")
            return False
            
    except Exception as e:
        print(f"\nProxy verification failed: {str(e)}")
        return False

def verify_proxy_usage(session: Session, url: str) -> Dict[str, Any]:
    """Verify proxy usage and return traffic stats"""
    start_size = 0
    response = session.get(url, stream=True)
    content_size = len(response.content)
    
    return {
        "status_code": response.status_code,
        "content_size": content_size,
        "headers": dict(response.headers),
        "proxy_used": bool(session.proxies)
    }

def search_tech_jobs_with_proxies() -> Optional[pd.DataFrame]:
    # Comprehensive search configuration
    search_config = {
        # Search parameters
        'search_term': 'IT Engineer',
        'location': 'Lone Tree, CO',
        'distance': 25,
        'results_wanted': 50,
        'job_type': 'fulltime',
        'hours_old': 72,
        
        # Filter settings
        'exclude_clearance': True,
        'search_sites': ["indeed", "linkedin"],
        
        # Proxy settings
        'use_proxy': True,  # Proxy kill switch
        'proxy_list': [
            "http://brd-customer-hl_92b00ed6-zone-residential_proxies_us:5t01plrkfs6y@brd.superproxy.io:33335",
            "http://brd-customer-hl_92b00ed6-zone-residential_proxy2_us:uyfjctxhc8t4@brd.superproxy.io:33335"
        ],
        
        # Clearance keywords to filter
        'clearance_keywords': [
            'clearance', 'security clearance', 'secret', 'top secret', 
            'ts/sci', 'sci', 'classified', 'poly', 'polygraph',
            'public trust', 'security+', 'security plus'
        ],
        
        # Additional settings for better results
        'max_retries_per_proxy': 2,    # Number of retries per proxy
        'verify_timeout': 15,          # Timeout for proxy verification
        'date_format': '%Y-%m-%d',     # Standardize date format
        'strict_location': True,       # Enforce stricter location filtering
        
        # Location verification
        'location_center': {
            'lat': 39.5486,  # Lone Tree coordinates
            'lon': -104.8719
        },
        'max_distance': 25,  # miles
        
        # Debug settings
        'show_filtered_jobs': False,   # Option to show filtered out jobs
        'debug_mode': False,           # Additional debugging information
        'debug': {
            'show_traffic': True,
            'log_requests': True,
            'show_proxy_usage': True
        }
    }

    max_retries = 3
    retry_count = 0

    # Proxy verification and kill switch
    if search_config['use_proxy']:
        print("\nVerifying proxy configuration...")
        proxy_verified = False
        for proxy in search_config['proxy_list']:
            if verify_proxy(proxy):
                proxy_verified = True
                break
        
        if not proxy_verified:
            print("\nNo working proxies found! Exiting for safety...")
            sys.exit(1)
    else:
        print("\nWARNING: Running without proxy! This may result in IP blocking.")
        user_input = input("Continue without proxy? (yes/no): ")
        if user_input.lower() != 'yes':
            print("Exiting...")
            sys.exit(0)

    while retry_count < max_retries:
        current_proxy = search_config['proxy_list'][retry_count % len(search_config['proxy_list'])] if search_config['use_proxy'] else None
        
        try:
            print(f"\nAttempt {retry_count + 1} of {max_retries}")
            if current_proxy:
                print(f"Using proxy: {current_proxy}")
            print(f"Searching for: {search_config['search_term']} in {search_config['location']}")
            print(f"Distance: {search_config['distance']} miles")
            print(f"Job Type: {search_config['job_type']}")
            print(f"Posts from last: {search_config['hours_old']} hours")
            print(f"Excluding clearance jobs: {search_config['exclude_clearance']}")
            print(f"Searching on: {', '.join(search_config['search_sites'])}")

            jobs = scrape_jobs(
                site_name=search_config['search_sites'],
                search_term=search_config['search_term'],
                location=search_config['location'],
                distance=search_config['distance'],
                results_wanted=search_config['results_wanted'],
                job_type=search_config['job_type'],
                hours_old=search_config['hours_old'],
                country_indeed="USA",
                description_format="markdown",
                verbose=2,
                proxy=current_proxy,
                verify=False if current_proxy else certifi.where(),  # Disable SSL verify when using proxy
            )

            if not isinstance(jobs, pd.DataFrame):
                print("Invalid response format from job search.")
                retry_count += 1
                continue

            if jobs.empty:
                print("No jobs found with current search parameters.")
                retry_count += 1
                continue
            
            print(f"\nInitial jobs found: {len(jobs)}")
            
            # Track filtered jobs
            filtered_jobs = {
                'clearance': 0,
                'location': 0,
                'date': 0
            }
            
            if search_config['exclude_clearance']:
                original_count = len(jobs)
                pattern = '|'.join(search_config['clearance_keywords'])
                clearance_mask = ~(
                    jobs['title'].str.lower().str.contains(pattern, na=False) |
                    jobs['description'].str.lower().str.contains(pattern, na=False)
                )
                filtered_jobs['clearance'] = original_count - len(jobs[clearance_mask])
                jobs = jobs[clearance_mask]
            
            # Fix date formatting
            jobs['date_posted'] = pd.to_datetime(jobs['date_posted'], errors='coerce')
            date_mask = jobs['date_posted'].notna()
            filtered_jobs['date'] = len(jobs) - len(jobs[date_mask])
            jobs = jobs[date_mask]
            
            # Location filtering
            if search_config['strict_location']:
                location_mask = jobs['location'].apply(
                    lambda x: is_within_radius(x, 
                                             search_config['location_center'],
                                             search_config['max_distance'])
                )
                filtered_jobs['location'] = len(jobs) - len(jobs[location_mask])
                jobs = jobs[location_mask]
            
            # Print filtering summary
            print("\nFiltering Summary:")
            for reason, count in filtered_jobs.items():
                if count > 0:
                    print(f"Removed {count} jobs due to {reason}")
            
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
            
            # Save to CSV
            jobs.to_csv(
                csv_filename,
                quoting=csv.QUOTE_NONNUMERIC,
                escapechar="\\",
                index=False
            )
            
            print(f"\nResults saved to: {csv_filename}")
            return jobs
            
        except Exception as e:
            print(f"\nError with proxy {current_proxy}:")
            print(f"Error details: {str(e)}")
            retry_count += 1
            
            if retry_count < max_retries:
                wait_time = 5 * (retry_count)
                print(f"\nWaiting {wait_time} seconds before trying next proxy...")
                time.sleep(wait_time)
            else:
                print("\nAll attempts failed. Please try again later.")

    return None

def calculate_distance(job_location, search_location):
    """
    Placeholder for distance calculation.
    In a full implementation, this would use geocoding and actual distance calculation.
    """
    return "Unknown"  # Would need geocoding API to calculate actual distances

def is_within_radius(job_location: str, center: dict, max_distance: int) -> bool:
    """Verify if job location is within specified radius"""
    try:
        # Add geocoding logic here if needed
        return True  # Placeholder for now
    except Exception:
        return False

if __name__ == "__main__":
    print("Starting job search...")
    jobs = search_tech_jobs_with_proxies()
    
    if jobs is not None and not jobs.empty:
        print("\nSearch completed successfully!")
        print(f"Total jobs found: {len(jobs)}")
        print("\nJobs by source:")
        print(jobs['site'].value_counts())
    else:
        print("\nNo results found. Try adjusting search parameters.")
