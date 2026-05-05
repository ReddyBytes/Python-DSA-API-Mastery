"""
16_design_patterns/factory.py
================================
CONCEPT: Factory patterns — separating object CREATION from object USE.
The three levels: Simple Factory (function), Factory Method (subclass decides),
Abstract Factory (families of related objects).
WHY THIS MATTERS: When you need to create objects whose type is determined at
runtime (from config, user input, database), factories centralize that logic
and decouple callers from concrete classes. Adding a new type means adding a
new class — not modifying every caller.

Prerequisite: Modules 01–10 (OOP, ABCs, decorators)
"""

from __future__ import annotations
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

# =============================================================================
# SECTION 1: Simple Factory — a function that creates objects
# =============================================================================

# CONCEPT: The simplest form. A function (or class method) takes a type string
# and returns the appropriate object. Not technically a GoF pattern but
# ubiquitous in Python because it's clean and Pythonic.

print("=== Section 1: Simple Factory ===")

class Notification(ABC):
    """Base notification — concrete types differ in how they send."""

    @abstractmethod
    def send(self, message: str, recipient: str) -> dict:
        ...


class EmailNotification(Notification):
    def send(self, message: str, recipient: str) -> dict:
        return {"channel": "email", "to": recipient, "body": message, "sent": True}


class SMSNotification(Notification):
    def send(self, message: str, recipient: str) -> dict:
        return {"channel": "sms", "to": recipient, "text": message[:160], "sent": True}


class PushNotification(Notification):
    def send(self, message: str, recipient: str) -> dict:
        return {"channel": "push", "device": recipient, "payload": message}


def create_notification(channel: str) -> Notification:
    """
    Simple factory function.
    WHY: callers ask for "email" — they don't import EmailNotification directly.
    Adding a new channel = add a class + one line here. Callers unchanged.
    """
    factories = {
        "email": EmailNotification,
        "sms":   SMSNotification,
        "push":  PushNotification,
    }
    if channel not in factories:
        raise ValueError(f"Unknown channel: {channel!r}. Valid: {list(factories)}")
    return factories[channel]()


# Use: caller only knows the string "email" — not the concrete class
for channel in ["email", "sms", "push"]:
    notif = create_notification(channel)
    result = notif.send("Your order shipped!", "user@example.com")
    print(f"  {result['channel']:5}: {result}")


# =============================================================================
# SECTION 2: Factory with registry — self-registering classes
# =============================================================================

# CONCEPT: A registry maps string keys to classes. Classes register themselves
# via a decorator. Adding a new type = create the class + add @register.
# The factory function stays unchanged forever. This is the extensible version.

print("\n=== Section 2: Factory with Registry ===")

class ReportFactory:
    """
    Self-registering factory for report generators.
    Each report class registers itself — factory code never needs to change.
    """
    _registry: dict[str, type] = {}

    @classmethod
    def register(cls, name: str):
        """Decorator: @ReportFactory.register("pdf") registers the class."""
        def decorator(report_cls):
            cls._registry[name] = report_cls
            return report_cls
        return decorator

    @classmethod
    def create(cls, report_type: str, **config) -> "Report":
        if report_type not in cls._registry:
            available = list(cls._registry.keys())
            raise KeyError(f"Unknown report type: {report_type!r}. Available: {available}")
        return cls._registry[report_type](**config)

    @classmethod
    def available_types(cls) -> list:
        return list(cls._registry.keys())


class Report(ABC):
    @abstractmethod
    def render(self, data: list) -> str: ...


@ReportFactory.register("csv")
class CSVReport(Report):
    def __init__(self, delimiter: str = ","):
        self.delimiter = delimiter

    def render(self, data: list) -> str:
        if not data:
            return ""
        headers = self.delimiter.join(data[0].keys())
        rows    = [self.delimiter.join(str(v) for v in row.values()) for row in data]
        return "\n".join([headers] + rows)


@ReportFactory.register("json")
class JSONReport(Report):
    def __init__(self, indent: int = 2):
        self.indent = indent

    def render(self, data: list) -> str:
        return json.dumps(data, indent=self.indent)


@ReportFactory.register("html")
class HTMLReport(Report):
    def render(self, data: list) -> str:
        if not data:
            return "<table></table>"
        headers = "".join(f"<th>{k}</th>" for k in data[0].keys())
        rows    = "".join(
            "<tr>" + "".join(f"<td>{v}</td>" for v in row.values()) + "</tr>"
            for row in data
        )
        return f"<table><thead><tr>{headers}</tr></thead><tbody>{rows}</tbody></table>"


sample_data = [
    {"id": 1, "name": "Alice", "score": 95},
    {"id": 2, "name": "Bob",   "score": 87},
]

print(f"  Available types: {ReportFactory.available_types()}")

for rtype in ["csv", "json", "html"]:
    report = ReportFactory.create(rtype)
    output = report.render(sample_data)
    print(f"\n  [{rtype.upper()} Report]")
    print("  " + output.replace("\n", "\n  ")[:120])


# =============================================================================
# SECTION 3: Factory Method — the GoF pattern via subclasses
# =============================================================================

# CONCEPT: Factory Method defines an interface for creating an object but lets
# SUBCLASSES decide which class to instantiate. The creator class has a
# `create_X()` method that subclasses override.
# WHY: the framework defines the algorithm skeleton; the plugin defines what
# objects get created. Used heavily in Django (form factories, model factories).

print("\n\n=== Section 3: Factory Method Pattern ===")

class DataParser(ABC):
    """
    Creator — defines the pipeline, delegates object creation to subclasses.
    The `create_reader()` and `create_validator()` are the factory methods.
    """

    @abstractmethod
    def create_reader(self) -> "DataReader":
        """Factory method — subclass decides what reader to create."""
        ...

    @abstractmethod
    def create_validator(self) -> "DataValidator":
        """Factory method — subclass decides what validator to create."""
        ...

    def process(self, raw_input: str) -> dict:
        """
        Template method — algorithm stays the same for all subclasses.
        Only the created objects (reader, validator) differ.
        """
        reader    = self.create_reader()
        validator = self.create_validator()

        data   = reader.read(raw_input)
        errors = validator.validate(data)
        return {"data": data, "errors": errors, "valid": len(errors) == 0}


class DataReader(ABC):
    @abstractmethod
    def read(self, raw: str) -> list: ...


class DataValidator(ABC):
    @abstractmethod
    def validate(self, data: list) -> list: ...


# Concrete implementations
class JSONReader(DataReader):
    def read(self, raw: str) -> list:
        return json.loads(raw)


class CSVReader(DataReader):
    def read(self, raw: str) -> list:
        lines = raw.strip().split("\n")
        headers = lines[0].split(",")
        return [dict(zip(headers, line.split(","))) for line in lines[1:]]


class SchemaValidator(DataValidator):
    def __init__(self, required_fields: list):
        self.required = required_fields

    def validate(self, data: list) -> list:
        errors = []
        for i, row in enumerate(data):
            for field in self.required:
                if field not in row or not row[field]:
                    errors.append(f"Row {i}: missing required field '{field}'")
        return errors


# Concrete creators — each overrides the factory methods
class JSONParser(DataParser):
    def create_reader(self)    -> DataReader:    return JSONReader()
    def create_validator(self) -> DataValidator: return SchemaValidator(["id", "name"])


class CSVParser(DataParser):
    def create_reader(self)    -> DataReader:    return CSVReader()
    def create_validator(self) -> DataValidator: return SchemaValidator(["id", "name"])


json_input = '[{"id": "1", "name": "Alice"}, {"id": "2", "name": ""}]'
csv_input  = "id,name,score\n1,Alice,95\n2,Bob,87"

for parser, raw in [(JSONParser(), json_input), (CSVParser(), csv_input)]:
    result = parser.process(raw)
    print(f"  {parser.__class__.__name__}: {len(result['data'])} rows, "
          f"valid={result['valid']}, errors={result['errors']}")


# =============================================================================
# SECTION 4: Abstract Factory — families of related objects
# =============================================================================

# CONCEPT: Abstract Factory creates FAMILIES of related objects.
# Instead of one factory method, you have multiple — one per product type.
# The concrete factory decides the entire "theme" (e.g., dark mode vs light mode).
# Change the factory → change the whole family at once.

print("\n=== Section 4: Abstract Factory ===")

# Product interfaces
class Button(ABC):
    @abstractmethod
    def render(self) -> str: ...

class TextField(ABC):
    @abstractmethod
    def render(self) -> str: ...

class Dialog(ABC):
    @abstractmethod
    def render(self) -> str: ...


# Abstract Factory
class UIFactory(ABC):
    """Creates a family of UI components — all consistent with one theme."""

    @abstractmethod
    def create_button(self, label: str)    -> Button:    ...
    @abstractmethod
    def create_text_field(self, placeholder: str) -> TextField: ...
    @abstractmethod
    def create_dialog(self, title: str)    -> Dialog:    ...


# Light theme family
class LightButton(Button):
    def __init__(self, label: str): self.label = label
    def render(self) -> str: return f"[  {self.label}  ] (light)"

class LightTextField(TextField):
    def __init__(self, placeholder: str): self.placeholder = placeholder
    def render(self) -> str: return f"[ {self.placeholder}... ] (light)"

class LightDialog(Dialog):
    def __init__(self, title: str): self.title = title
    def render(self) -> str: return f"╔══ {self.title} ══╗ (light)"


# Dark theme family
class DarkButton(Button):
    def __init__(self, label: str): self.label = label
    def render(self) -> str: return f"▓▓ {self.label} ▓▓ (dark)"

class DarkTextField(TextField):
    def __init__(self, placeholder: str): self.placeholder = placeholder
    def render(self) -> str: return f"▓ {self.placeholder}... ▓ (dark)"

class DarkDialog(Dialog):
    def __init__(self, title: str): self.title = title
    def render(self) -> str: return f"█══ {self.title} ══█ (dark)"


# Concrete factories
class LightThemeFactory(UIFactory):
    def create_button(self, label):       return LightButton(label)
    def create_text_field(self, placeholder): return LightTextField(placeholder)
    def create_dialog(self, title):       return LightDialog(title)


class DarkThemeFactory(UIFactory):
    def create_button(self, label):       return DarkButton(label)
    def create_text_field(self, placeholder): return DarkTextField(placeholder)
    def create_dialog(self, title):       return DarkDialog(title)


def build_login_form(factory: UIFactory) -> None:
    """
    Client code — uses the abstract factory interface only.
    Doesn't know or care which theme is active.
    """
    dialog    = factory.create_dialog("Login")
    username  = factory.create_text_field("Username")
    password  = factory.create_text_field("Password")
    submit    = factory.create_button("Sign In")

    print(f"  {dialog.render()}")
    print(f"  {username.render()}")
    print(f"  {password.render()}")
    print(f"  {submit.render()}")


for factory_cls in [LightThemeFactory, DarkThemeFactory]:
    print(f"\n  --- {factory_cls.__name__} ---")
    build_login_form(factory_cls())


print("\n=== Factory patterns complete ===")
print("Pattern guide:")
print("  Simple Factory    → a function mapping string → object (most common)")
print("  Registry Factory  → self-registering, open for extension")
print("  Factory Method    → subclass decides what to create (GoF, frameworks)")
print("  Abstract Factory  → create families of related objects (UI themes, DBs)")
