from datetime import datetime
from typing import Optional

from .observation import Observation
from .observation_log import ObservationLog
from .teamtv_object import TeamTVObject


class SportingEvent(TeamTVObject):
    @property
    def scheduled_at(self) -> datetime:
        return self._scheduled_at

    @property
    def sporting_event_id(self) -> str:
        return self._sporting_event_id

    @property
    def name(self):
        return self._name

    @property
    def tags(self):
        return self._tags

    @property
    def main_video_id(self) -> Optional[str]:
        if self._video_ids:
            return self._video_ids[0]
        return None

    @property
    def is_local(self):
        return self._is_local

    def get_observation_log(self) -> ObservationLog:
        video_id = self.main_video_id
        if video_id:
            clock_id = self._clocks[video_id]['clockId']
        else:
            clock_id = 'U1'

        return ObservationLog(
            Observation,
            self._requester,
            "GET",
            f"/sportingEvents/{self.sporting_event_id}/observations/{clock_id}",
            clock_id,
            self
        )

    def _use_attributes(self, attributes: dict):
        self._name = attributes['name']
        self._sporting_event_id = attributes['sportingEventId']
        self._tags = attributes.get('tags', {})
        self._video_ids = attributes.get('videoIds', [])
        self._clocks = attributes['clocks']
        self._scheduled_at = datetime.fromisoformat(attributes['scheduledAt'].replace("Z", "+00:00"))
        self._is_local = attributes['_metadata']['source']['type'] == 'ResourceGroup'

    def __str__(self):
        return f"{self._scheduled_at.strftime('%d/%m/%y')} {self._name}"
