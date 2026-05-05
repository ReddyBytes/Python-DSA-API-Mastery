"""
pytest examples — comprehensive practical guide.
Run: pytest pytest_examples.py -v
     pytest pytest_examples.py -v --tb=short
     pytest pytest_examples.py -k "bank"
     pytest pytest_examples.py --cov=. --cov-report=term-missing
"""
import pytest
from datetime import datetime, timedelta
from dataclasses import dataclass, field


# ─────────────────────────────────────────────
# Code under test
# ─────────────────────────────────────────────

class InsufficientFundsError(Exception):
    pass


class BankAccount:
    def __init__(self, owner: str, initial_balance: float = 0):
        if initial_balance < 0:
            raise ValueError("Initial balance cannot be negative")
        self.owner = owner
        self._balance = initial_balance
        self._transactions: list[dict] = []

    @property
    def balance(self) -> float:
        return self._balance

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError(f"Deposit amount must be positive, got {amount}")
        self._balance += amount
        self._transactions.append({"type": "deposit", "amount": amount})

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError(f"Withdrawal amount must be positive, got {amount}")
        if amount > self._balance:
            raise InsufficientFundsError(
                f"Cannot withdraw {amount:.2f}, balance is {self._balance:.2f}"
            )
        self._balance -= amount
        self._transactions.append({"type": "withdrawal", "amount": amount})

    def transaction_count(self) -> int:
        return len(self._transactions)


def calculate_compound_interest(principal: float, rate: float, years: int) -> float:
    """Calculate compound interest (annually compounded)."""
    return principal * (1 + rate) ** years


def is_valid_email(email: str) -> bool:
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


@dataclass
class User:
    name: str
    email: str
    age: int
    created_at: datetime = field(default_factory=datetime.now)

    def is_adult(self) -> bool:
        return self.age >= 18

    def display_name(self) -> str:
        return self.name.title()


class ShoppingCart:
    def __init__(self):
        self._items: dict[str, tuple[float, int]] = {}  # name → (price, qty)

    def add_item(self, name: str, price: float, quantity: int = 1) -> None:
        if price < 0:
            raise ValueError("Price cannot be negative")
        if quantity < 1:
            raise ValueError("Quantity must be at least 1")
        if name in self._items:
            old_price, old_qty = self._items[name]
            self._items[name] = (old_price, old_qty + quantity)
        else:
            self._items[name] = (price, quantity)

    def remove_item(self, name: str) -> None:
        if name not in self._items:
            raise KeyError(f"Item '{name}' not in cart")
        del self._items[name]

    def total(self) -> float:
        return sum(price * qty for price, qty in self._items.values())

    def item_count(self) -> int:
        return sum(qty for _, qty in self._items.values())

    def is_empty(self) -> bool:
        return len(self._items) == 0


# ─────────────────────────────────────────────
# 1. Basic Tests — Assert Introspection
# ─────────────────────────────────────────────

class TestBankAccountBasics:
    """pytest shows exactly what failed — no assertEqual needed."""

    def test_initial_balance_is_zero_by_default(self):
        account = BankAccount("Alice")
        assert account.balance == 0

    def test_initial_balance_can_be_set(self):
        account = BankAccount("Alice", 100)
        assert account.balance == 100

    def test_deposit_increases_balance(self):
        account = BankAccount("Alice", 50)
        account.deposit(25)
        assert account.balance == 75

    def test_withdraw_decreases_balance(self):
        account = BankAccount("Alice", 100)
        account.withdraw(30)
        assert account.balance == 70

    def test_owner_attribute(self):
        account = BankAccount("Bob")
        assert account.owner == "Bob"


# ─────────────────────────────────────────────
# 2. Exception Testing
# ─────────────────────────────────────────────

class TestBankAccountExceptions:

    def test_withdraw_more_than_balance_raises(self):
        account = BankAccount("Alice", 50)
        with pytest.raises(InsufficientFundsError):
            account.withdraw(100)

    def test_insufficient_funds_message_mentions_amounts(self):
        account = BankAccount("Alice", 50)
        with pytest.raises(InsufficientFundsError, match="Cannot withdraw 100"):
            account.withdraw(100)

    def test_deposit_negative_amount_raises_value_error(self):
        account = BankAccount("Alice")
        with pytest.raises(ValueError, match="must be positive"):
            account.deposit(-10)

    def test_deposit_zero_raises_value_error(self):
        account = BankAccount("Alice")
        with pytest.raises(ValueError):
            account.deposit(0)

    def test_negative_initial_balance_raises(self):
        with pytest.raises(ValueError, match="cannot be negative"):
            BankAccount("Alice", -100)

    def test_withdraw_negative_amount_raises(self):
        account = BankAccount("Alice", 100)
        with pytest.raises(ValueError):
            account.withdraw(-5)


# ─────────────────────────────────────────────
# 3. Fixtures
# ─────────────────────────────────────────────

@pytest.fixture
def empty_account():
    """A fresh account with zero balance."""
    return BankAccount("Test User")


@pytest.fixture
def funded_account():
    """An account pre-loaded with $1000."""
    return BankAccount("Test User", 1000)


@pytest.fixture
def cart_with_items():
    """A cart with 3 items pre-loaded."""
    cart = ShoppingCart()
    cart.add_item("apple", 1.50, 3)
    cart.add_item("bread", 2.99)
    cart.add_item("milk", 3.49, 2)
    return cart


class TestWithFixtures:

    def test_empty_account_has_no_transactions(self, empty_account):
        assert empty_account.transaction_count() == 0

    def test_deposit_on_empty_account(self, empty_account):
        empty_account.deposit(500)
        assert empty_account.balance == 500

    def test_funded_account_can_withdraw_full_amount(self, funded_account):
        funded_account.withdraw(1000)
        assert funded_account.balance == 0

    def test_cart_total(self, cart_with_items):
        # 3×1.50 + 1×2.99 + 2×3.49 = 4.50 + 2.99 + 6.98 = 14.47
        assert cart_with_items.total() == pytest.approx(14.47)

    def test_cart_item_count(self, cart_with_items):
        assert cart_with_items.item_count() == 6  # 3 + 1 + 2

    def test_cart_remove_item(self, cart_with_items):
        cart_with_items.remove_item("bread")
        assert cart_with_items.total() == pytest.approx(11.48)


# ─────────────────────────────────────────────
# 4. Parametrize
# ─────────────────────────────────────────────

@pytest.mark.parametrize("email, expected", [
    ("user@example.com",     True),
    ("user.name@domain.co",  True),
    ("user+tag@example.org", True),
    ("plainaddress",         False),
    ("@missing-user.com",    False),
    ("user@",                False),
    ("",                     False),
])
def test_email_validation(email, expected):
    assert is_valid_email(email) == expected


@pytest.mark.parametrize("principal, rate, years, expected", [
    (1000, 0.05, 1,  pytest.approx(1050.0)),
    (1000, 0.05, 2,  pytest.approx(1102.5)),
    (1000, 0.10, 10, pytest.approx(2593.74, rel=1e-3)),
    (500,  0.03, 0,  pytest.approx(500.0)),
    pytest.param(1000, 0.0, 5, pytest.approx(1000.0), id="zero-rate"),
])
def test_compound_interest(principal, rate, years, expected):
    result = calculate_compound_interest(principal, rate, years)
    assert result == expected


@pytest.mark.parametrize("amount", [1, 50, 999.99, 1000])
def test_deposit_valid_amounts(empty_account, amount):
    empty_account.deposit(amount)
    assert empty_account.balance == amount


@pytest.mark.parametrize("amount", [0, -1, -100, -0.01])
def test_deposit_invalid_amounts_raise(empty_account, amount):
    with pytest.raises(ValueError):
        empty_account.deposit(amount)


# ─────────────────────────────────────────────
# 5. Float comparison with pytest.approx
# ─────────────────────────────────────────────

def test_float_addition_approx():
    result = 0.1 + 0.2
    assert result == pytest.approx(0.3)          # passes (0.30000000000000004 ≈ 0.3)

def test_compound_interest_approx():
    result = calculate_compound_interest(1000, 0.05, 1)
    assert result == pytest.approx(1050.0, rel=1e-6)

def test_cart_total_with_floating_point():
    cart = ShoppingCart()
    for _ in range(10):
        cart.add_item(f"item_{_}", 0.1)
    assert cart.total() == pytest.approx(1.0)


# ─────────────────────────────────────────────
# 6. Module-scope fixture
# ─────────────────────────────────────────────

@pytest.fixture(scope="module")
def shared_user():
    """Created once for the entire module — expensive setup."""
    return User("alice smith", "alice@example.com", 25)


class TestUserDisplay:
    def test_display_name_is_title_case(self, shared_user):
        assert shared_user.display_name() == "Alice Smith"

    def test_adult_check_for_25_year_old(self, shared_user):
        assert shared_user.is_adult() is True

    def test_email_is_lowercase(self, shared_user):
        assert shared_user.email == "alice@example.com"


# ─────────────────────────────────────────────
# 7. Markers
# ─────────────────────────────────────────────

@pytest.mark.slow
def test_expensive_operation():
    """Run with: pytest -m slow  |  skip with: pytest -m 'not slow'"""
    import time
    time.sleep(0.001)
    assert True


@pytest.mark.skip(reason="Feature not yet implemented")
def test_unimplemented_feature():
    assert False  # never runs


@pytest.mark.xfail(reason="Known bug: issue #42")
def test_known_failure():
    assert 1 == 2  # expected to fail — not reported as error


# ─────────────────────────────────────────────
# 8. Class-based tests (autouse fixture)
# ─────────────────────────────────────────────

class TestShoppingCartWorkflow:
    """Test the complete cart lifecycle."""

    @pytest.fixture(autouse=True)
    def setup_cart(self):
        self.cart = ShoppingCart()

    def test_new_cart_is_empty(self):
        assert self.cart.is_empty()
        assert self.cart.total() == 0

    def test_add_single_item(self):
        self.cart.add_item("laptop", 999.99)
        assert not self.cart.is_empty()
        assert self.cart.total() == pytest.approx(999.99)

    def test_add_duplicate_increases_quantity(self):
        self.cart.add_item("apple", 0.50, 2)
        self.cart.add_item("apple", 0.50, 3)
        assert self.cart.item_count() == 5

    def test_remove_last_item_empties_cart(self):
        self.cart.add_item("apple", 0.50)
        self.cart.remove_item("apple")
        assert self.cart.is_empty()

    def test_remove_nonexistent_item_raises(self):
        with pytest.raises(KeyError, match="Widget"):
            self.cart.remove_item("Widget")

    def test_negative_price_raises(self):
        with pytest.raises(ValueError, match="cannot be negative"):
            self.cart.add_item("refund", -10.0)


# ─────────────────────────────────────────────
# 9. Testing file I/O with tmp_path
# ─────────────────────────────────────────────

def read_config(path: str) -> dict:
    """Read a simple KEY=VALUE config file."""
    config = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                config[k.strip()] = v.strip()
    return config


def test_read_config(tmp_path):
    """tmp_path is a pytest built-in fixture — unique temp dir per test."""
    config_file = tmp_path / "config.cfg"
    config_file.write_text("HOST=localhost\nPORT=5432\n# comment\nDB=mydb\n")

    result = read_config(str(config_file))

    assert result["HOST"] == "localhost"
    assert result["PORT"] == "5432"
    assert result["DB"] == "mydb"
    assert "#" not in result


def test_read_empty_config(tmp_path):
    config_file = tmp_path / "empty.cfg"
    config_file.write_text("")
    assert read_config(str(config_file)) == {}


# ─────────────────────────────────────────────
# Run: python pytest_examples.py
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
