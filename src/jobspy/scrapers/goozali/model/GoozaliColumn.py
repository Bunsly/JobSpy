from typing import Optional

from jobspy.scrapers.goozali.model import GoozaliColumnTypeOptions


class GoozaliColumn:
    def __init__(self, id: str, name: str, description: Optional[str], type: str, typeOptions: GoozaliColumnTypeOptions,
                 default: Optional[str], initialCreatedTime: str, initialCreatedByUserId: str,
                 lastModifiedTime: str, lastModifiedByUserId: str, isEditableFromSync: bool):
        self.id = id
        self.name = name
        self.description = description
        self.type = type
        self.typeOptions = typeOptions
        self.default = default
        self.initialCreatedTime = initialCreatedTime
        self.initialCreatedByUserId = initialCreatedByUserId
        self.lastModifiedTime = lastModifiedTime
        self.lastModifiedByUserId = lastModifiedByUserId
        self.isEditableFromSync = isEditableFromSync
