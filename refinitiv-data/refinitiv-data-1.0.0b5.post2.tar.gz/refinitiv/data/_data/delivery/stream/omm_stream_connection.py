# coding: utf-8


from .event import StreamEventPool
from .stream_connection import StreamConnection
from .stream_cxn_state import StreamCxnState


class OMMStreamConnection(StreamConnection):
    def get_login_message(self):
        login_message = {
            "Domain": "Login",
            "ID": self.id,
            "Key": self._session.get_omm_login_message_key_data(),
        }
        return login_message

    def get_close_message(self) -> dict:
        close_message = {
            "Domain": "Login",
            "ID": self.id,
            "Type": "Close",
        }
        return close_message

    def _handle_login_message(self, message: dict):
        """
        Parameters
        ----------
        message
            {
                'ID': 2,
                'Type': 'Refresh',
                'Domain': 'Login',
                'Key':
                    {
                        'Name': TOKEN_HERE,
                        'Elements': {
                            'AllowSuspectData': 1, 'ApplicationId': '256',
                            'ApplicationName': 'RTO',
                            'AuthenticationErrorCode': 0,
                            'AuthenticationErrorText': {
                                'Type': 'AsciiString', 'Data': None
                            },
                            'AuthenticationTTReissue': 1634562361,
                            'Position': '10.46.188.21/EPUAKYIW3629',
                            'ProvidePermissionExpressions': 1,
                            'ProvidePermissionProfile': 0,
                            'SingleOpen': 1, 'SupportEnhancedSymbolList': 1,
                            'SupportOMMPost': 1,
                            'SupportPauseResume': 0, 'SupportStandby': 0,
                            'SupportBatchRequests': 7,
                            'SupportViewRequests': 1, 'SupportOptimizedPauseResume': 0
                        }
                    },
                'State':
                    {
                        'Stream': 'Open', 'Data': 'Ok',
                        'Text': 'Login accepted by host ads-fanout-lrg-az2-apse1-prd.'
                    }, 'Elements': {'PingTimeout': 30, 'MaxMsgSize': 61426}
            }
        """

        state = message.get("State", {})
        stream_state = state.get("Stream")

        if stream_state == "Open":
            self._state = StreamCxnState.Ready
            self._loop.call_soon_threadsafe(self._prepared.set_result, True)

        elif stream_state == "Closed":
            self.error(
                f"{self._classname} received a closing message "
                f"(cxn state={self.state}, message state={state})"
            )
            self.dispose()

        else:
            raise ValueError(
                f"{self._classname} Don't know what to do "
                f"(cxn state={self.state}, "
                f"stream_state={stream_state}, message={message})"
            )

    def _process_message(self, message: dict) -> None:
        self.debug(f"{self._classname} process_message {message} ")

        message_type = message.get("Type")
        stream_id = message.get("ID")

        event = StreamEventPool.pop(stream_id)

        if message_type == "Refresh":
            self._emitter.emit(event.refresh, self, message)
            message_complete = message.get("Complete", True)
            message_complete and self._emitter.emit(event.complete, self, message)

        elif message_type == "Update":
            self._emitter.emit(event.update, self, message)

        elif message_type == "Status":
            self._emitter.emit(event.status, self, message)

        elif message_type == "Error":
            self._emitter.emit(event.error, self, message)

        elif message_type == "Ping":
            pong_message = {"Type": "Pong"}
            self.send(pong_message)

        else:
            raise ValueError(f"Unknown message {message}")

        StreamEventPool.push(stream_id, event)
