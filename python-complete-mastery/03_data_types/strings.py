"""
==============================================================
PYTHON STRINGS – COMPLETE FUNDAMENTALS + DEEP REVISION FILE
==============================================================

This file is structured as INTERVIEW REVISION MATERIAL.

It contains:
✔ Concept explanations
✔ Memory behavior
✔ Immutability deep dive
✔ Performance impact
✔ Hashing logic
✔ Unicode behavior
✔ Indexing & slicing mastery
✔ Case methods
✔ Real-world development insights
✔ strip() / lstrip() / rstrip()
✔ split() / rsplit()
✔ join()
✔ replace()
✔ find() vs index()
✔ count()
✔ startswith() / endswith()
✔ Validation methods (isalpha, isdigit, etc.)
✔ Edge cases & interview traps

Study this file slowly before interviews.
==============================================================
"""


# ==============================================================
# 1️⃣ WHAT IS A STRING?
# ==============================================================

"""
A string in Python:
- Is an object of type 'str'
- Is stored in heap memory
- Variable holds a reference to the object
- Is IMMUTABLE (cannot be modified in-place)
"""

# s = "hello"
# print(type(s))  # <class 'str'>

"""
Memory Model:

s  ---->  "hello"

The variable does NOT store characters.
It stores a reference to the string object.
"""


# ==============================================================
# 2️⃣ STRING CREATION METHODS
# ==============================================================

"""
Python allows:
- Single quotes
- Double quotes
- Triple quotes
"""

a = 'hello'
b = "hello"
c = """multi-line
string"""

"""
There is NO internal difference between single and double quotes.
Triple quotes are mainly used for:
- Multi-line strings
- Docstrings
"""


# ==============================================================
# 3️⃣ ESCAPE SEQUENCES
# ==============================================================

"""
Escape sequences allow special characters inside strings.

\n  → New line
\t  → Tab
\\  → Backslash
\"  → Double quote
\'  → Single quote
"""

# print("Hello\nWorld")

"""
Important:
'\n' is ONE character internally.
"""

# print(len("Hello\nWorld"))  # newline counts as 1 character


# ==============================================================
# 4️⃣ RAW STRINGS
# ==============================================================

"""
Raw strings ignore escape processing.

Used mainly for:
- Windows paths
- Regex patterns
"""

# print(r"Hello\nWorld")

"""
Important:
Raw strings cannot end with a single backslash.
r"C:\folder\"  -> SyntaxError
"""


# ==============================================================
# 5️⃣ STRING IMMUTABILITY
# ==============================================================

"""
Strings cannot be modified in-place.
"""

s = "hello"

# s[0] = "H"  # TypeError

"""
Correct approach:
Create a NEW string.
"""

s = "H" + s[1:]
# print(s)

"""
Immutability means:
- Every modification creates a NEW object.
- Original object remains unchanged.
"""


# ==============================================================
# 6️⃣ MEMORY BEHAVIOR & REFERENCES
# ==============================================================

s = "python"
t = s

"""
Both variables reference SAME object.
"""

# print(s is t)  # Often True (string interning)

"""
If we modify s:
"""

s = s + "3"

"""
Now:
t → "python"
s → "python3"

Original object remains if at least one reference exists.
"""


# ==============================================================
# 7️⃣ PERFORMANCE IMPACT OF IMMUTABILITY
# ==============================================================

"""
Repeated string concatenation is inefficient.

Example:
"""

s = ""
for i in range(5):
    s = s + "a"

"""
Why inefficient?

Each iteration:
- Allocates new memory
- Copies entire old string
- Appends new char

Total complexity ≈ O(n²)
"""

"""
Efficient approach:
Use list + join
"""

chars = []
for i in range(5):
    chars.append("a")

s = "".join(chars)

"""
append() → O(1)
join()   → O(n)

Total complexity → O(n)
"""


# ==============================================================
# 8️⃣ HASHING & DICTIONARY CONNECTION
# ==============================================================

"""
hash() returns an integer representation of object content.

Strings are hashable because they are immutable.
"""

# print(hash("python"))

"""
Dictionary internally stores:
- hash(key)
- reference to key
- reference to value

Immutability guarantees:
Hash never changes → Dictionary remains stable.
"""

data = {"name": "reddy"}


# ==============================================================
# 9️⃣ UNICODE BEHAVIOR
# ==============================================================

"""
Python 3 strings are Unicode by default.

They can store:
- English
- Telugu
- Hindi
- Emojis
- Any global language
"""

# print(len("😊"))  # 1 character

"""
Case conversion may change length in Unicode.
"""

# print("ß".upper())       # SS
# print(len("ß".upper()))  # 2


# ==============================================================
# 🔟 BASIC STRING OPERATIONS
# ==============================================================

"""
Concatenation (+)
Repetition (*)
Membership (in)
"""

# print("hello" + " world")
# print("hi" * 3)

# print("py" in "python")
# print("" in "python")       # True
# print("python" in "")       # False


# ==============================================================
# 1️⃣1️⃣ INDEXING
# ==============================================================

s = "python"

"""
Indexing:
0 1 2 3 4 5
p y t h o n
"""

# print(s[0])    # p
# print(s[-1])   # n

"""
Valid positive index: 0 → len(s)-1
Valid negative index: -1 → -len(s)
"""


# ==============================================================
# 1️⃣2️⃣ SLICING
# ==============================================================

"""
Syntax:
s[start:end]
Includes start
Excludes end
"""

# print(s[0:2])   # py
# print(s[:3])    # pyt
# print(s[3:])    # hon
# print(s[1:1])   # ""
# print(s[4:2])   # ""

"""
Step slicing:
s[start:end:step]
"""

# print(s[::2])    # pto
# print(s[::-1])   # reverse string
# print(s[::-2])   # nhy

"""
Rules:
- Positive step → move left to right
- Negative step → move right to left
- Wrong direction → empty string
"""


# ==============================================================
# 1️⃣3️⃣ CASE METHODS (FREQUENTLY USED IN DEVELOPMENT)
# ==============================================================

"""
lower() → converts to lowercase
upper() → converts to uppercase

Important:
These DO NOT modify original string.
They return NEW string.
"""

s = "HELLO"

# print(s.lower())  # hello
# print(s)          # HELLO (unchanged)

"""
Real-world usage:
- User input normalization
- Case-insensitive comparisons
"""

username = "Admin"
# print(username.lower() == "admin")  # True



# =============================================================================
# 1️⃣ STRIP FAMILY
# =============================================================================

"""
strip() removes whitespace from BOTH ends of the string.

Whitespace includes:
- Space
- \n (newline)
- \t (tab)

IMPORTANT:
strip() does NOT remove characters in the middle.
"""

s = "   hello   "
# print(s.strip())   # 'hello'
# print(s.lstrip())  # 'hello   '
# print(s.rstrip())  # '   hello'


"""
strip() can remove specific characters.

IMPORTANT:
It removes characters individually, NOT substring.
"""

# print("cabhelloabc".strip("abc"))  
# Output: 'hello'

"""
Explanation:
Removes any combination of 'a', 'b', 'c' from both ends.
Stops when first non-matching character appears.
"""


# =============================================================================
# 2️⃣ SPLIT & RSPLIT
# =============================================================================

"""
split() breaks string into list.

Default behavior:
- Splits on ANY whitespace
- Merges multiple spaces
- Ignores leading/trailing whitespace
"""

s = "   one   two   "
# print(s.split())  
# ['one', 'two']


"""
split(" ") behaves differently:
- Splits at EVERY literal space
- Produces empty strings
"""

# print(s.split(" "))


"""
Custom separator:
"""

# print("a,b,c".split(","))  
# ['a', 'b', 'c']


"""
Consecutive separators create empty strings.
"""

# print("one,two,,three".split(","))  
# ['one', 'two', '', 'three']


"""
maxsplit parameter:
"""

# print("one two three four".split(" ", 1))
# ['one', 'two three four']


"""
rsplit() splits from RIGHT side.
"""

# print("one two three four".rsplit(" ", 1))
# ['one two three', 'four']


# =============================================================================
# 3️⃣ JOIN
# =============================================================================

"""
separator.join(iterable)

- Called on separator
- Inserts separator BETWEEN elements
- Never at beginning or end
- All elements must be strings
"""

# words = ["hello", "world"]
# print(" ".join(words))  
# # 'hello world'


# print(",".join(["a", "b", "c"]))  
# # 'a,b,c'


"""
String is iterable → joins character by character
"""

# print("-".join("abc"))  
# 'a-b-c'


"""
Edge cases:
"""

# print("X".join([]))        # ''
# print("X".join(["a"]))     # 'a'
# print("-".join(["a", "", "b"]))  # 'a--b'


"""
Performance Insight:
Use join() instead of += in loop to avoid O(n²).
"""


# =============================================================================
# 4️⃣ REPLACE
# =============================================================================

"""
replace(old, new, count)

- Replaces non-overlapping occurrences
- Case-sensitive
- Returns new string
"""

# print("apple apple".replace("apple", "orange"))
# # 'orange orange'


# print("apple apple".replace("apple", "orange", 1))
# # 'orange apple'


"""
Non-overlapping behavior:
"""

# print("aaaa".replace("aa", "b"))  
# # 'bb'

# print("aaa".replace("aa", "b"))  
# 'ba'


# =============================================================================
# 5️⃣ FIND vs INDEX
# =============================================================================

"""
find() → returns index OR -1
index() → returns index OR raises ValueError
"""

# s = "hello world"

# print(s.find("world"))   # 6
# print(s.find("python"))  # -1

# print(s.index("python"))  # ValueError


"""
Best practice to check existence:
"""

# print("world" in s)  # True


# =============================================================================
# 6️⃣ COUNT
# =============================================================================

"""
Counts non-overlapping occurrences.
"""

# print("banana".count("a"))  
# # 3

# print("aaaa".count("aa"))  
# # 2


# =============================================================================
# 7️⃣ STARTSWITH & ENDSWITH
# =============================================================================

s = "hello world"

# print(s.startswith("hello"))  # True
# print(s.endswith("world"))    # True


"""
Supports tuple of prefixes/suffixes:
"""

# filename = "report.pdf"
# print(filename.endswith((".pdf", ".docx")))  
# # True


# =============================================================================
# 8️⃣ VALIDATION METHODS
# =============================================================================

"""
All is*() methods return True only if:
1. String is NOT empty
2. ALL characters satisfy condition
"""

# print("hello".isalpha())      # True
# print("hello123".isalpha())   # False

# print("123".isdigit())        # True
# print("-123".isdigit())       # False
# print("²".isdigit())          # True (Unicode digit)

# print("abc123".isalnum())     # True
# print("abc 123".isalnum())    # False

# print("   ".isspace())        # True
# print("".isspace())           # False


# =============================================================================
# 9️⃣ REAL-WORLD VALIDATION EXAMPLE
# =============================================================================

# sample = "   test@example.com   "

# cleaned = sample.strip()

# if "@" in cleaned and cleaned.endswith(".com"):
#     print("Valid email format")
# else:
#     print("Invalid email format")

"""
===============================================================================
PYTHON STRINGS – DAY 3 ADVANCED CONCEPTS
(Formatting, Encoding, ord/chr, Interning, Identity vs Equality)

This file covers everything learned AFTER string methods.
Interview-focused and production-relevant.
===============================================================================
"""

# =============================================================================
# 1️⃣ F-STRINGS (Modern Formatting)
# =============================================================================

"""
f-strings allow embedding expressions inside strings.

Syntax:
f"Text {expression}"

- Supports variables
- Supports arithmetic
- Supports method calls
- Evaluates expressions directly
"""

# name = "Reddy"
# age = 25
# print(f"My name is {name} and I am {age} years old")

# # Expressions inside {}
# a = 10
# b = 5
# print(f"Sum is {a + b}")

# # Method calls inside {}
# print(f"Uppercase: {name.upper()}")


# =============================================================================
# 2️⃣ FORMAT CONTROL (Precision & Width)
# =============================================================================

"""
Decimal Precision:
:.2f → 2 decimal places (rounded)
"""

# value = 3.14159
# print(f"{value:.2f}")   # 3.14

# value = 3.1
# print(f"{value:.2f}")   # 3.10


"""
Width & Alignment:

<  → Left align
>  → Right align
^  → Center align
"""

# num = 42
# print(f"{num:5}")     # Right aligned (default for numbers)
# print(f"{num:<5}")    # Left aligned
# print(f"{num:^5}")    # Center aligned

"""
Zero Padding:
"""

# print(f"{num:0>5}")   # 00042


# =============================================================================
# 3️⃣ ENCODING & DECODING
# =============================================================================

"""
Python strings (str) are Unicode.
Computers store data as bytes.

encode() → str → bytes
decode() → bytes → str
"""

# s = "hello"
# b = s.encode()
# print(type(s))  # <class 'str'>
# print(type(b))  # <class 'bytes'>

# print(b.decode())  # hello


# =============================================================================
# 4️⃣ ASCII vs UTF-8
# =============================================================================

"""
ASCII:
- 128 characters (0–127)
- English letters, digits, symbols

UTF-8:
- Supports all Unicode characters
- Default in Python
- Backward compatible with ASCII
"""

# print("hello".encode("ascii"))
# print("hello".encode("utf-8"))

"""
This fails because 'é' is not in ASCII:
"""

# print("café".encode("ascii"))  # UnicodeEncodeError


"""
UTF-8 supports extended characters:
"""

# print("café".encode("utf-8"))
# print("😊".encode("utf-8"))


# =============================================================================
# 5️⃣ ERROR HANDLING IN ENCODING
# =============================================================================

"""
Error strategies:

strict  → default (raises error)
ignore  → skips unsupported characters
replace → replaces with '?'
"""

s = "café"

# print(s.encode("ascii", "ignore").decode("ascii"))   # caf
# print(s.encode("ascii", "replace").decode("ascii"))  # caf?


# =============================================================================
# 6️⃣ CHARACTER vs BYTE LENGTH
# =============================================================================

"""
len(str) → character count
len(bytes) → byte count
"""

# print(len("😊"))               # 1 character
# print(len("😊".encode()))      # 4 bytes in UTF-8


# =============================================================================
# 7️⃣ ord() and chr()
# =============================================================================

"""
ord() → character → Unicode code point
chr() → integer → character
"""

# print(ord("A"))   # 65
# print(chr(65))    # 'A'

"""
Uppercase and lowercase difference:
"""

# print(ord("a") - ord("A"))  # 32

"""
Character shifting:
"""

# print(chr(ord("B") + 1))    # C
# print(chr(ord("A") + 32))   # a

"""
Important:
No automatic wraparound.
"""

# print(chr(ord("z") + 1))    # '{'


# =============================================================================
# 8️⃣ STRING INTERNING
# =============================================================================

"""
Python may reuse string literals to save memory.
This is called interning.
"""

# a = "hello"
# b = "hello"
# print(a is b)  # Often True

"""
Compile-time concatenation (constant folding):
"""

# x = "hello world"
# y = "hello " + "world"
# print(x is y)  # Usually True


"""
Runtime concatenation:
"""

# part1 = "hello "
# part2 = "world"
# z = part1 + part2

# print(x == z)  # True (same value)
# print(x is z)  # False (different objects)


# =============================================================================
# 9️⃣ == vs is (CRITICAL INTERVIEW POINT)
# =============================================================================

"""
==  → checks value equality
is  → checks object identity (memory reference)
"""

# a = "python"
# b = "".join(["py", "thon"])

# print(a == b)  # True
# print(a is b)  # False

"""
Never use 'is' for string comparison.
Use '=='.
Use 'is' only for identity checks like:
"""

# x = None
# print(x is None)  # Correct usage


# ==============================================================
# 🧠 CORE INTERVIEW TAKEAWAYS
# ==============================================================

"""
✔ Strings are immutable.
✔ Every modification creates new object.
✔ Repeated concatenation → O(n²).
✔ Use list + join for efficiency → O(n).
✔ Strings are hashable because immutable.
✔ Dictionary uses hash for O(1) lookup.
✔ Strings are Unicode by default.
✔ Case methods return new strings.
✔ Slicing never raises IndexError.
✔ Indexing can raise IndexError.
✔ strip() removes characters from ends, not middle
✔ split() vs split(" ") difference is critical
✔ rsplit() useful for parsing from right
✔ join() inserts separator between elements only
✔ replace() and count() are non-overlapping
✔ find() returns -1, index() raises error
✔ startswith()/endswith() support tuple
✔ isdigit() is Unicode-aware
✔ is*() methods return False for empty string
✔ Use "in" for existence checking
✔ f-strings support expressions and formatting
✔ : .2f controls decimal precision
✔ Width and alignment control formatting
✔ encode() converts str → bytes
✔ decode() converts bytes → str
✔ ASCII is limited; UTF-8 supports Unicode
✔ UTF-8 is backward compatible with ASCII
✔ ord() and chr() convert between characters and numbers
✔ Strings may be interned at compile time
✔ Runtime concatenation creates new objects
✔ Always use '==' for string comparison
✔ Use 'is' only for identity (like None)
"""

"""
==============================================================
END OF STRING FUNDAMENTALS + IMMUTABILITY + HASHING REVISION
==============================================================
"""




# 1️⃣ Reverse a string (without slicing)

# with slicing 

# input_string=input("enter the string to reverse : ").strip().lower()
# revesed_string=input_string[::-1]
# print(reversed_string)

# without slicing
# input_string=input("enter the string to reverse: ").strip().lower()
# reversed_string=""
# for word in range(len(input_string)-1,-1,-1):
#     reversed_string+=input_string[word]
# print(reversed_string)



###############################################################################

# 2️⃣ Check if string is palindrome (ignore case + spaces)

# input_string=input("enter the word to check palindrome : ").strip().lower()
# revesed_string=input_string[::-1]
# if input_string==revesed_string:
#     print(f"{input_string} is a palindrome")
# else:
#     print(f"{input_string} is not a palindrome")


###############################################################################
# 3️⃣ Count vowels and consonants
# s="ooaaee"
# vowels=["a","e","i","o","u"]
# sum=0
# for i in range(len(s)):
#     if s[i] in vowels:
#         sum+=1
# print(f"vowels are {sum} and constants are {len(s)-sum}")



###############################################################################

# 4️⃣ Count frequency of each character


###############################################################################
# 5️⃣ Remove all duplicate characters (keep order)

###############################################################################
# 🟡 LEVEL 2 – Indexing & Slicing Mastery

###############################################################################
# 6️⃣ Print characters at even indices

###############################################################################
# 7️⃣ Print characters at odd indices

###############################################################################
# 8️⃣ Reverse words in a sentence
# Example:

# "I love python" → "python love I"

###############################################################################
# 9️⃣ Swap first and last character of string

###############################################################################
# 🔟 Find longest word in sentence

###############################################################################
# 🟠 LEVEL 3 – Methods + Logic

# 1️⃣1️⃣ Count occurrences of a substring (without using count())

###############################################################################
# 1️⃣2️⃣ Replace all spaces with hyphen (without using replace())

###############################################################################
# 1️⃣3️⃣ Find first non-repeating character

###############################################################################
# 1️⃣4️⃣ Check if two strings are anagrams

###############################################################################
# 1️⃣5️⃣ Remove all special characters (keep only alphanumeric)

###############################################################################
# 🔵 LEVEL 4 – Validation + Real-world

###############################################################################
# 1️⃣6️⃣ Validate email format (basic version)

###############################################################################
# 1️⃣7️⃣ Check if string contains only digits (without isdigit())

###############################################################################
# 1️⃣8️⃣ Convert lowercase to uppercase using ord/chr (no upper())

###############################################################################
# 1️⃣9️⃣ Caesar cipher (shift letters by n positions)

###############################################################################
# 2️⃣0️⃣ Compress string
# Example:

# "aaabbc" → "a3b2c1"


## Reverse of strings

# input_string=input("enter your name : ").strip().lower()
# # reverse_string=input_string[::-1]
# # print(reverse_string)
# output_string=""
# le=len(input_string)
# for i in range(le-1,-1,-1): # Ramu
#     output_string+=input_string[i]
    
  
# print(output_string)


























# a = "hello"
# b = 'hello'

# print(a is b)
# print(id(a))
# print(id(b))


# doc strings 
# def test(a,b):
#     """ this is function description
#     2nd line
#     """
#     c=a+b
#     """ end of the function"""
#     pass
# print(test.__doc__)



# Escape sequences

# s = "Hello\nWorld"
# print(len(s)) # 11

# print("Hello\\\nWorld")

# raw strings
# print(r"Hello\nWorld")
# print(r"C:\new_folder\"")


#  immutability
# s = "hello"
# # s[0] = "H"
# s = "H" + s[1:]
# print(s)


# print("hi" * 0)
# print(len("hi" * 0))


# s="python"
# # print(s[10:12])
# print(s[5:1:-1])
# print(s[1:5:-1])

################## hashing
# print(hash("pythonalakjsdlk jv;sourbkfv s;klfvjbnsdkfjvbn;sidfv .dsnc n;sdjv "))
# print(hash("pythons"))

# data = {(1, [2, 3]): 100}
# print(data)


# s="samsung"
# k="APPLE"

# print(s.upper())
# print("ß".lower())
# print("ß".upper())



#### strip 
# s = "\n\t  hello  \t\n"
# print(s.strip())
# s = "   one   two   "
# print(s.split(" "))

# print(("f".join("a")))
# print("-".join(["a", "", "b"]))
# s = "apple apple apple"
# print(s.replace("apple", "orange", 1))
# s = "aaaa"
# print(s.replace("aa", "b"))

# order_id = 42
# print(f"ORD-{order_id:0>5}")


# s = "hello"
# print(type(s.encode()))
# # print("😊".encode("ascii"))
# print("😊".encode())


# a = "hello"
# b = "hello"

# print(a is b)

# a = "hello world"
# b = "hello" + " world"

# print(a is b)

# part1 = "hello "
# part2 = "world"

# a = "hello world"
# b = part1 + part2

# print(a is b)