"""
16_design_patterns/strategy.py
=================================
CONCEPT: Strategy — define a family of algorithms, encapsulate each one,
and make them interchangeable. The client selects the algorithm at runtime
without changing the code that uses it.
WHY THIS MATTERS: Avoids if/elif chains that grow with every new algorithm.
New strategies can be added without modifying existing code (Open/Closed
Principle). Used everywhere: sorting algorithms, payment processors, pricing
engines, authentication strategies, compression codecs.

Prerequisite: Modules 01–10 (OOP, ABCs, first-class functions, decorators)
"""

from __future__ import annotations
import math
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, Any

# =============================================================================
# SECTION 1: Classic Strategy — ABC + interchangeable implementations
# =============================================================================

# CONCEPT: Define an abstract base class (Strategy interface). Concrete
# strategies implement it. The Context holds a reference to the current strategy
# and delegates the algorithm to it. Swap strategies without changing the context.

print("=== Section 1: Classic Strategy — Sorting ===")

class SortStrategy(ABC):
    """Strategy interface for sorting algorithms."""

    @abstractmethod
    def sort(self, data: list) -> list:
        """Sort and return a NEW list — don't mutate the original."""
        ...

    @property
    @abstractmethod
    def name(self) -> str: ...


class BubbleSortStrategy(SortStrategy):
    """O(n²) — simple but slow. Good for nearly-sorted small data."""

    @property
    def name(self) -> str: return "Bubble Sort"

    def sort(self, data: list) -> list:
        result = list(data)
        n = len(result)
        for i in range(n):
            for j in range(0, n - i - 1):
                if result[j] > result[j + 1]:
                    result[j], result[j + 1] = result[j + 1], result[j]
        return result


class QuickSortStrategy(SortStrategy):
    """O(n log n) average — fast in practice for random data."""

    @property
    def name(self) -> str: return "Quick Sort"

    def sort(self, data: list) -> list:
        if len(data) <= 1:
            return list(data)
        pivot  = data[len(data) // 2]
        left   = [x for x in data if x < pivot]
        middle = [x for x in data if x == pivot]
        right  = [x for x in data if x > pivot]
        return self.sort(left) + middle + self.sort(right)


class TimSortStrategy(SortStrategy):
    """O(n log n) worst-case — Python's built-in sort. Best for production."""

    @property
    def name(self) -> str: return "Tim Sort (built-in)"

    def sort(self, data: list) -> list:
        return sorted(data)   # delegates to Python's C-level Timsort


class Sorter:
    """
    Context — uses a strategy but doesn't know which algorithm runs.
    Strategy can be replaced at any time via `.set_strategy()`.
    """

    def __init__(self, strategy: SortStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: SortStrategy) -> None:
        self._strategy = strategy

    def sort(self, data: list) -> list:
        start  = time.perf_counter()
        result = self._strategy.sort(data)
        elapsed = time.perf_counter() - start
        print(f"  [{self._strategy.name}] sorted {len(data)} items in {elapsed*1000:.3f}ms")
        return result


import random
data = [random.randint(0, 1000) for _ in range(200)]

sorter = Sorter(BubbleSortStrategy())
r1 = sorter.sort(data)

sorter.set_strategy(QuickSortStrategy())
r2 = sorter.sort(data)

sorter.set_strategy(TimSortStrategy())
r3 = sorter.sort(data)

print(f"  All produce identical results: {r1 == r2 == r3}")


# =============================================================================
# SECTION 2: Strategy with registry — runtime selection from config
# =============================================================================

# CONCEPT: Store strategies in a dict. Select strategy from config string.
# This powers plugin systems, API format negotiation, and routing.

print("\n=== Section 2: Payment Strategy with Registry ===")

@dataclass
class PaymentResult:
    success:       bool
    transaction_id: str
    amount:        float
    processor:     str
    fee:           float = 0.0

    @property
    def net_amount(self) -> float:
        return self.amount - self.fee


class PaymentStrategy(ABC):
    """Interface for all payment processors."""

    @abstractmethod
    def process(self, amount: float, card_token: str) -> PaymentResult: ...

    @abstractmethod
    def refund(self, transaction_id: str, amount: float) -> bool: ...


class PaymentRegistry:
    _strategies: dict[str, type[PaymentStrategy]] = {}

    @classmethod
    def register(cls, name: str):
        def decorator(strategy_cls):
            cls._strategies[name] = strategy_cls
            return strategy_cls
        return decorator

    @classmethod
    def get(cls, name: str) -> PaymentStrategy:
        if name not in cls._strategies:
            raise KeyError(f"Unknown payment method: {name!r}. "
                           f"Available: {list(cls._strategies)}")
        return cls._strategies[name]()


@PaymentRegistry.register("stripe")
class StripeStrategy(PaymentStrategy):
    FEE_RATE = 0.029   # 2.9% + $0.30

    def process(self, amount: float, card_token: str) -> PaymentResult:
        fee = round(amount * self.FEE_RATE + 0.30, 2)
        return PaymentResult(
            success=True,
            transaction_id=f"stripe_{card_token[:6]}_001",
            amount=amount,
            processor="Stripe",
            fee=fee,
        )

    def refund(self, transaction_id: str, amount: float) -> bool:
        print(f"  [Stripe] Refunding ${amount:.2f} for {transaction_id}")
        return True


@PaymentRegistry.register("paypal")
class PayPalStrategy(PaymentStrategy):
    FEE_RATE = 0.034   # 3.4% + $0.30

    def process(self, amount: float, card_token: str) -> PaymentResult:
        fee = round(amount * self.FEE_RATE + 0.30, 2)
        return PaymentResult(
            success=True,
            transaction_id=f"pp_{card_token[:6]}_A1",
            amount=amount,
            processor="PayPal",
            fee=fee,
        )

    def refund(self, transaction_id: str, amount: float) -> bool:
        print(f"  [PayPal] Refunding ${amount:.2f} for {transaction_id}")
        return True


@PaymentRegistry.register("crypto")
class CryptoStrategy(PaymentStrategy):
    FEE_RATE = 0.001   # 0.1% flat

    def process(self, amount: float, card_token: str) -> PaymentResult:
        fee = round(amount * self.FEE_RATE, 4)
        return PaymentResult(
            success=True,
            transaction_id=f"btc_{card_token[:8]}",
            amount=amount,
            processor="Bitcoin",
            fee=fee,
        )

    def refund(self, transaction_id: str, amount: float) -> bool:
        print(f"  [Crypto] Refunds not supported for {transaction_id}")
        return False


class Checkout:
    """Context — delegates to whatever strategy is configured."""

    def __init__(self, payment_method: str):
        self._strategy = PaymentRegistry.get(payment_method)

    def pay(self, amount: float, card_token: str) -> PaymentResult:
        result = self._strategy.process(amount, card_token)
        print(f"  [{result.processor}] ${amount:.2f} → "
              f"fee=${result.fee:.2f}, net=${result.net_amount:.2f} "
              f"| txn={result.transaction_id}")
        return result


for method in ["stripe", "paypal", "crypto"]:
    checkout = Checkout(method)
    checkout.pay(99.99, "tok_abc123def456")


# =============================================================================
# SECTION 3: Function-based Strategy — using callables (Pythonic)
# =============================================================================

# CONCEPT: In Python, first-class functions ARE strategies. You don't need a
# class hierarchy if each strategy is a pure function.
# Use ABC-based strategy when: strategies need state or shared helpers.
# Use callable strategy when: algorithms are stateless pure functions.

print("\n=== Section 3: Functional Strategy (callables) ===")

# Shipping cost strategies — each is a pure function
def standard_shipping(weight_kg: float, distance_km: float) -> float:
    return weight_kg * 0.5 + distance_km * 0.01

def express_shipping(weight_kg: float, distance_km: float) -> float:
    return (weight_kg * 1.2 + distance_km * 0.05) * 1.5

def free_shipping(weight_kg: float, distance_km: float) -> float:
    return 0.0

def overnight_shipping(weight_kg: float, distance_km: float) -> float:
    return weight_kg * 2.0 + 25.0   # flat fee + weight


@dataclass
class Order:
    item:     str
    weight:   float
    distance: float
    _shipping_fn: Callable = field(default=standard_shipping, repr=False)

    def set_shipping(self, fn: Callable) -> "Order":
        self._shipping_fn = fn
        return self   # fluent

    def shipping_cost(self) -> float:
        return self._shipping_fn(self.weight, self.distance)

    def total(self, item_price: float) -> float:
        return item_price + self.shipping_cost()


order = Order("Laptop", weight=2.5, distance=500)

strategies = [
    ("Standard",  standard_shipping),
    ("Express",   express_shipping),
    ("Free",      free_shipping),
    ("Overnight", overnight_shipping),
]

for name, fn in strategies:
    order.set_shipping(fn)
    print(f"  {name:10}: shipping=${order.shipping_cost():.2f}, "
          f"total=${order.total(999.99):.2f}")


# =============================================================================
# SECTION 4: Combined — strategy selection from config with callable
# =============================================================================

# CONCEPT: Build a compression/encoding pipeline where each stage
# can swap algorithms. Demonstrates real-world strategy composition.

print("\n=== Section 4: Pipeline with Composable Strategies ===")

# Data transform strategies (callable approach)
def no_transform(data: str) -> str:
    return data

def uppercase_transform(data: str) -> str:
    return data.upper()

def reverse_transform(data: str) -> str:
    return data[::-1]

def redact_transform(data: str) -> str:
    """Redact anything that looks like an email or phone."""
    import re
    data = re.sub(r"[\w\.-]+@[\w\.-]+", "[EMAIL]", data)
    data = re.sub(r"\d{3}[-.\s]?\d{3}[-.\s]?\d{4}", "[PHONE]", data)
    return data


class DataPipeline:
    """
    Pipeline of transform strategies applied in sequence.
    Each transform is a Callable[[str], str].
    """

    def __init__(self):
        self._stages: list[tuple[str, Callable]] = []

    def add_stage(self, name: str, transform: Callable) -> "DataPipeline":
        self._stages.append((name, transform))
        return self   # fluent interface

    def process(self, data: str) -> str:
        result = data
        for name, fn in self._stages:
            result = fn(result)
            print(f"  After [{name}]: {result[:50]}")
        return result


raw = "User alice@example.com called 555-123-4567 about their order."
print(f"  Input: {raw}")

pipeline = (DataPipeline()
            .add_stage("redact",    redact_transform)
            .add_stage("uppercase", uppercase_transform))

output = pipeline.process(raw)
print(f"  Output: {output}")


print("\n=== Strategy patterns complete ===")
print("Choosing the right Strategy form:")
print("  ABC class       → strategies need state, shared helpers, or many methods")
print("  Registry        → strategies selected from config/string at runtime")
print("  Pure functions  → stateless algorithms — simplest, most Pythonic")
print("  Pipeline        → compose N strategies in sequence")
print()
print("Open/Closed Principle: add new strategies by adding new code, not editing old code")
