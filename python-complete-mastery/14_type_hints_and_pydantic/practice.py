# 💻 Type Hints & Pydantic — Practice

# =============================================================================
# SECTION 1: Basic Type Hints
# =============================================================================

# Python type hints are purely for editors + static analysis (mypy/pyright).
# They are NOT enforced at runtime by Python itself.

def greet(name: str) -> str:
    return f"Hello, {name}"

def add(a: int, b: int) -> int:
    return a + b

def is_valid(value: str) -> bool:
    return len(value) > 0

def set_flag(on: bool) -> None:
    pass  # returns nothing — annotate as None

# Python will NOT raise for wrong types:
print(greet(999))       # → "Hello, 999" — Python doesn't enforce
print(add(1.5, 2.5))    # → 4.0 — Python runs fine


# ── Complex types ─────────────────────────────────────────────────────────────

from typing import Optional, Union, Any, Callable, Literal

# Modern Python 3.10+ syntax (no imports needed):
def find_user(user_id: int) -> str | None:
    return "Alice" if user_id == 1 else None

def parse(value: str | int) -> str:
    return str(value)

# Old typing module syntax (still valid, required for Python < 3.10):
def find_user_old(user_id: int) -> Optional[str]:
    return "Alice" if user_id == 1 else None

def parse_old(value: Union[str, int]) -> str:
    return str(value)

# Containers — both styles:
def process_names(names: list[str]) -> dict[str, int]:
    return {name: len(name) for name in names}

def get_coords() -> tuple[float, float]:
    return (51.5, -0.1)

# Literal — only specific values allowed:
def set_role(role: Literal["user", "assistant", "system"]) -> None:
    print(f"Role set to: {role}")

# Callable — function as argument:
def apply(fn: Callable[[str], int], value: str) -> int:
    return fn(value)

result = apply(len, "hello")
print(f"apply(len, 'hello') = {result}")   # → 5


# ── *args and **kwargs ────────────────────────────────────────────────────────

def log_messages(*messages: str) -> None:
    for msg in messages:
        print(f"[LOG] {msg}")

def create_record(**fields: Any) -> dict[str, Any]:
    return dict(fields)

log_messages("Starting up", "Connected to DB", "Ready")
record = create_record(name="Alice", age=30, active=True)
print(record)


# =============================================================================
# SECTION 2: TypedDict and dataclass
# =============================================================================

from typing import TypedDict
from dataclasses import dataclass, field

# TypedDict: a dict with a known, typed structure
class MessageDict(TypedDict):
    role: str
    content: str

msg_dict: MessageDict = {"role": "user", "content": "Hello"}
print(msg_dict["role"])   # IDE knows this is a str

# dataclass: a class with type hints and auto-generated __init__, __repr__, __eq__
@dataclass
class Config:
    model: str
    temperature: float = 0.7
    max_tokens: int = 1000
    stop_sequences: list[str] = field(default_factory=list)

cfg = Config(model="gpt-4o")
print(cfg)
# → Config(model='gpt-4o', temperature=0.7, max_tokens=1000, stop_sequences=[])

# Neither TypedDict nor dataclass validates at runtime:
bad_cfg = Config(model=123)   # stores 123 — no error raised
print(bad_cfg.model)           # → 123


# =============================================================================
# SECTION 3: Pydantic BaseModel — Core Usage
# =============================================================================

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic import ValidationError

print("\n" + "="*60)
print("SECTION 3: Pydantic BaseModel")
print("="*60)

class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str
    tokens: int = 0

# Creating a valid model:
msg = ChatMessage(role="user", content="What is Python?")
print(msg)
# → role='user' content='What is Python?' tokens=0

# Pydantic coerces compatible types — "42" → 42:
msg2 = ChatMessage(role="assistant", content="Python is great!", tokens="42")
print(f"tokens type: {type(msg2.tokens)}, value: {msg2.tokens}")
# → tokens type: <class 'int'>, value: 42

# Pydantic raises ValidationError for incompatible types:
print("\n--- Validation Error Example ---")
try:
    bad = ChatMessage(role="hacker", content="Exploit!")   # role not in Literal
except ValidationError as e:
    print(f"ValidationError caught: {e.error_count()} error(s)")
    print(e)

# Access fields like a regular object:
print(f"\nMessage role: {msg.role}")
print(f"Message content: {msg.content}")
print(f"Message tokens: {msg.tokens}")


# =============================================================================
# SECTION 4: Pydantic Models for an AI App
# =============================================================================

print("\n" + "="*60)
print("SECTION 4: AI App Models")
print("="*60)

from typing import Optional
from datetime import datetime


class RAGDocument(BaseModel):
    """A document chunk retrieved from a vector store."""
    doc_id: str
    content: str
    source: str                                      # e.g. "docs/guide.pdf"
    page: int | None = None
    score: float = Field(ge=0.0, le=1.0, description="Cosine similarity score")


class LLMRequest(BaseModel):
    """A request to be sent to an LLM API."""
    messages: list[ChatMessage]
    model: str = "gpt-4o"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1000, gt=0)
    context_documents: list[RAGDocument] = []
    stream: bool = False

    @field_validator("messages")
    @classmethod
    def messages_not_empty(cls, v: list) -> list:
        if not v:
            raise ValueError("messages list cannot be empty")
        return v


class TokenUsage(BaseModel):
    """Token usage returned by the LLM API."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class LLMResponse(BaseModel):
    """Parsed response from an LLM API call."""
    content: str
    model: str
    usage: TokenUsage                                # nested model
    finish_reason: str = "stop"
    latency_ms: float | None = None

    @property
    def cost_estimate_usd(self) -> float:
        """Rough cost estimate based on token usage (GPT-4o pricing)."""
        input_cost  = (self.usage.prompt_tokens     / 1_000_000) * 2.50
        output_cost = (self.usage.completion_tokens / 1_000_000) * 10.00
        return round(input_cost + output_cost, 6)


class RAGResult(BaseModel):
    """The result of a full RAG pipeline run."""
    query: str
    answer: str
    source_documents: list[RAGDocument]
    llm_response: LLMResponse
    created_at: datetime = Field(default_factory=datetime.now)

    @property
    def top_source(self) -> RAGDocument | None:
        """Return the highest-scoring source document."""
        if not self.source_documents:
            return None
        return max(self.source_documents, key=lambda d: d.score)


# Instantiate and explore:
doc1 = RAGDocument(
    doc_id="doc_001",
    content="Python is a high-level, interpreted programming language.",
    source="docs/python_intro.pdf",
    page=1,
    score=0.92,
)

doc2 = RAGDocument(
    doc_id="doc_002",
    content="Python was created by Guido van Rossum and first released in 1991.",
    source="docs/python_intro.pdf",
    page=2,
    score=0.87,
)

request = LLMRequest(
    messages=[
        ChatMessage(role="system", content="Answer the question using the provided context."),
        ChatMessage(role="user",   content="Who created Python and when?"),
    ],
    model="gpt-4o",
    temperature=0.3,
    context_documents=[doc1, doc2],
)

print(f"Request model: {request.model}")
print(f"Request messages: {len(request.messages)}")
print(f"Context docs: {len(request.context_documents)}")

# Nested model coercion: dict → TokenUsage automatically
response = LLMResponse(
    content="Python was created by Guido van Rossum and first released in 1991.",
    model="gpt-4o",
    usage={"prompt_tokens": 120, "completion_tokens": 25, "total_tokens": 145},
    latency_ms=342.5,
)

print(f"\nResponse: {response.content}")
print(f"Total tokens: {response.usage.total_tokens}")
print(f"Latency: {response.latency_ms}ms")
print(f"Est. cost: ${response.cost_estimate_usd}")
print(f"Usage type: {type(response.usage)}")   # <class 'TokenUsage'> — not a dict


# =============================================================================
# SECTION 5: Validation Examples — Errors
# =============================================================================

print("\n" + "="*60)
print("SECTION 5: Validation Errors")
print("="*60)

# Field constraint violation:
print("\n--- Field constraint violation ---")
try:
    bad_doc = RAGDocument(
        doc_id="x",
        content="Test",
        source="test.pdf",
        score=1.5,   # gt 1.0 — violates le=1.0
    )
except ValidationError as e:
    for err in e.errors():
        print(f"  Field: {err['loc']}")
        print(f"  Error: {err['msg']}")
        print(f"  Input: {err['input']}")

# Multiple errors at once:
print("\n--- Multiple validation errors ---")
try:
    bad_request = LLMRequest(
        messages=[],           # fails: messages_not_empty validator
        temperature=3.5,       # fails: le=2.0
        max_tokens=-10,        # fails: gt=0
    )
except ValidationError as e:
    print(f"Total errors: {e.error_count()}")
    for err in e.errors():
        print(f"  [{'.'.join(str(x) for x in err['loc'])}] {err['msg']}")

# Wrong type with no coercion path:
print("\n--- Type error with no coercion path ---")
try:
    bad_msg = ChatMessage(role="user", content=["not", "a", "string"])
except ValidationError as e:
    print(e)


# =============================================================================
# SECTION 6: model_dump and model_validate
# =============================================================================

print("\n" + "="*60)
print("SECTION 6: model_dump and model_validate")
print("="*60)

# model_dump(): export to dict
response_dict = response.model_dump()
print("model_dump():")
print(response_dict)

# Selective export:
print("\nmodel_dump(include={'content', 'model'}):")
print(response.model_dump(include={"content", "model"}))

print("\nmodel_dump(exclude={'latency_ms'}):")
print(response.model_dump(exclude={"latency_ms"}))

print("\nmodel_dump(exclude_none=True):")
resp_no_latency = LLMResponse(
    content="Hello",
    model="gpt-4o",
    usage={"prompt_tokens": 5, "completion_tokens": 3, "total_tokens": 8},
)
print(resp_no_latency.model_dump(exclude_none=True))

# model_dump_json(): export to JSON string
print("\nmodel_dump_json():")
print(response.model_dump_json())

# model_validate(): import from dict
print("\nmodel_validate() from dict:")
data = {
    "content": "Python was created by Guido van Rossum.",
    "model": "claude-3-5-sonnet-20241022",
    "usage": {"prompt_tokens": 80, "completion_tokens": 15, "total_tokens": 95},
    "finish_reason": "end_turn",
}
loaded = LLMResponse.model_validate(data)
print(f"Loaded: {loaded.model} — {loaded.usage.total_tokens} tokens")
print(f"Type of usage: {type(loaded.usage)}")   # <class 'TokenUsage'>

# model_validate_json(): import from JSON string
print("\nmodel_validate_json():")
json_str = '{"role": "user", "content": "Hello from JSON"}'
msg_from_json = ChatMessage.model_validate_json(json_str)
print(f"From JSON: {msg_from_json}")


# =============================================================================
# SECTION 7: model_json_schema — For LLM Structured Output / Function Calling
# =============================================================================

import json

print("\n" + "="*60)
print("SECTION 7: model_json_schema")
print("="*60)

# Generate JSON Schema from any Pydantic model:
schema = ChatMessage.model_json_schema()
print("ChatMessage schema:")
print(json.dumps(schema, indent=2))

# A more interesting schema for structured LLM output:
class SentimentResult(BaseModel):
    sentiment: Literal["positive", "negative", "neutral"]
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score 0–1")
    reasoning: str = Field(description="One sentence explaining the classification")
    keywords: list[str] = Field(default_factory=list, description="Key words that influenced the result")

print("\nSentimentResult schema:")
print(json.dumps(SentimentResult.model_json_schema(), indent=2))

# This is what you'd pass to OpenAI structured outputs:
# response = client.beta.chat.completions.parse(
#     model="gpt-4o",
#     messages=[...],
#     response_format=SentimentResult,
# )
# result = response.choices[0].message.parsed   # → SentimentResult instance


# =============================================================================
# SECTION 8: Realistic Example — Parsing a Simulated LLM API Response
# =============================================================================

print("\n" + "="*60)
print("SECTION 8: Parsing a Simulated LLM API Response")
print("="*60)

# Simulate the raw dict that openai.chat.completions.create() returns
# (simplified version of the actual OpenAI response structure)
raw_openai_response = {
    "id": "chatcmpl-abc123",
    "object": "chat.completion",
    "model": "gpt-4o-2024-08-06",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "Python was created by Guido van Rossum and first released in 1991.",
            },
            "finish_reason": "stop",
        }
    ],
    "usage": {
        "prompt_tokens": 45,
        "completion_tokens": 18,
        "total_tokens": 63,
    },
}


def parse_openai_response(raw: dict, latency_ms: float) -> LLMResponse:
    """
    Convert a raw OpenAI API response dict into a typed LLMResponse model.
    Pydantic validates all fields and converts the usage dict to TokenUsage.
    """
    return LLMResponse(
        content=raw["choices"][0]["message"]["content"],
        model=raw["model"],
        usage=raw["usage"],                        # dict auto-coerced to TokenUsage
        finish_reason=raw["choices"][0]["finish_reason"],
        latency_ms=latency_ms,
    )


parsed = parse_openai_response(raw_openai_response, latency_ms=287.4)

print(f"Content      : {parsed.content}")
print(f"Model        : {parsed.model}")
print(f"Finish reason: {parsed.finish_reason}")
print(f"Latency      : {parsed.latency_ms}ms")
print(f"Prompt tokens: {parsed.usage.prompt_tokens}")
print(f"Total tokens : {parsed.usage.total_tokens}")
print(f"Est. cost    : ${parsed.cost_estimate_usd}")
print(f"Usage type   : {type(parsed.usage)}")      # <class 'TokenUsage'>

# Now build a RAGResult tying everything together:
rag_result = RAGResult(
    query="Who created Python and when?",
    answer=parsed.content,
    source_documents=[doc1, doc2],
    llm_response=parsed,
)

print(f"\nRAG query       : {rag_result.query}")
print(f"RAG answer      : {rag_result.answer}")
print(f"Sources used    : {len(rag_result.source_documents)}")
print(f"Top source      : {rag_result.top_source.source} (score={rag_result.top_source.score})")
print(f"Created at      : {rag_result.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

# Export the whole result to a dict for storage:
output_dict = rag_result.model_dump(exclude_none=True)
print(f"\nSerialized keys : {list(output_dict.keys())}")

# Re-import from that dict:
reloaded = RAGResult.model_validate(output_dict)
print(f"Reloaded answer : {reloaded.answer[:50]}...")
print(f"Reloaded tokens : {reloaded.llm_response.usage.total_tokens}")
