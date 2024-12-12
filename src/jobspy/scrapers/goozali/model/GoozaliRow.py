from typing import Dict, List


class GoozaliRow:
    def __init__(self, id: str, createdTime: str, cellValuesByColumnId: Dict[str, List[str]]):
        self.id = id
        self.createdTime = createdTime
        self.cellValuesByColumnId = cellValuesByColumnId
