from jobspy import scrape_jobs
import pandas as pd

from jobspy.scrapers.goozali.model import GoozaliColumnTypeOptions, GoozaliResponse, GoozaliTable
from jobspy.scrapers.goozali.model.GoozaliColumn import GoozaliColumn
from jobspy.scrapers.goozali.model.GoozaliColumnChoice import GoozaliColumnChoice
from jobspy.scrapers.goozali.model.GoozaliRow import GoozaliRow
from jobspy.scrapers.goozali.model.GozaaliResponseData import GoozaliResponseData

# URL Example
# https://airtable.com/v0.3/view/viwagEIbkfz2iMsLU/readSharedViewData?stringifiedObjectParams=%7B%22shouldUseNestedResponseFormat%22%3Atrue%7D&requestId=reqXyRSHWlXyiRgY9&accessPolicy=%7B%22allowedActions%22%3A%5B%7B%22modelClassName%22%3A%22view%22%2C%22modelIdSelector%22%3A%22viwagEIbkfz2iMsLU%22%2C%22action%22%3A%22readSharedViewData%22%7D%2C%7B%22modelClassName%22%3A%22view%22%2C%22modelIdSelector%22%3A%22viwagEIbkfz2iMsLU%22%2C%22action%22%3A%22getMetadataForPrinting%22%7D%2C%7B%22modelClassName%22%3A%22view%22%2C%22modelIdSelector%22%3A%22viwagEIbkfz2iMsLU%22%2C%22action%22%3A%22readSignedAttachmentUrls%22%7D%2C%7B%22modelClassName%22%3A%22row%22%2C%22modelIdSelector%22%3A%22rows%20*%5BdisplayedInView%3DviwagEIbkfz2iMsLU%5D%22%2C%22action%22%3A%22createDocumentPreviewSession%22%7D%5D%2C%22shareId%22%3A%22shr97tl6luEk4Ca9R%22%2C%22applicationId%22%3A%22app5sYJyDgcRbJWYU%22%2C%22generationNumber%22%3A0%2C%22expires%22%3A%222025-01-02T00%3A00%3A00.000Z%22%2C%22signature%22%3A%223aa292ee44d15aa75d9506200329e413653471f89e000fa370ef9fa38393070a%22%7D


def test_goozali():
    result = scrape_jobs(
        site_name="glassdoor",
        search_term="engineer",
        results_wanted=5,
    )
    assert (
        isinstance(result, pd.DataFrame) and len(result) == 5
    ), "Result should be a non-empty DataFrame"


def createMockGoozaliResponse() -> GoozaliResponse:
    data = GoozaliResponseData(table=GoozaliTable(
        applicationId="app7OQjqEzTtCRq7u",
        id="tblBQjp5Aw6O172VY",
        name="Shared view table",
        columns=[
            GoozaliColumn(
                id="fldIf9DbRpNRLJXuD",
                name="Industry",
                description=None,
                type="multiSelect",
                typeOptions=GoozaliColumnTypeOptions(
                    choiceOrder=["selcE6QUv4vWIIcZR",
                                 "sel0JIQKMmz3jCFUN", "selzhpwlfPssG4OEx"],
                    choices={
                        "selwhDNBom2dZJkgv": GoozaliColumnChoice(id="selwhDNBom2dZJkgv", name="HealthTech", color="orange"),
                        "selReHesNOVD3PvCo": GoozaliColumnChoice(id="selReHesNOVD3PvCo", name="Automotive", color="pink")
                    },
                    disableColors=False
                ),
                default=None,
                initialCreatedTime="2022-12-29T10:23:21.000Z",
                initialCreatedByUserId="usr1fVy2RIyCuGHec",
                lastModifiedTime="2024-07-21T09:30:02.000Z",
                lastModifiedByUserId="usr1fVy2RIyCuGHec",
                isEditableFromSync=False
            )
        ],
        primaryColumnId="fldLT11B0cpV6p9Uz",
        meaningfulColumnOrder=[
            {"columnId": "fldLT11B0cpV6p9Uz", "visibility": True},
            {"columnId": "fldIf9DbRpNRLJXuD", "visibility": True, "width": 368},
            {"columnId": "fldOLt34j8Pm2dcCq", "visibility": True, "width": 182}
        ],
        viewOrder=["viwNRSqqmqZLP0a3C"],
        rows=[
            GoozaliRow(
                id="recwiKgHT9mJrqoxa",
                createdTime="2023-01-09T10:32:09.000Z",
                cellValuesByColumnId={
                    "fldLT11B0cpV6p9Uz": ["3M"],
                    "fldIf9DbRpNRLJXuD": ["selwhDNBom2dZJkgv", "selReHesNOVD3PvCo"]
                }
            )
        ]
    ))
    return GoozaliResponse(msg="SUCCESS", data=data)
