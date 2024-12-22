from datetime import datetime
import json

from jobspy.jobs import JobPost, Location
from jobspy.scrapers.goozali.model import GoozaliColumnTypeOptions, GoozaliResponse, GoozaliRow
from jobspy.scrapers.goozali.model.GoozaliColumn import GoozaliColumn
from jobspy.scrapers.goozali.model.GoozaliColumnChoice import GoozaliColumnChoice
from jobspy.scrapers.goozali.model.GozaaliResponseData import GoozaliResponseData
from .constants import job_post_column_to_goozali_column, job_post_column_names

# Mapping function to convert parsed dictionary into GoozaliResponseData


class GoozaliMapper:
    def _map_dict_to_goozali_response_column_choice(self, column_choices: dict) -> dict[str, GoozaliColumnChoice]:
        # Create a dictionary to store GoozaliColumnChoice objects
        goolzali_column_choices: dict[str, GoozaliColumnChoice] = {}

        # Map the data to GoozaliColumnChoice instances
        for key, value in column_choices.items():
            goolzali_column_choices[key] = GoozaliColumnChoice(
                id=value['id'],
                name=value['name'],
                # Using get to safely access 'color', it may not always be present
                color=value.get('color', "")
            )

        return goolzali_column_choices

    def _map_dict_to_goozali_response_column_type_option(self, type_options: dict) -> GoozaliColumnTypeOptions:
        goozali_type_options = GoozaliColumnTypeOptions(
            typeOptions=type_options)
        if goozali_type_options.choices:
            goozali_type_options.choices = self._map_dict_to_goozali_response_column_choice(
                goozali_type_options.choices)

        return goozali_type_options

    def _map_dict_to_goozali_response_columns(self, columns: list) -> list[GoozaliColumn]:
        goozali_columns: list[GoozaliColumn] = []
        for column in columns:
            goozali_column = GoozaliColumn(**column)
            if goozali_column.typeOptions:
                goozali_column.typeOptions = self._map_dict_to_goozali_response_column_type_option(
                    goozali_column.typeOptions)
            goozali_columns.append(goozali_column)

        return goozali_columns

    def _map_dict_to_goozali_response_data(self, data: dict) -> GoozaliResponseData:

        columns = self._map_dict_to_goozali_response_columns(data['columns'])
        rows = [GoozaliRow(**row) for row in data['rows']]

        return GoozaliResponseData(
            applicationId=data['applicationId'],
            id=data['id'],
            name=data['name'],
            columns=columns,
            primaryColumnId=data['primaryColumnId'],
            meaningfulColumnOrder=data['meaningfulColumnOrder'],
            viewOrder=data['viewOrder'],
            rows=rows
        )

    # Updated map response function

    def map_response_to_goozali_response(self, response) -> GoozaliResponse:
        # Check the response content (this is a bytes object)
        response_content = response.content
        # Decode the byte content to a string
        decoded_content = response_content.decode('utf-8')
        # Now you can parse the decoded content as JSON
        data = json.loads(decoded_content)

        # Convert the 'data' dictionary into GoozaliResponseData object
        data_obj = self._map_dict_to_goozali_response_data(data['data'])

        # Return a new GoozaliResponse with msg and the converted data
        return GoozaliResponse(msg=data['msg'], data=data_obj)

    def get_value_by_job_post_Id(self, job_post_column: str, row: GoozaliRow, dict_column_name_to_column: dict[str, GoozaliColumn]):
        goozali_column_name = job_post_column_to_goozali_column[job_post_column]
        column = dict_column_name_to_column[goozali_column_name]
        value = row.cellValuesByColumnId[column.id]
        if (job_post_column == "location"):
            location = Location(text="Not Found")
            if type(value) is list:
                location_text = column.typeOptions.choices[value[0]].name
                location.text = location_text

            return location
        if (job_post_column == "company_industry"):
            if type(value) is list:
                value = column.typeOptions.choices[value[0]].name

        if (job_post_column == "date_posted"):
            return datetime.fromisoformat(value.replace("Z", "")).date()

        if (job_post_column == "field"):
            value = column.typeOptions.choices[value].name

        return str(value)

    def map_goozali_response_to_job_post(self, row: GoozaliRow, dict_column_name_to_column: dict[str, GoozaliColumn]) -> JobPost:
        temp = {}
        for col in job_post_column_names:
            value = self.get_value_by_job_post_Id(
                col, row, dict_column_name_to_column)
            temp[col] = value

        return JobPost.model_validate(temp)
