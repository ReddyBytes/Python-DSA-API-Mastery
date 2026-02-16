# 🎯 Testing — Interview Preparation Guide  
From Unit Tests to Production Reliability

---

# 🧠 What Interviewers Actually Test

Testing questions test:

- Do you write testable code?
- Do you understand isolation?
- Can you mock external dependencies?
- Do you understand CI/CD?
- Can you design safe refactoring strategy?
- Do you think about edge cases?

Testing reflects engineering maturity.

---

# 🔹 Level 1: 0–2 Years Experience

Basic clarity expected.

---

## 1️⃣ What is unit testing?

Strong answer:

> Unit testing verifies the correctness of individual functions or classes in isolation.

Mention:
It focuses on small units of logic.

---

## 2️⃣ Difference between unit test and integration test?

Unit test:
Tests small component in isolation.

Integration test:
Tests multiple components working together.

Clear distinction is important.

---

## 3️⃣ What is pytest?

Strong answer:

> pytest is a modern Python testing framework that simplifies test writing using simple assert statements and supports fixtures, parameterization, and plugins.

Mention fixtures.

---

## 4️⃣ What is mocking?

Strong answer:

> Mocking replaces real dependencies like APIs or databases with fake objects during testing to isolate the unit under test.

Key idea:
Isolation.

---

# 🔹 Level 2: 2–5 Years Experience

Now interviewer expects:

- Test design reasoning
- Fixture clarity
- Mocking strategies
- Coverage awareness
- CI familiarity

---

## 5️⃣ Why is test isolation important?

Strong answer:

> Tests should not depend on shared state or execution order. Isolation ensures reliability and reproducibility.

Avoid flaky tests.

---

## 6️⃣ What are fixtures in pytest?

Fixtures provide reusable setup logic.

Example:

- Database connection
- Test data
- Temporary files

Mention:
Fixtures improve reusability and readability.

---

## 7️⃣ What is code coverage?

Strong answer:

> Code coverage measures how much of the codebase is executed during tests.

Important:
High coverage does not guarantee correctness.

Mention that 100% coverage can still miss edge cases.

---

## 8️⃣ What is TDD?

Test-Driven Development:

1. Write failing test
2. Write minimal code
3. Refactor

Benefit:
Improves design and clarity.

---

## 9️⃣ How do you test external API calls?

Strong answer:

> I mock external APIs using unittest.mock or pytest monkeypatch to simulate responses, ensuring tests are fast and independent of network availability.

Practical answer matters.

---

# 🔹 Level 3: 5–10 Years Experience

Now interview focuses on architecture and strategy.

---

## 🔟 How do you design testable code?

Strong answer:

> I design loosely coupled components, use dependency injection, avoid global state, and separate business logic from infrastructure code.

Testing influences architecture.

---

## 1️⃣1️⃣ What makes a test brittle?

- Testing internal implementation
- Hardcoded values
- Dependency on execution order
- External state dependency

Strong candidate recognizes fragility.

---

## 1️⃣2️⃣ How would you handle flaky tests?

Steps:

1. Identify randomness
2. Remove external dependencies
3. Add deterministic behavior
4. Review asynchronous timing issues
5. Improve isolation

Structured debugging answer wins.

---

## 1️⃣3️⃣ How do you test asynchronous code?

Strong answer:

> I use pytest-asyncio or event loop utilities to test async functions and ensure proper awaiting of coroutines.

Mention async testing tools.

---

## 1️⃣4️⃣ What role does testing play in CI/CD?

Strong answer:

> Tests run automatically in CI pipelines to prevent merging broken code. They act as quality gates before deployment.

Mention automation.

---

## 1️⃣5️⃣ How do you balance speed and coverage in large projects?

Strong answer:

> I prioritize fast unit tests for quick feedback and use integration tests selectively. Slow end-to-end tests run in CI pipelines, not during every local execution.

Shows pragmatic thinking.

---

# 🔥 Scenario-Based Questions

---

## Scenario 1:
Tests pass locally but fail in CI.

Possible causes:

- Environment differences
- Missing dependencies
- Hardcoded paths
- Timing issues
- OS differences

Need systematic investigation.

---

## Scenario 2:
Code coverage high but production bug occurred.

Why?

Coverage measures execution, not correctness.
Edge cases missing.
Assertions insufficient.

---

## Scenario 3:
Mocking hides real integration issue.

Cause:

Over-mocking.

Solution:
Add integration tests.

Balance unit and integration.

---

## Scenario 4:
Refactoring large module safely.

Approach:

1. Write tests first.
2. Ensure good coverage.
3. Refactor in small steps.
4. Run tests frequently.

Testing enables safe refactoring.

---

## Scenario 5:
Slow test suite delays development.

Solutions:

- Parallel test execution
- Reduce integration tests
- Mock heavy operations
- Optimize fixtures
- Separate fast and slow tests

Engineering productivity question.

---

# 🧠 How to Answer Like a Strong Candidate

Weak:

“I write tests.”

Strong:

> “I focus on writing isolated, fast, and deterministic unit tests. I mock external dependencies, use fixtures for reusable setup, and ensure tests run in CI pipelines before deployment. I avoid brittle tests by testing behavior instead of internal implementation.”

Structured.
Professional.
Practical.

---

# ⚠️ Common Weak Candidate Mistakes

- Confusing unit and integration tests
- Over-mocking everything
- Ignoring negative test cases
- Writing tests dependent on execution order
- Treating coverage as quality guarantee
- Skipping edge cases

Testing depth reflects engineering maturity.

---

# 🎯 Rapid-Fire Revision

- Unit test → isolated logic
- Integration test → components together
- Mocking → replace real dependencies
- Fixtures → reusable setup
- Coverage ≠ correctness
- TDD improves design
- CI runs tests automatically
- Isolated tests prevent flakiness
- Test behavior, not implementation

---

# 🏆 Final Interview Mindset

Testing questions evaluate:

- Professional discipline
- Code quality awareness
- Architecture maturity
- Production readiness

If you demonstrate:

- Structured thinking
- Practical experience
- Isolation clarity
- Mocking knowledge
- CI integration awareness
- Refactoring strategy

You appear as production-ready engineer.

Testing is not optional in serious engineering.

It is foundational.

---

# 🔁 Navigation

Previous:  
[17_testing/theory.md](./theory.md)

Next:  
[18_performance_optimization/theory.md](../18_performance_optimization/theory.md)

