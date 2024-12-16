from jobspy.scrapers.goozali.model.GoozaliColumnChoice import GoozaliColumnChoice


class GoozaliColumnTypeOptions:
    def __init__(self, choiceOrder: list[str], choices: dict[str, GoozaliColumnChoice], disableColors: bool):
        self.choiceOrder = choiceOrder
        self.choices = choices
        self.disableColors = disableColors

    def __init__(self, typeOptions: dict):
        self.choiceOrder = typeOptions.get("choiceOrder", [])
        self.choices: dict[str, GoozaliColumnChoice] = typeOptions.get(
            "choices", {})
        self.disableColors = typeOptions.get("disableColors", False)
        self.dateFormat = typeOptions.get("dateFormat", "")
        self.isDateTime = typeOptions.get("isDateTime", False)
        self.timeZone = typeOptions.get("timeZone", "")
        self.shouldDisplayTimeZone = typeOptions.get(
            "shouldDisplayTimeZone", False)
        self.formulaTextParsed = typeOptions.get("formulaTextParsed", "")
        self.dependencies = typeOptions.get("dependencies", [])
        self.resultType = typeOptions.get("resultType", "")
        self.resultIsArray = typeOptions.get("resultIsArray", False)
