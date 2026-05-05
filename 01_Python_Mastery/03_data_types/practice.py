"""
╔══════════════════════════════════════════════════════════════════╗
║              DATA TYPES — REAL WORLD EXAMPLES                   ║
║      See how each type looks in actual, everyday Python code    ║
║                                                                  ║
║  📌 NOTE: We haven't learned functions yet, so all code here    ║
║     runs top-to-bottom with just variables and print()          ║
╚══════════════════════════════════════════════════════════════════╝
"""

print("=" * 60)
print("        DATA TYPES — REAL WORLD EXAMPLES")
print("=" * 60)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# INT IN REAL LIFE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n── int: Real Life Uses ──")

# → Counting students in a class
total_students = 42
boys  = 18
girls = 24
print(f"Class: {total_students} students ({boys} boys, {girls} girls)")

# → Working out how many pages in a book chapter
words_in_chapter = 4500
words_per_page   = 250
full_pages       = words_in_chapter // words_per_page
leftover_words   = words_in_chapter % words_per_page
print(f"\nChapter: {full_pages} full pages + {leftover_words} words on last page")

# → Checking if a year is a leap year (divisible by 4)
year = 2024
if year % 4 == 0:
    print(f"\n{year} is a leap year ✓")
else:
    print(f"\n{year} is NOT a leap year")

# → Checking if a number is even or odd
number = 37
if number % 2 == 0:
    print(f"{number} is even")
else:
    print(f"{number} is odd")

# → Simple Interest calculation
principal = 10000
rate      = 7          # 7% per year
years     = 3
interest  = principal * rate * years // 100
total     = principal + interest
print(f"\nSimple Interest: ₹{interest}")
print(f"Total after {years} years: ₹{total}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FLOAT IN REAL LIFE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n── float: Real Life Uses ──")

# → Calculating a restaurant bill
item1_price = 120.50
item2_price = 85.00
item3_price = 45.75
subtotal    = item1_price + item2_price + item3_price
gst_rate    = 0.05                    # 5% GST
gst_amount  = subtotal * gst_rate
total_bill  = subtotal + gst_amount

print(f"\nRestaurant Bill:")
print(f"  Subtotal: ₹{subtotal:.2f}")
print(f"  GST 5%:   ₹{gst_amount:.2f}")
print(f"  Total:    ₹{total_bill:.2f}")

# → Body Mass Index (BMI)
weight_kg  = 70.5
height_m   = 1.75
bmi        = weight_kg / (height_m ** 2)
print(f"\nBMI: {bmi:.1f}")
if bmi < 18.5:
    print("Category: Underweight")
elif bmi < 25:
    print("Category: Normal weight")
elif bmi < 30:
    print("Category: Overweight")
else:
    print("Category: Obese")

# → Temperature conversion (Celsius to Fahrenheit)
celsius    = 37.0          # body temperature
fahrenheit = (celsius * 9 / 5) + 32
print(f"\n{celsius}°C = {fahrenheit:.1f}°F")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BOOL IN REAL LIFE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n── bool: Real Life Uses ──")

# → User login check
is_logged_in   = True
is_admin       = False
has_paid       = True

print(f"\nUser status:")
print(f"  Logged in:  {is_logged_in}")
print(f"  Admin:      {is_admin}")
print(f"  Paid:       {has_paid}")

if is_logged_in and has_paid:
    print("  → Access granted to content")
elif is_logged_in and not has_paid:
    print("  → Please upgrade your account")
else:
    print("  → Please log in")

# → Counting TRUE values (because True == 1)
quiz_answers = [True, False, True, True, False, True, True]
correct_answers = sum(quiz_answers)   # True counts as 1
total_questions = len(quiz_answers)
percentage      = (correct_answers / total_questions) * 100
print(f"\nQuiz: {correct_answers}/{total_questions} correct ({percentage:.0f}%)")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STRING IN REAL LIFE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n── str: Real Life Uses ──")

# → Building a user profile display
first_name = "alice"
last_name  = "sharma"
email      = "  alice.sharma@gmail.com  "
city       = "Mumbai"

full_name  = (first_name + " " + last_name).title()   # "Alice Sharma"
clean_email = email.strip().lower()                    # remove spaces, lowercase
domain     = clean_email.split("@")[1]                 # "gmail.com"

print(f"\nUser Profile:")
print(f"  Name:   {full_name}")
print(f"  Email:  {clean_email}")
print(f"  Domain: {domain}")
print(f"  City:   {city}")

# → Checking user input
phone_number = "9876543210"
print(f"\nPhone validation:")
print(f"  Is all digits? {phone_number.isdigit()}")
print(f"  Length OK?     {len(phone_number) == 10}")
if phone_number.isdigit() and len(phone_number) == 10:
    print(f"  → Valid Indian phone number!")
else:
    print(f"  → Invalid phone number")

# → Working with a CSV-like string
raw_data   = "Alice,25,Mumbai,Engineer"
parts      = raw_data.split(",")
name, age, city, job = parts
print(f"\nParsed data:")
print(f"  {name} is a {age}-year-old {job} from {city}")

# → Generating a simple report
scores_str = "85 92 78 96 70 88"
scores     = scores_str.split()
print(f"\nScores: {scores}")
print(f"Count:  {len(scores)}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LIST IN REAL LIFE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n── list: Real Life Uses ──")

# → Shopping cart
cart = []
cart.append("Apples")
cart.append("Milk")
cart.append("Bread")
cart.append("Eggs")
print(f"\nShopping cart: {cart}")
print(f"Items to buy:  {len(cart)}")

cart.remove("Milk")   # changed mind
print(f"After removing Milk: {cart}")

# → Class attendance
students = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
present  = ["Alice", "Charlie", "Eve"]
absent   = []

for student in students:
    if student not in present:
        absent.append(student)

print(f"\nAttendance:")
print(f"  Present ({len(present)}): {present}")
print(f"  Absent  ({len(absent)}):  {absent}")

# → Top 3 scores from a list
all_scores = [78, 92, 85, 96, 70, 88, 91, 76, 99, 83]
all_scores.sort(reverse=True)        # sort from highest to lowest
top_3 = all_scores[:3]               # take first 3
print(f"\nAll scores (sorted): {all_scores}")
print(f"Top 3 scores:        {top_3}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TUPLE IN REAL LIFE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n── tuple: Real Life Uses ──")

# → GPS coordinates (should never change after being set)
mumbai_coords   = (19.0760, 72.8777)   # (latitude, longitude)
delhi_coords    = (28.6139, 77.2090)

lat, lon = mumbai_coords   # unpack into variables
print(f"\nMumbai: Lat={lat}, Lon={lon}")

# → RGB colors (fixed values, never meant to change)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE  = (0, 0, 255)

r, g, b = RED
print(f"Red color: r={r}, g={g}, b={b}")

# → Monthly data (fixed labels)
months  = ("Jan","Feb","Mar","Apr","May","Jun",
           "Jul","Aug","Sep","Oct","Nov","Dec")
revenue = [120, 145, 130, 160, 180, 175, 190, 210, 200, 195, 220, 250]

for i, month in enumerate(months):
    print(f"  {month}: ₹{revenue[i]}k")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SET IN REAL LIFE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n── set: Real Life Uses ──")

# → Remove duplicate entries from a list
email_list = [
    "alice@gmail.com",
    "bob@yahoo.com",
    "alice@gmail.com",    # duplicate!
    "charlie@gmail.com",
    "bob@yahoo.com",      # duplicate!
]
unique_emails = list(set(email_list))
print(f"\nOriginal list: {len(email_list)} emails")
print(f"After dedup:   {len(unique_emails)} unique emails")

# → Finding students who enrolled in both courses
python_batch = {"Alice", "Bob", "Charlie", "Diana"}
sql_batch    = {"Bob", "Eve", "Charlie", "Frank"}

enrolled_both   = python_batch & sql_batch
enrolled_either = python_batch | sql_batch
only_python     = python_batch - sql_batch

print(f"\nEnrolled in both: {enrolled_both}")
print(f"Total unique:     {enrolled_either}")
print(f"Only Python:      {only_python}")

# → Fast lookup for valid inputs
valid_cities = {"Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad", "Kolkata"}
user_city = "Pune"

if user_city in valid_cities:
    print(f"\n{user_city} is a supported city")
else:
    print(f"\n{user_city} is not in our coverage area yet")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DICT IN REAL LIFE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n── dict: Real Life Uses ──")

# → Student report card
student = {
    "name":    "Alice Sharma",
    "grade":   10,
    "scores": {
        "Math":    92,
        "Science": 88,
        "English": 95,
        "Hindi":   79,
        "History": 85
    }
}

print(f"\n📋 Report Card: {student['name']}")
print(f"Grade: {student['grade']}")
print("-" * 30)
total = 0
for subject, marks in student["scores"].items():
    print(f"  {subject:<12}: {marks}")
    total += marks

average = total / len(student["scores"])
print("-" * 30)
print(f"  Average      : {average:.1f}")
if average >= 90:
    print("  Grade        : A+")
elif average >= 80:
    print("  Grade        : A")
elif average >= 70:
    print("  Grade        : B")
else:
    print("  Grade        : C")

# → Country dial codes
dial_codes = {
    "India":         "+91",
    "USA":           "+1",
    "UK":            "+44",
    "Australia":     "+61",
    "Germany":       "+49",
}

country = "India"
code = dial_codes.get(country, "Unknown")
print(f"\nDial code for {country}: {code}")

unknown = dial_codes.get("Mars", "Not on Earth")
print(f"Dial code for Mars: {unknown}")

# → Word frequency counter
sentence = "the cat sat on the mat the cat is fat"
words    = sentence.split()
freq     = {}
for word in words:
    freq[word] = freq.get(word, 0) + 1    # safe increment using .get()

print(f"\nWord frequency:")
for word, count in sorted(freq.items(), key=lambda x: x[1], reverse=True):
    bar = "█" * count
    print(f"  {word:<6}: {bar} ({count})")


print("\n" + "=" * 60)
print("Study these examples, then open practice.py!")
print("=" * 60)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NAVIGATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
📁 You are in: 03_data_types/examples.py
──────────────────────────────────────────
📖 README.md      ← Full theory & concepts (start here!)
🌍 examples.py    ← THIS FILE
💻 practice.py    ← Exercises to solve
🎤 interview.md   ← Q&A with explanations
⚡ cheatsheet.md  ← Quick reference card

⬅️  02_control_flow/   ➡️  04_functions/
🏠  ../README.md
"""