from typing import Dict, List

from jobspy.scrapers.goozali.model.GoozaliColumn import GoozaliColumn
from jobspy.scrapers.goozali.model.GoozaliRow import GoozaliRow


class GoozaliTable:
    def __init__(self, applicationId: str, id: str, name: str, columns: List[GoozaliColumn], primaryColumnId: str,
                 meaningfulColumnOrder: List[Dict[str, str]], viewOrder: List[str], rows: List[GoozaliRow]):
        self.applicationId = applicationId
        self.id = id
        self.name = name
        self.columns = columns
        self.primaryColumnId = primaryColumnId
        self.meaningfulColumnOrder = meaningfulColumnOrder
        self.viewOrder = viewOrder
        self.rows = rows
