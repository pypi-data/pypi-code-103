from botbuilder.core import Middleware, TurnContext
from botbuilder.schema import Activity,ActivityTypes
from .translate_settings import TranslateSettings
from .translate_service import TranslateService
from typing import Callable, Awaitable


class TranslateMiddleware(Middleware):
    def __init__(self, settings: TranslateSettings):
        if not settings.validate_settings():
            raise Exception("Translate middleware settings are invalid")
        self.translator = TranslateService(settings)

    async def on_turn(self,
                      context: TurnContext,
                      call_next: Callable[[TurnContext], Awaitable]):

        if context.activity.type == ActivityTypes.message:
            translate_response = self.translator.translate_text(context.activity.text)
            context.turn_state.setdefault('translate_response', translate_response)

        return await call_next()
