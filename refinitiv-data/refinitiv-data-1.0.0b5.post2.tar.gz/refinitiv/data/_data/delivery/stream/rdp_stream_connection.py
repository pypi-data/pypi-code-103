# coding: utf-8
import requests

from .event import StreamEventPool
from .stream_connection import StreamConnection
from .stream_cxn_state import StreamCxnState


class RDPStreamConnection(StreamConnection):
    def get_login_message(self):
        login_message = self.session.get_rdp_login_message(self.id)
        return login_message

    def set_auth_token(self, auth_token: str) -> None:
        auth_message = self.session.get_rdp_login_message(self.id)
        self.send(auth_message)

    def _handle_login_message(self, message: dict):
        """
        Parameters
        ----------
        message
            {
                'state': {
                    'code': 200,
                    'status': 'OK',
                    'message': 'Access token is valid'
                },
                'type': 'Ack',
                'streamID': '2'
            }
        """
        state = message.get("state", {})
        status = state.get("status")
        code = state.get("code")

        # "OK" for qps and "Ok" for tds
        if status == "OK" or status == "Ok":
            self._state = StreamCxnState.Ready
            self._loop.call_soon_threadsafe(self._prepared.set_result, True)

        elif status == "Closed":
            self.error(
                f"{self._classname} received a closing message "
                f"(cxn state={self.state}, message state={state})"
            )
            self.dispose()

        elif status == "Error" or code == requests.codes.bad:
            self.error(
                f"{self._classname} received an error message "
                f"(cxn state={self.state}, message state={state})"
            )
            self.dispose()

        else:
            raise ValueError(
                f"{self._classname} Don't know what to do "
                f"(cxn state={self.state}, "
                f"message status={status}, message={message})"
            )

    def _process_message(self, message: dict) -> None:
        self.debug(f"{self._classname} process_message {message} ")

        stream_id = message.get("streamID")
        message_type = message.get("type")

        event = StreamEventPool.pop(stream_id)

        if message_type == "Ack":
            self._emitter.emit(event.ack, self, message)

        elif message_type == "Response":
            self._emitter.emit(event.response, self, message)

        elif message_type == "Update":
            self._emitter.emit(event.update, self, message)

        elif message_type == "Alarm":
            self._emitter.emit(event.alarm, self, message)

        elif message_type == "Error":
            self._emitter.emit(event.error, self, message)

        elif message_type == "Heartbeat":
            # do nothing
            pass

        else:
            raise ValueError(f"Unknown message {message}")

        StreamEventPool.push(stream_id, event)
