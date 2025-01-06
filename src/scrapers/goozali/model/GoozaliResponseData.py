from . import GoozaliRow, GoozaliColumn


class GoozaliResponseData:
    def __init__(self, applicationId: str, id: str, name: str, columns: list[GoozaliColumn], primaryColumnId: str,
                 meaningfulColumnOrder: list[dict[str, str]], viewOrder: list[str], rows: list[GoozaliRow]):
        self.applicationId = applicationId
        self.id = id
        self.name = name
        self.columns = columns
        self.primaryColumnId = primaryColumnId
        self.meaningfulColumnOrder = meaningfulColumnOrder
        self.viewOrder = viewOrder
        self.rows = rows
