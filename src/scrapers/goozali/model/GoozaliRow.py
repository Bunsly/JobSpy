from datetime import datetime
from typing import Dict, List


class GoozaliRow:
    def __init__(self, id: str, createdTime: str, cellValuesByColumnId: Dict[str, List[str]]):
        self.id = id
        self.createdTime = datetime.strptime(
            createdTime, '%Y-%m-%dT%H:%M:%S.%fZ')
        self.cellValuesByColumnId = cellValuesByColumnId
