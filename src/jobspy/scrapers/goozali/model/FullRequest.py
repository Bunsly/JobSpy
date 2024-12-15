import json


class GoozaliFullRequest():
    def __init__(self, base_url: str):
        self.view_id: str = "viwIOzPYaUGxlA0Jd"
        self.url = base_url.format(view_id=self.view_id)
        self.application_id: str = "appwewqLk7iUY4azc"
        self.air_table_page_load_id: str = "pglqAAzFDZEWCEC7s"
        self.stringifiedObjectParams = {
            "shouldUseNestedResponseFormat": "true"}
        self.session_id: str = "lWt/xRLIQas/blkys/2YBYl0priNI7gv85sXXtmkrW+TzbLHR8Vm6iY5RDialmLUYsQgLab8uWZyahWRw0HizxdOXhJxd5FB66H85GpUAX8zZbAZPZdUHvzxjaVa130w14QSXDa8OmsNlpKtiUtZ/DXMTOZ1wYDWC4tVJTKJ171wyKA7C9E="
        self.cookies: dict[str, str] = {}
        self.request_id: str = "req4q4tKw3woEEWxw&"
        self.share_id: str = "shrQBuWjXd0YgPqV6"
        self.signature: str = "be8bd40c133f051f929ebab311c416013f5af0d5acae4264575b88ccf051ee59"
        self.headers = self._generate_headers()
        self.params = self._generate_params()
        self.cookies = {}

    def _generate_params(self) -> dict[str, str]:
        access_policy = self._generate_access_policy()

        return {
            "stringifiedObjectParams": self.stringifiedObjectParams,
            "request_id": self.request_id,
            "accessPolicy": access_policy
        }

    def _generate_headers(self) -> str:
        return {
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
            'x-airtable-application-id': self.application_id,
            'x-airtable-inter-service-client': 'webClient',
            'x-airtable-page-load-id': self.air_table_page_load_id,
            'x-early-prefetch': 'true',
            'x-requested-with': 'XMLHttpRequest',
            'x-time-zone': 'Asia/Jerusalem',
            'x-user-locale': 'en'
        }

    def _generate_access_policy(self) -> str:
        """
        Generates a JSON string for access policy.
        """
        access_policy = {
            "allowedActions": [
                {"modelClassName": "view", "modelIdSelector": self.view_id,
                 "action": "readSharedViewData"},
                {"modelClassName": "view", "modelIdSelector": self.view_id,
                 "action": "getMetadataForPrinting"},
                {"modelClassName": "view", "modelIdSelector": self.view_id,
                 "action": "readSignedAttachmentUrls"},
                {"modelClassName": "row", "modelIdSelector": f"rows *[displayedInView={self.view_id}]",
                 "action": "createDocumentPreviewSession"}
            ],
            "shareId": self.share_id,
            "applicationId": self.application_id,
            "generationNumber": 0,
            "expires": "2025-01-02T00:00:00.000Z",
            "signature": self.signature
        }
        # Convert to a JSON string
        return json.dumps(access_policy)
