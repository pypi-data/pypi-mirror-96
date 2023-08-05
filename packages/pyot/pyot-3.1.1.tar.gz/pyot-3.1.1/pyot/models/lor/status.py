from datetime import datetime
from typing import List

from dateutil.parser import parse
from .__core__ import PyotCore, PyotStatic

# PYOT STATIC OBJECTS

class StatusContentData(PyotStatic):
    locale: str
    content: str


class StatusUpdateData(PyotStatic):
    id: int
    author: str
    publish: bool
    publish_locations: List[str] # (Legal values: riotclient, riotstatus, game)
    translations: List[StatusContentData]
    created_at: datetime
    updated_at: datetime

    class Meta(PyotCore.Meta):
        raws = ["publish_locations"]
        renamed = {"created_at": "created_at_strftime", "updated_at": "updated_at_strftime"}

    @property
    def created_at(self) -> datetime:
        timestr = self.created_at_strftime
        return parse(timestr) if timestr is not None else timestr

    @property
    def updated_at(self) -> datetime:
        timestr = self.updated_at_strftime
        return parse(timestr) if timestr is not None else timestr


class StatusDetailData(PyotStatic):
    id: int
    maintenance_status: str # (Legal values: scheduled, in_progress, complete)
    incident_severity: str # (Legal values: info, warning, critical)
    titles: List[StatusContentData]
    updates: List[StatusUpdateData]
    created_at: datetime
    archive_at: datetime
    updated_at: datetime
    platforms: List[str]

    class Meta(PyotCore.Meta):
        raws = ["platforms"]
        renamed = {"created_at": "created_at_strftime", "updated_at": "updated_at_strftime", "archive_at": "archive_at_strftime"}

    @property
    def created_at(self) -> datetime:
        timestr = self.created_at_strftime
        return parse(timestr) if timestr is not None else timestr

    @property
    def archive_at(self) -> datetime:
        timestr = self.archive_at_strftime
        return parse(timestr) if timestr is not None else timestr

    @property
    def updated_at(self) -> datetime:
        timestr = self.updated_at_strftime
        return parse(timestr) if timestr is not None else timestr


# PYOT CORE OBJECTS

class Status(PyotCore):
    id: str
    name: str
    locales: List[str]
    maintenances: List[StatusDetailData]
    incidents: List[StatusDetailData]

    class Meta(PyotCore.Meta):
        rules = {"status_v1_platform_data": []}
        raws = ["locales"]

    def __init__(self, region: str = None):
        self._lazy_set(locals())
