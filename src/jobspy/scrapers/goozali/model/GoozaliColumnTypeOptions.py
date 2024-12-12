from typing import Dict, List

from jobspy.scrapers.goozali.model.GoozaliColumnChoice import GoozaliColumnChoice


class GoozaliColumnTypeOptions:
    def __init__(self, choiceOrder: List[str], choices: Dict[str, GoozaliColumnChoice], disableColors: bool):
        self.choiceOrder = choiceOrder
        self.choices = choices
        self.disableColors = disableColors
