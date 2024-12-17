import json
import os
from jobspy import scrape_jobs
import pandas as pd

from jobspy.scrapers.goozali.GoozaliMapper import GoozaliMapper
from jobspy.scrapers.goozali.GoozaliScrapperComponent import GoozaliScrapperComponent
from jobspy.scrapers.goozali.model.GozaaliResponseData import GoozaliResponseData
# URL Example
# https://airtable.com/v0.3/view/viwagEIbkfz2iMsLU/readSharedViewData?stringifiedObjectParams=%7B%22shouldUseNestedResponseFormat%22%3Atrue%7D&requestId=reqXyRSHWlXyiRgY9&accessPolicy=%7B%22allowedActions%22%3A%5B%7B%22modelClassName%22%3A%22view%22%2C%22modelIdSelector%22%3A%22viwagEIbkfz2iMsLU%22%2C%22action%22%3A%22readSharedViewData%22%7D%2C%7B%22modelClassName%22%3A%22view%22%2C%22modelIdSelector%22%3A%22viwagEIbkfz2iMsLU%22%2C%22action%22%3A%22getMetadataForPrinting%22%7D%2C%7B%22modelClassName%22%3A%22view%22%2C%22modelIdSelector%22%3A%22viwagEIbkfz2iMsLU%22%2C%22action%22%3A%22readSignedAttachmentUrls%22%7D%2C%7B%22modelClassName%22%3A%22row%22%2C%22modelIdSelector%22%3A%22rows%20*%5BdisplayedInView%3DviwagEIbkfz2iMsLU%5D%22%2C%22action%22%3A%22createDocumentPreviewSession%22%7D%5D%2C%22shareId%22%3A%22shr97tl6luEk4Ca9R%22%2C%22applicationId%22%3A%22app5sYJyDgcRbJWYU%22%2C%22generationNumber%22%3A0%2C%22expires%22%3A%222025-01-02T00%3A00%3A00.000Z%22%2C%22signature%22%3A%223aa292ee44d15aa75d9506200329e413653471f89e000fa370ef9fa38393070a%22%7D


try:
    current_directory = os.getcwd()
    file_path = os.path.join(current_directory, 'src',
                             'tests', 'goozali_response_example.json')
    with open(file_path, 'r', encoding='ISO-8859-1') as file:
        test_json_response = json.load(file)
    print(test_json_response['msg'])  # Output: Success
    mapper = GoozaliMapper()
    response_data: GoozaliResponseData = mapper._map_dict_to_goozali_response_data(
        test_json_response['data'])
    print("ya gever!!")

    component = GoozaliScrapperComponent()
    hours_old = 200
    column = component.find_column(response_data.columns, "Field")
    column_choice = component.find_choice_from_column(
        column, "Software Engineering")

    filtered_rows_by_column_choice = component.filter_rows_by_column_choice(
        response_data.rows, column, column_choice)
    filtered_rows_by_age_and_column_choice = component.filter_rows_by_hours(
        filtered_rows_by_column_choice, hours_old)

    filtered_rows_by_age_and_column_choice
except FileNotFoundError:
    print("The file was not found.")
except json.JSONDecodeError:
    print("There was an error decoding the JSON data.")
except UnicodeDecodeError as e:
    print(f"Unicode decode error: {e}")
