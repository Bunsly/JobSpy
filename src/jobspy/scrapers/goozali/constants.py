import json


view_ids = ["viwIOzPYaUGxlA0Jd"]

headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9,he-IL;q=0.8,he;q=0.7',
    'priority': 'u=1, i',
    'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'x-airtable-accept-msgpack': 'true',
    'x-airtable-application-id': 'appwewqLk7iUY4azc',
    'x-airtable-inter-service-client': 'webClient',
    'x-airtable-page-load-id': 'pglqAAzFDZEWCEC7s',
    'x-early-prefetch': 'true',
    'x-requested-with': 'XMLHttpRequest',
    'x-time-zone': 'Asia/Jerusalem',
    'x-user-locale': 'en'
}

session_id = "lWt/xRLIQas/blkys/2YBYl0priNI7gv85sXXtmkrW+TzbLHR8Vm6iY5RDialmLUYsQgLab8uWZyahWRw0HizxdOXhJxd5FB66H85GpUAX8zZbAZPZdUHvzxjaVa130w14QSXDa8OmsNlpKtiUtZ/DXMTOZ1wYDWC4tVJTKJ171wyKA7C9E="

cookies = {}

request_id = "req4q4tKw3woEEWxw&"
share_id = "shrQBuWjXd0YgPqV6"
application_id = "appwewqLk7iUY4azc"
signature = "be8bd40c133f051f929ebab311c416013f5af0d5acae4264575b88ccf051ee59"


def get_access_policy(view_id: str) -> dict[str, str]:
    access_policy = {
        "allowedActions": [
            {"modelClassName": "view", "modelIdSelector": view_id,
                "action": "readSharedViewData"},
            {"modelClassName": "view", "modelIdSelector": view_id,
                "action": "getMetadataForPrinting"},
            {"modelClassName": "view", "modelIdSelector": view_id,
                "action": "readSignedAttachmentUrls"},
            {"modelClassName": "row", "modelIdSelector": f"rows *[displayedInView={view_id}]",
             "action": "createDocumentPreviewSession"}
        ],
        "shareId": share_id,
        "applicationId": application_id,
        "generationNumber": 0,
        "expires": "2025-01-02T00:00:00.000Z",
        "signature": signature
    }
    # Convert to a JSON string
    return json.dumps(access_policy)


stringifiedObjectParams = {"shouldUseNestedResponseFormat": "true"}
