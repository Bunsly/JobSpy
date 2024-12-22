from jobspy.scrapers.goozali.model import GoozaliResponseData


class GoozaliResponse:
    def __init__(self, msg: str, data: GoozaliResponseData):
        self.msg = msg
        self.data = data
