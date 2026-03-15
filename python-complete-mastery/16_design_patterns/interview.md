# 🎯 Design Patterns — Interview Preparation Guide  
From Clean Code to Architectural Thinking

---

# 🧠 What Interviewers Actually Test

Design pattern questions test:

- Can you structure scalable systems?
- Do you understand decoupling?
- Can you reduce tight coupling?
- Do you know when to use patterns?
- Can you refactor messy code?

They are testing thinking,
not memorization.

---

# 🔹 Level 1: 0–2 Years Experience

Basic pattern awareness expected.

---

## 1️⃣ What is a design pattern?

Strong answer:

> A design pattern is a reusable solution to a common software design problem. It provides a structured approach to solving recurring architectural challenges.

Avoid:
“It is predefined code.”

It is a concept.

---

## 2️⃣ Why do we use design patterns?

- Improve maintainability
- Improve scalability
- Improve testability
- Reduce duplication
- Encourage best practices

---

## 3️⃣ What is Singleton?

Strong answer:

> Singleton ensures that only one instance of a class exists throughout the application.

Use cases:

- Logger
- Configuration
- Shared services

Important:

Mention testing challenges due to global state.

---

# 🔹 Level 2: 2–5 Years Experience

Now interviewer expects:

- Pattern reasoning
- Use-case clarity
- Trade-off awareness
- Clean abstraction explanation

---

## 4️⃣ What is Factory pattern?

Strong answer:

> Factory pattern centralizes object creation logic and decouples the client from concrete implementations.

Benefits:

- Easier extension
- Cleaner code
- Reduced conditionals

Mention Open/Closed principle.

---

## 5️⃣ What is Strategy pattern?

Strong answer:

> Strategy pattern allows selecting algorithms at runtime by encapsulating them inside interchangeable classes.

Used in:

- Payment methods
- Sorting algorithms
- Discount calculations

Key benefit:
Behavior can change without modifying context class.

---

## 6️⃣ What is Observer pattern?

Strong answer:

> Observer pattern defines a one-to-many dependency so that when one object changes state, all dependents are notified automatically.

Used in:

- Event systems
- Messaging
- UI frameworks

---

## 7️⃣ What is Dependency Injection?

Strong answer:

> Dependency Injection decouples classes by providing dependencies from outside instead of creating them internally.

Benefits:

- Improved testability
- Loose coupling
- Easier mocking

This is highly valued in interviews.

---

# 🔹 Level 3: 5–10 Years Experience

Now interview shifts to architecture maturity.

---

## 8️⃣ When should you NOT use Singleton?

Strong answer:

> Singleton introduces global state which can make testing difficult and increase coupling. It should be avoided when multiple instances might be required in future or when state isolation is important.

Shows mature thinking.

---

## 9️⃣ How does Strategy pattern support Open/Closed Principle?

Strong answer:

> Strategy allows adding new behaviors without modifying existing code, making the system open for extension but closed for modification.

Explicit SOLID reference is good.

---

## 🔟 How would you refactor large if-else block into pattern?

Example:

Many condition checks for payment type.

Refactor using:

- Factory to create object
- Strategy for behavior

Shows practical understanding.

---

## 1️⃣1️⃣ How does Dependency Injection improve testing?

Strong answer:

> By injecting dependencies, we can replace real implementations with mock or stub objects during testing, improving isolation and reducing reliance on external systems.

Interviewers love this answer.

---

## 1️⃣2️⃣ How would you implement plugin architecture?

Strong answer:

> I would use a combination of factory and strategy patterns, possibly combined with dynamic loading and dependency injection to register new plugins without modifying core logic.

Shows advanced system thinking.

---

# 🔥 Scenario-Based Questions

---

## Scenario 1:
You have growing if-else conditions to select behavior.

Solution:

Refactor using Strategy pattern.

Why?

Removes condition complexity.
Improves extensibility.

---

## Scenario 2:
Multiple modules need same configuration object.

Solution:

Singleton or centralized config injection.

But mention:
Be careful of global state.

---

## Scenario 3:
You need to notify multiple systems when event occurs.

Solution:

Observer pattern.

Decouples producer and consumers.

---

## Scenario 4:
Testing a service class is difficult due to database dependency.

Solution:

Apply Dependency Injection.

Inject mock DB.

---

## Scenario 5:
System must support multiple payment gateways in future.

Solution:

Factory + Strategy.

Factory creates payment strategy.
Context executes it.

Scalable architecture.

---

# 🧠 How to Answer Like a Strong Candidate

Weak:

“I use patterns to make code better.”

Strong:

> “I use design patterns when they simplify complexity and improve extensibility. For example, I prefer Strategy pattern to eliminate large conditional blocks, and Dependency Injection to decouple services and improve testability.”

Clear.
Practical.
Balanced.

---

# ⚠️ Common Weak Candidate Mistakes

- Memorizing definitions without understanding
- Overusing patterns unnecessarily
- Ignoring trade-offs
- Not linking patterns to SOLID principles
- Not explaining real-world examples

Interviewers prefer reasoning over memorization.

---

# 🎯 Rapid-Fire Revision

- Singleton → single instance
- Factory → centralized object creation
- Strategy → interchangeable behaviors
- Observer → event notification
- Dependency Injection → loose coupling
- Patterns improve scalability and maintainability
- Use patterns when complexity grows
- Avoid overengineering

---

# 🏆 Final Interview Mindset

Design pattern questions test:

- Architectural maturity
- Clean code thinking
- Extensibility reasoning
- Decoupling awareness
- Testing mindset

If you demonstrate:

- Clear explanation
- Real use cases
- Trade-off awareness
- SOLID principle connection
- Refactoring approach

You appear as senior engineer.

Design patterns are not about showing knowledge.

They are about designing systems that survive growth.

---

# 🔁 Navigation

Previous:  
[16_design_patterns/theory.md](./theory.md)

Next:  
[17_testing/theory.md](../17_testing/theory.md)

---

**[🏠 Back to README](../README.md)**

**Prev:** [← Dependency Injection](./dependency_injection.md) &nbsp;|&nbsp; **Next:** [Testing — Theory →](../17_testing/theory.md)

**Related Topics:** [Theory](./theory.md) · [Dependency Injection](./dependency_injection.md)
