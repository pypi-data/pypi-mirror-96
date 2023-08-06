"""Test asyncpraw.models.auth."""
import pytest
from asyncprawcore import InvalidToken

from asyncpraw import Reddit

from .. import IntegrationTest


class TestAuthScript(IntegrationTest):
    async def test_scopes(self):
        with self.use_cassette():
            assert self.reddit.read_only is True
            assert await self.reddit.auth.scopes() == {"*"}


class TestAuthWeb(IntegrationTest):
    def setup_reddit(self):
        self.reddit = Reddit(
            client_id=pytest.placeholders.client_id,
            client_secret=pytest.placeholders.client_secret,
            redirect_uri=pytest.placeholders.redirect_uri,
            user_agent=pytest.placeholders.user_agent,
            username=None,
        )

    async def test_authorize(self):
        with self.use_cassette():
            token = await self.reddit.auth.authorize(pytest.placeholders.auth_code)
            assert isinstance(token, str)
            assert self.reddit.read_only is False
            assert await self.reddit.auth.scopes() == {"submit"}

    async def test_scopes__read_only(self):
        with self.use_cassette():
            assert self.reddit.read_only is True
            assert await self.reddit.auth.scopes() == {"*"}


class TestAuthImplicit(IntegrationTest):
    def setup_reddit(self):
        self.reddit = Reddit(
            client_id=pytest.placeholders.client_id,
            client_secret=None,
            user_agent=pytest.placeholders.user_agent,
        )

    async def test_implicit__with_invalid_token(self):
        self.reddit.auth.implicit("invalid_token", 10, "read")
        with self.use_cassette():
            with pytest.raises(InvalidToken):
                await self.reddit.user.me()

    async def test_scopes__read_only(self):
        with self.use_cassette():
            assert self.reddit.read_only is True
            assert await self.reddit.auth.scopes() == {"*"}
