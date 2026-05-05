"""
mocking_examples.py — comprehensive guide to unittest.mock.
Run: pytest mocking_examples.py -v
     pytest mocking_examples.py -v -k "patch"
"""
import pytest
import json
import os
from datetime import datetime
from unittest.mock import (
    Mock, MagicMock, AsyncMock,
    patch, patch_object := patch.object,
    call, sentinel, ANY, DEFAULT,
    create_autospec, mock_open,
    PropertyMock
)
from typing import Protocol


# ─────────────────────────────────────────────
# Code under test — production code
# ─────────────────────────────────────────────

class EmailSender:
    """Sends emails via SMTP. We'll mock this."""
    def send(self, to: str, subject: str, body: str) -> bool:
        raise NotImplementedError("Real SMTP not available in tests")


class UserRepository:
    """Fetches users from a database."""
    def find_by_id(self, user_id: int) -> dict:
        raise NotImplementedError("Real DB not available in tests")

    def save(self, user: dict) -> dict:
        raise NotImplementedError("Real DB not available in tests")

    def count(self) -> int:
        raise NotImplementedError("Real DB not available in tests")


class NotificationService:
    """Business logic — the thing we actually want to test."""

    def __init__(self, repo: UserRepository, emailer: EmailSender):
        self._repo = repo
        self._emailer = emailer

    def notify_user(self, user_id: int, message: str) -> bool:
        user = self._repo.find_by_id(user_id)
        if user is None:
            return False
        return self._emailer.send(
            to=user["email"],
            subject="Notification",
            body=message
        )

    def send_welcome_emails(self, new_user_ids: list[int]) -> int:
        sent = 0
        for uid in new_user_ids:
            user = self._repo.find_by_id(uid)
            if user:
                ok = self._emailer.send(
                    to=user["email"],
                    subject="Welcome!",
                    body=f"Hi {user['name']}, welcome!"
                )
                if ok:
                    sent += 1
        return sent


def fetch_weather(city: str) -> dict:
    """Makes an HTTP request — we'll mock requests.get."""
    import requests
    resp = requests.get(f"https://api.example.com/weather/{city}")
    resp.raise_for_status()
    return resp.json()


def load_app_config() -> dict:
    """Reads config from environment and file."""
    config_path = os.environ.get("CONFIG_PATH", "config.json")
    with open(config_path) as f:
        return json.load(f)


def get_current_year() -> int:
    return datetime.now().year


class Counter:
    def __init__(self, start: int = 0):
        self.value = start

    def increment(self) -> int:
        self.value += 1
        return self.value

    def reset(self) -> None:
        self.value = 0


# ─────────────────────────────────────────────
# 1. Mock basics
# ─────────────────────────────────────────────

class TestMockBasics:

    def test_mock_records_calls(self):
        m = Mock()
        m.do_something(1, 2, key="value")

        m.do_something.assert_called_once_with(1, 2, key="value")
        assert m.do_something.call_count == 1

    def test_mock_return_value(self):
        m = Mock()
        m.fetch.return_value = {"id": 1, "name": "Alice"}

        result = m.fetch(user_id=1)
        assert result["name"] == "Alice"

    def test_mock_side_effect_exception(self):
        m = Mock()
        m.connect.side_effect = ConnectionError("server down")

        with pytest.raises(ConnectionError, match="server down"):
            m.connect()

    def test_mock_side_effect_list(self):
        """Returns different values on successive calls."""
        m = Mock()
        m.get_id.side_effect = [1, 2, 3]

        assert m.get_id() == 1
        assert m.get_id() == 2
        assert m.get_id() == 3

    def test_mock_side_effect_callable(self):
        """Side effect as a function — processes arguments."""
        m = Mock()
        m.double.side_effect = lambda x: x * 2

        assert m.double(5) == 10
        assert m.double(3) == 6

    def test_mock_not_called(self):
        m = Mock()
        m.method.assert_not_called()

    def test_mock_called_multiple_times(self):
        m = Mock()
        m.log("event1")
        m.log("event2")
        m.log("event3")

        assert m.log.call_count == 3
        m.log.assert_any_call("event2")
        assert m.log.call_args_list == [
            call("event1"),
            call("event2"),
            call("event3"),
        ]

    def test_mock_attribute_access(self):
        m = Mock()
        m.config.database.host = "localhost"
        assert m.config.database.host == "localhost"


# ─────────────────────────────────────────────
# 2. MagicMock — supports dunder methods
# ─────────────────────────────────────────────

class TestMagicMock:

    def test_magic_mock_supports_len(self):
        m = MagicMock()
        m.__len__.return_value = 5
        assert len(m) == 5

    def test_magic_mock_supports_iteration(self):
        m = MagicMock()
        m.__iter__.return_value = iter([1, 2, 3])
        assert list(m) == [1, 2, 3]

    def test_magic_mock_supports_context_manager(self):
        m = MagicMock()
        with m as ctx:
            ctx.do_something()
        m.__enter__.assert_called_once()
        m.__exit__.assert_called_once()

    def test_magic_mock_supports_indexing(self):
        m = MagicMock()
        m.__getitem__.return_value = "value"
        assert m["key"] == "value"

    def test_mock_vs_magic_mock(self):
        # Mock does NOT support dunder methods by default
        plain = Mock()
        with pytest.raises(TypeError):
            len(plain)  # AttributeError → TypeError

        # MagicMock does
        magic = MagicMock()
        len(magic)  # returns 0 by default — no error


# ─────────────────────────────────────────────
# 3. Injecting mocks via constructor (best practice)
# ─────────────────────────────────────────────

class TestNotificationService:
    """
    Inject mocks via constructor — no @patch needed.
    This is the cleanest approach for code with dependency injection.
    """

    def setup_method(self):
        self.mock_repo = Mock(spec=UserRepository)
        self.mock_emailer = Mock(spec=EmailSender)
        self.service = NotificationService(self.mock_repo, self.mock_emailer)

    def test_notify_user_fetches_and_emails(self):
        # Arrange
        self.mock_repo.find_by_id.return_value = {
            "id": 1, "email": "alice@example.com", "name": "Alice"
        }
        self.mock_emailer.send.return_value = True

        # Act
        result = self.service.notify_user(1, "Your order is ready")

        # Assert
        assert result is True
        self.mock_repo.find_by_id.assert_called_once_with(1)
        self.mock_emailer.send.assert_called_once_with(
            to="alice@example.com",
            subject="Notification",
            body="Your order is ready"
        )

    def test_notify_user_returns_false_when_user_not_found(self):
        self.mock_repo.find_by_id.return_value = None

        result = self.service.notify_user(999, "message")

        assert result is False
        self.mock_emailer.send.assert_not_called()

    def test_send_welcome_emails_counts_successes(self):
        def fake_find(uid):
            users = {
                1: {"email": "a@ex.com", "name": "Alice"},
                2: None,  # not found
                3: {"email": "c@ex.com", "name": "Charlie"},
            }
            return users.get(uid)

        self.mock_repo.find_by_id.side_effect = fake_find
        self.mock_emailer.send.return_value = True

        count = self.service.send_welcome_emails([1, 2, 3])

        assert count == 2  # user 2 not found, others emailed
        assert self.mock_emailer.send.call_count == 2


# ─────────────────────────────────────────────
# 4. @patch decorator — patching module-level names
# ─────────────────────────────────────────────

class TestPatchDecorator:
    """
    CRITICAL RULE: patch WHERE the name is USED, not where it's defined.

    In mocking_examples.py:
        import requests      → at module level (from requests import get would differ)
        fetch_weather calls requests.get

    Since requests is used as `requests.get` in THIS module, we patch:
        "mocking_examples.requests.get"   ← WHERE IT'S USED
    NOT:
        "requests.get"                    ← WHERE IT'S DEFINED (wrong!)
    """

    @patch("mocking_examples.requests.get")
    def test_fetch_weather_calls_correct_url(self, mock_get):
        # Arrange: set up the mock response
        mock_response = Mock()
        mock_response.json.return_value = {"temp": 22, "condition": "sunny"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Act
        result = fetch_weather("London")

        # Assert
        mock_get.assert_called_once_with("https://api.example.com/weather/London")
        assert result["temp"] == 22

    @patch("mocking_examples.requests.get")
    def test_fetch_weather_propagates_http_error(self, mock_get):
        import requests as req
        mock_get.return_value.raise_for_status.side_effect = (
            req.exceptions.HTTPError("404 Not Found")
        )

        with pytest.raises(req.exceptions.HTTPError):
            fetch_weather("NonExistentCity")


# ─────────────────────────────────────────────
# 5. patch as context manager
# ─────────────────────────────────────────────

class TestPatchContextManager:

    def test_load_config_reads_correct_file(self, tmp_path):
        config_data = {"db_host": "localhost", "port": 5432}
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(config_data))

        with patch.dict(os.environ, {"CONFIG_PATH": str(config_file)}):
            result = load_app_config()

        assert result["db_host"] == "localhost"
        assert result["port"] == 5432

    def test_mock_open_for_file_reading(self):
        fake_content = '{"host": "db.internal", "port": 3306}'
        m = mock_open(read_data=fake_content)

        with patch("mocking_examples.open", m):
            with patch.dict(os.environ, {"CONFIG_PATH": "any.json"}):
                result = load_app_config()

        assert result["host"] == "db.internal"
        m.assert_called_once_with("any.json")

    def test_patch_dict_env_variables(self):
        with patch.dict(os.environ, {"MY_VAR": "test_value"}):
            assert os.environ["MY_VAR"] == "test_value"
        # Restored outside context
        assert "MY_VAR" not in os.environ


# ─────────────────────────────────────────────
# 6. patch.object — patch a specific attribute on an object/class
# ─────────────────────────────────────────────

class TestPatchObject:

    def test_patch_object_method(self):
        counter = Counter(10)

        with patch.object(counter, "reset") as mock_reset:
            counter.reset()
            mock_reset.assert_called_once()
        # Real reset restored after context
        counter.reset()
        assert counter.value == 0

    def test_patch_datetime_now(self):
        fixed_time = datetime(2024, 1, 15, 12, 0, 0)

        with patch("mocking_examples.datetime") as mock_dt:
            mock_dt.now.return_value = fixed_time
            year = get_current_year()

        assert year == 2024

    def test_patch_class_method(self):
        with patch.object(Counter, "increment", return_value=42) as mock_inc:
            c = Counter()
            result = c.increment()
            assert result == 42
            mock_inc.assert_called_once()


# ─────────────────────────────────────────────
# 7. PropertyMock — mock a @property
# ─────────────────────────────────────────────

class Config:
    @property
    def database_url(self) -> str:
        return os.environ.get("DATABASE_URL", "")


class TestPropertyMock:

    def test_mock_property(self):
        with patch.object(Config, "database_url",
                          new_callable=PropertyMock) as mock_url:
            mock_url.return_value = "postgresql://test:5432/db"
            config = Config()
            assert config.database_url == "postgresql://test:5432/db"
            mock_url.assert_called_once()


# ─────────────────────────────────────────────
# 8. monkeypatch (pytest fixture)
# ─────────────────────────────────────────────

class TestMonkeypatch:
    """
    monkeypatch: pytest's built-in alternative to @patch.
    Automatically undone after test — no decorator/context needed.
    """

    def test_monkeypatch_env_variable(self, monkeypatch):
        monkeypatch.setenv("API_KEY", "test-key-123")
        assert os.environ["API_KEY"] == "test-key-123"

    def test_monkeypatch_setattr(self, monkeypatch, tmp_path):
        config_file = tmp_path / "config.json"
        config_file.write_text('{"key": "value"}')

        monkeypatch.setenv("CONFIG_PATH", str(config_file))
        result = load_app_config()
        assert result["key"] == "value"

    def test_monkeypatch_replaces_function(self, monkeypatch):
        monkeypatch.setattr("mocking_examples.get_current_year", lambda: 2000)
        assert get_current_year() == 2000

    def test_monkeypatch_delattr(self, monkeypatch):
        import mocking_examples
        monkeypatch.delattr(mocking_examples, "get_current_year")
        assert not hasattr(mocking_examples, "get_current_year")


# ─────────────────────────────────────────────
# 9. spec= and create_autospec — safer mocks
# ─────────────────────────────────────────────

class TestSpecMocks:
    """
    Mock(spec=RealClass) prevents calling non-existent methods.
    Catches typos and API drift early.
    """

    def test_spec_prevents_invalid_method_call(self):
        m = Mock(spec=UserRepository)

        # Valid methods work
        m.find_by_id.return_value = {"id": 1}
        result = m.find_by_id(1)
        assert result["id"] == 1

        # Invalid methods raise AttributeError
        with pytest.raises(AttributeError):
            m.nonexistent_method()  # not in UserRepository

    def test_create_autospec(self):
        """create_autospec also checks signatures."""
        m = create_autospec(UserRepository, instance=True)
        m.find_by_id.return_value = None

        # Correct signature
        m.find_by_id(user_id=1)

        # Wrong signature raises TypeError
        with pytest.raises(TypeError):
            m.find_by_id(1, 2)  # too many args

    def test_spec_class_method(self):
        m = create_autospec(EmailSender, instance=True)
        m.send.return_value = True
        result = m.send("a@b.com", "Subject", "Body")
        assert result is True


# ─────────────────────────────────────────────
# 10. ANY and sentinel for flexible assertions
# ─────────────────────────────────────────────

class TestAnyAndSentinel:

    def test_any_matches_anything(self):
        m = Mock()
        m.log(42, "some random message", timestamp=datetime.now())

        m.log.assert_called_once_with(42, ANY, timestamp=ANY)

    def test_sentinel_unique_object(self):
        """sentinel creates unique objects for identity tests."""
        NOT_SET = sentinel.NOT_SET

        m = Mock()
        m.get_value.return_value = NOT_SET

        result = m.get_value()
        assert result is NOT_SET
        assert result is NOT_SET  # same sentinel object


# ─────────────────────────────────────────────
# 11. Async mocking
# ─────────────────────────────────────────────

async def fetch_user_async(repo, user_id: int) -> dict:
    return await repo.find_user(user_id)


async def send_notifications_async(emailer, recipients: list[str], msg: str) -> int:
    count = 0
    for recipient in recipients:
        if await emailer.send_async(recipient, msg):
            count += 1
    return count


class TestAsyncMock:

    @pytest.mark.asyncio
    async def test_async_mock_basic(self):
        mock_repo = AsyncMock()
        mock_repo.find_user.return_value = {"id": 1, "name": "Alice"}

        result = await fetch_user_async(mock_repo, 1)

        assert result["name"] == "Alice"
        mock_repo.find_user.assert_awaited_once_with(1)

    @pytest.mark.asyncio
    async def test_async_mock_counts_successes(self):
        mock_emailer = AsyncMock()
        mock_emailer.send_async.return_value = True

        count = await send_notifications_async(
            mock_emailer, ["a@ex.com", "b@ex.com", "c@ex.com"], "Hello"
        )

        assert count == 3
        assert mock_emailer.send_async.await_count == 3

    @pytest.mark.asyncio
    async def test_async_mock_side_effect(self):
        mock_emailer = AsyncMock()
        mock_emailer.send_async.side_effect = [True, False, True]

        count = await send_notifications_async(
            mock_emailer, ["a@ex.com", "b@ex.com", "c@ex.com"], "Hello"
        )

        assert count == 2  # second call returned False


# ─────────────────────────────────────────────
# 12. Verify no unexpected calls — assert_called_* summary
# ─────────────────────────────────────────────

class TestAssertionMethods:
    """Quick reference for all mock assertion methods."""

    def test_all_assertion_methods(self):
        m = Mock()

        # Not called yet
        m.method.assert_not_called()

        # First call
        m.method("a", key="b")
        m.method.assert_called()
        m.method.assert_called_once()
        m.method.assert_called_with("a", key="b")
        m.method.assert_called_once_with("a", key="b")

        # Second call
        m.method("c")
        m.method.assert_any_call("a", key="b")  # was called with these args at some point
        m.method.assert_any_call("c")
        assert m.method.call_count == 2

        # Check full call history
        assert m.method.call_args_list == [
            call("a", key="b"),
            call("c"),
        ]

        # Reset
        m.method.reset_mock()
        m.method.assert_not_called()


# ─────────────────────────────────────────────
# Run
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v", "--tb=short",
                          "-k", "not Async"]))  # skip async unless pytest-asyncio installed
