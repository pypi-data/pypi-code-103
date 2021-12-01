from unittest.mock import patch

import pytest

from sym.flow.cli.commands.bots.list import get_bot_users_data
from sym.flow.cli.helpers.utils import human_friendly, utc_to_local
from sym.flow.cli.tests.factories.tokens import SymTokenFactory
from sym.flow.cli.tests.factories.users import BotUserFactory


class TestBotsList:
    @pytest.fixture
    def tokens_and_bots(self):
        bot_users = BotUserFactory.create_batch(3)
        tokens = [
            SymTokenFactory.create(user__id=bot_users[0].id),
            SymTokenFactory.create(user__id=bot_users[1].id),
        ]
        yield (tokens, bot_users)

    @pytest.fixture(autouse=True)
    def patchypatch(self, tokens_and_bots):
        tokens, bots = tokens_and_bots
        with patch("sym.flow.cli.helpers.api.SymAPI.get_users", return_value=bots):
            with patch("sym.flow.cli.helpers.api.SymAPI.get_tokens", return_value=tokens):
                yield

    def test_get_bot_users_data(self, tokens_and_bots, global_options):
        tokens, bots = tokens_and_bots
        table_data = get_bot_users_data(global_options.sym_api)

        assert table_data.pop(0) == ["Username", "Token Count", "Created At"]
        for i, row in enumerate(table_data):
            assert row == [
                bots[i].sym_identifier,
                1 if i == 0 or i == 1 else 0,  # Bot users 0 and 1 have 1 token
                human_friendly(utc_to_local(bots[i].created_at)),
            ]
