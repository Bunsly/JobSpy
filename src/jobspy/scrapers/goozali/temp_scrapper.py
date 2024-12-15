import requests

url = 'https://airtable.com/v0.3/view/viwIOzPYaUGxlA0Jd/readSharedViewData'
params = {
    'stringifiedObjectParams': '{"shouldUseNestedResponseFormat":true}',
    'requestId': 'req4q4tKw3woEEWxw',
    'accessPolicy': '{"allowedActions":[{"modelClassName":"view","modelIdSelector":"viwIOzPYaUGxlA0Jd","action":"readSharedViewData"},{"modelClassName":"view","modelIdSelector":"viwIOzPYaUGxlA0Jd","action":"getMetadataForPrinting"},{"modelClassName":"view","modelIdSelector":"viwIOzPYaUGxlA0Jd","action":"readSignedAttachmentUrls"},{"modelClassName":"row","modelIdSelector":"rows *[displayedInView=viwIOzPYaUGxlA0Jd]","action":"createDocumentPreviewSession"}],"shareId":"shrQBuWjXd0YgPqV6","applicationId":"appwewqLk7iUY4azc","generationNumber":0,"expires":"2025-01-02T00:00:00.000Z","signature":"be8bd40c133f051f929ebab311c416013f5af0d5acae4264575b88ccf051ee59"}'
}

headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9,he-IL;q=0.8,he;q=0.7',
    'cookie': '__Host-airtable-session=eyJzZXNzaW9uSWQiOiJzZXNxdFV4bVdKRVRoVGtRMiIsImNzcmZTZWNyZXQiOiIyT0JrVTJkU2I4bDA3NFZIRmd6eTdjTHUifQ==; __Host-airtable-session.sig=heWRrVH73Aa-2ALrH4c_CbvQqTNbNRv9VjPZYv3aHJ4; brw=brwtN7N3OgPFrtfb2; acq=eyJhY3F1aXNpdGlvbiI6Ilt7XCJwbGF0Zm9ybVwiOlwiZGVza3RvcFwiLFwib3JpZ2luXCI6XCJsb2dpblwiLFwidG91Y2hUaW1lXCI6XCIyMDI0LTEyLTEyVDE3OjU1OjQyLjU3OVpcIn1dIn0=; acq.sig=5xrqXjip4IJZxIeSPCkajWt_wlBmGw-k7HJCj8wicxU; brwConsent=opt-in; AWSALBTGCORS=YoIaU+wibkMfutpYUIlGnvYmnUa0VjM2ukwIhESaxfQUNL+PkCcRm5MIXVI5Q+dNJn7rAfdvTlrSF8XXU7wIWQqg8DQn2+OmvFeR5uzreWH5QaRIodTZ5gVQpXK1A62oDSR18fgyIOBRza2wIiet/67JgimPxGpuecdbz2oUwr7UqifGVz0=; AWSALBTG=lWt/xRLIQas/blkys/2YBYl0priNI7gv85sXXtmkrW+TzbLHR8Vm6iY5RDialmLUYsQgLab8uWZyahWRw0HizxdOXhJxd5FB66H85GpUAX8zZbAZPZdUHvzxjaVa130w14QSXDa8OmsNlpKtiUtZ/DXMTOZ1wYDWC4tVJTKJ171wyKA7C9E=; AWSALBTGCORS=lWt/xRLIQas/blkys/2YBYl0priNI7gv85sXXtmkrW+TzbLHR8Vm6iY5RDialmLUYsQgLab8uWZyahWRw0HizxdOXhJxd5FB66H85GpUAX8zZbAZPZdUHvzxjaVa130w14QSXDa8OmsNlpKtiUtZ/DXMTOZ1wYDWC4tVJTKJ171wyKA7C9E=; __Host-airtable-session=eyJzZXNzaW9uSWQiOiJzZXNJU0RKYTBPb1I3QlE0WCJ9; __Host-airtable-session.sig=TCCFy2Z5tzMD0iDHuLNL6HzGQAWaTkjpUHH9QZWOIEo; brw=brwtN7N3OgPFrtfb2',
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

response = requests.get(url, headers=headers, params=params)

# Print the response content
print(response.status_code)
print(response.text)
