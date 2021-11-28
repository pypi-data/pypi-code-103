# ------------------------------------------------------------ Imports ----------------------------------------------------------- #

# System
from typing import List, Optional
import json

# Pip
from kcu import request
from noraise import noraise

# Local
from .models import Message, ParseMode

# -------------------------------------------------------------------------------------------------------------------------------- #



# -------------------------------------------------------- class: Telegram ------------------------------------------------------- #

class Telegram:

    # --------------------------------------------------------- Init --------------------------------------------------------- #

    def __init__(
        self,
        token: str,
        chat_id: Optional[str] = None,
        debug: bool = False
    ):
        self.token = token
        self.chat_id = chat_id
        self.debug = debug


    # ---------------------------------------------------- Public methods ---------------------------------------------------- #

    def get_updates(
        self,
        allowed_updates: Optional[List[str]] = None
    ):
        return self._send(
            endpoint='getUpdates',
            allowed_updates=json.dumps(allowed_updates) if allowed_updates else None
        )

    def send_message(
        self,
        message: str,
        chat_id: Optional[str] = None,
        parse_mode: Optional[ParseMode] = None,
        reply_markup: Optional[dict] = None,
        **extra_params
    ) -> Optional[Message]:
        return self._send_message(
            endpoint='sendMessage',
            chat_id=chat_id,
            text=message,
            parse_mode=(parse_mode or ParseMode.HTML).value,
            reply_markup=json.dumps(reply_markup) if reply_markup else None,
            **extra_params
        )

    def send_poll(
        self,
        question: str,
        options: List[str],
        chat_id: Optional[str] = None,
        allows_multiple_answers: bool = False,
        open_period_seconds: Optional[int] = None,
        **extra_params
    ) -> Optional[Message]:
        return self._send_message(
            endpoint='sendPoll',
            chat_id=chat_id,
            question=question,
            options=json.dumps(options),
            allows_multiple_answers=allows_multiple_answers,
            open_period=open_period_seconds,
            **extra_params
        )
    
    def stop_poll(
        self,
        message_id: str,
        chat_id: Optional[str] = None
    ) -> Optional[dict]:
        return self._send(
            'stopPoll',
            chat_id=chat_id or self.chat_id,
            message_id=message_id
        )

    def delete_message(
        self,
        message_id: str,
        chat_id: Optional[str] = None
    ) -> Optional[dict]:
        return self._send(
            endpoint='deleteMessage',
            chat_id=chat_id or self.chat_id,
            message_id=message_id
        )


    # Private

    @noraise()
    def _send_message(
        self,
        endpoint: str,
        chat_id: Optional[str] = None,
        **extra_params
    ) -> Optional[Message]:
        chat_id = chat_id or self.chat_id

        if not chat_id:
            if self.debug:
                print('ERROR: No chat id')

            return None

        return Message.from_dict(
            self._send(
                endpoint=endpoint,
                chat_id=chat_id,
                **extra_params
            )['result']
        )

    @noraise()
    def _send(
        self,
        endpoint: str,
        **extra_params
    ) -> Optional[dict]:
        params = {k:v for k, v in extra_params.items() if v is not None}
        url = f'https://api.telegram.org/bot{self.token}/{endpoint}'

        if self.debug:
            print(url, params)

        res = request.get(
            url,
            params=params
        )

        return res.json()


# -------------------------------------------------------------------------------------------------------------------------------- #