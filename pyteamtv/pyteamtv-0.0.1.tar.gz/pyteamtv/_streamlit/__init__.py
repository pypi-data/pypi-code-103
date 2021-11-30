import os
from typing import Optional

import streamlit as st

from ..api import TeamTVUser, TeamTVApp
from ..models.resource_group.team import TeamResourceGroup


class App:
    def __init__(self, api):
        self.api = api
        if isinstance(api, TeamTVUser):
            self.membership_list = api.get_membership_list()
            self.current_resource_group: Optional[TeamResourceGroup] = None
        else:
            self.membership_list = None
            self.current_resource_group = api.get_resource_group()

        self.observation_logs = dict()
        self.sporting_events = dict()

    def reset(self):
        self.observation_logs = dict()
        self.sporting_events = dict()

    def set_team(self, name: str):
        if not self.membership_list:
            raise Exception("Cannot set_team in TeamTVApp")

        if not self.current_resource_group or self.current_resource_group.name != name:
            self.current_resource_group = self.membership_list.get_membership_by_name(
                name=name
            ).resource_group  # type: TeamResourceGroup
            self.reset()

    def get_sporting_events(self):
        if not self.sporting_events:
            self.sporting_events = {
                sporting_event.sporting_event_id: sporting_event
                for sporting_event in sorted(
                    self.current_resource_group.get_sporting_events(),
                    key=lambda sporting_event: sporting_event.scheduled_at,
                    reverse=True
                )
            }
        return self.sporting_events

    def get_sporting_event(self, sporting_event_id: str):
        if sporting_event_id not in self.sporting_events:
            self.sporting_events[sporting_event_id] = self.current_resource_group.get_sporting_event(
                sporting_event_id
            )
        return self.sporting_events[sporting_event_id]

    def get_observation_log(self, sporting_event_id: str):
        if sporting_event_id not in self.observation_logs:
            sporting_event = self.get_sporting_event(sporting_event_id)
            self.observation_logs[sporting_event_id] = sporting_event.get_observation_log()
        return self.observation_logs[sporting_event_id]


def get_current_app(app_id: str = None) -> App:
    if 'current_app' not in st.session_state:
        if 'TEAMTV_TOKEN' in os.environ:
            jwt_token = os.environ['TEAMTV_TOKEN']
            # token = jwt.decode(
            #     jwt_token,
            #     TOKEN,
            #     options={
            #         'verify_signature': False
            #     }
            # )
            #
            # print(token)
            # return app.get_team(name)
            api = TeamTVUser(jwt_token)
        else:
            if not app_id:
                app_id = os.environ.get('TEAMTV_APP_ID')
                if not app_id:
                    raise Exception("app_id must be set")

            query_params = st.experimental_get_query_params()
            if 'token' in query_params:
                api = TeamTVApp(
                    jwt_token=query_params['token'][0],
                    app_id=app_id
                )
            else:
                raise Exception("Token not set")

        st.session_state['current_app'] = App(
            api=api
        )

    return st.session_state['current_app']
