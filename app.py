from flask import Flask, jsonify, request
import sys
import os
import json

# Initialize the Flask application
app = Flask(__name__)

# Get the absolute path of the src directory
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src'))

import csv
# Add src to the system path
if src_path not in sys.path:
    sys.path.append(src_path)

from jobspy import scrape_jobs

@app.route('/Recommend_jobs', methods=['GET'])
def get_jobs():
    # Get parameters from the request
    site_name = request.args.getlist('site_name') or ["indeed"]
    search_term = request.args.get('search_term') or "software engineer"
    location = request.args.get('location') or "Dallas, TX"
    results_wanted = int(request.args.get('results_wanted', 3))
    hours_old = int(request.args.get('hours_old', 72))
    country_indeed = request.args.get('country_indeed') or 'USA'

    # Scrape the job data
    jobs = scrape_jobs(
        site_name=site_name,
        search_term=search_term,
        location=location,
        results_wanted=results_wanted,
        hours_old=hours_old,
        country_indeed=country_indeed
    )

    # Convert jobs to a list of dictionaries
    jobs_dict_list = jobs.to_dict(orient='records')

    # Return the JSON response
    return jsonify(jobs_dict_list)

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True)
