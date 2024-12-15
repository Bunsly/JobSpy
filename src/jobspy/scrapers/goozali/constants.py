view_ids = ["viwIOzPYaUGxlA0Jd"]

headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9,he-IL;q=0.8,he;q=0.7",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "x-airtable-accept-msgpack": "true",
    "x-airtable-application-id": "appwewqLk7iUY4azc",
    "x-requested-with": "XMLHttpRequest"
}

session_id = "lWt/xRLIQas/blkys/2YBYl0priNI7gv85sXXtmkrW+TzbLHR8Vm6iY5RDialmLUYsQgLab8uWZyahWRw0HizxdOXhJxd5FB66H85GpUAX8zZbAZPZdUHvzxjaVa130w14QSXDa8OmsNlpKtiUtZ/DXMTOZ1wYDWC4tVJTKJ171wyKA7C9E="

cookies = {
    "__Host-airtable-session": "eyJzZXNzaW9uSWQiOiJzZXNxdFV4bVdKRVRoVGtRMiIsImNzcmZTZWNyZXQiOiIyT0JrVTJkU2I4bDA3NFZIRmd6eTdjTHUifQ==",
    "__Host-airtable-session.sig": "heWRrVH73Aa-2ALrH4c_CbvQqTNbNRv9VjPZYv3aHJ4",
    "brw": "brwtN7N3OgPFrtfb2",
    "brwConsent": "opt-in",
    "acq": "eyJhY3F1aXNpdGlvbiI6Ilt7XCJwbGF0Zm9ybVwiOlwiZGVza3RvcFwiLFwib3JpZ2luXCI6XCJsb2dpblwiLFwidG91Y2hUaW1lXCI6XCIyMDI0LTEyLTEyVDE3OjU1OjQyLjU3OVpcIn1dIn0=",
    "acq.sig": "5xrqXjip4IJZxIeSPCkajWt_wlBmGw-k7HJCj8wicxU",
    "AWSALBTGCORS": "YoIaU+wibkMfutpYUIlGnvYmnUa0VjM2ukwIhESaxfQUNL+PkCcRm5MIXVI5Q+dNJn7rAfdvTlrSF8XXU7wIWQqg8DQn2+OmvFeR5uzreWH5QaRIodTZ5gVQpXK1A62oDSR18fgyIOBRza2wIiet/67JgimPxGpuecdbz2oUwr7UqifGVz0="
}

request_id = "req4q4tKw3woEEWxw&"
share_id = "shrQBuWjXd0YgPqV6"
application_id = "appwewqLk7iUY4azc"
signature = "be8bd40c133f051f929ebab311c416013f5af0d5acae4264575b88ccf051ee59"


def get_access_policy(view_id: str) -> dict[str, str]:
    return {
        "allowedActions": [
           {
               "modelClassName": "view",
               "modelIdSelector": view_id,
               "action": "readSharedViewData"
           },
            {
               "modelClassName": "view",
               "modelIdSelector": view_id,
               "action": "getMetadataForPrinting"
           },
            {
               "modelClassName": "view",
               "modelIdSelector": view_id,
               "action": "readSignedAttachmentUrls"
           },
            {
               "modelClassName": "row",
               "modelIdSelector": f"rows *[displayedInView={view_id}]",
               "action": "createDocumentPreviewSession"
           }
        ],
        "shareId": share_id,
        "applicationId": application_id,
        "generationNumber": 0,
        # "expires": "2025-01-02T00:00:00.000Z",  # todo:: check how to set it
        "signature": signature
    }


stringifiedObjectParams = {"shouldUseNestedResponseFormat": "true"}
