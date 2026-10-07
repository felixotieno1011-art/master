# ============================================
# Student Grades Manager
# Demonstrates lists and dictionaries
# ============================================

# ---- List of students ----
students = ["Felix", "Wanjiku", "Otieno", "Akinyi"]

# ---- Dictionary: name → grade ----
grades = {
    "Felix": 85,
    "Wanjiku": 92,
    "Otieno": 78,
    "Akinyi": 95
}

# ---- Print all students and grades ----
print("📚 STUDENT GRADES")
print("=" * 40)

for student in students:
    grade = grades[student]
    print(f"{student}: {grade}")

# ---- Calculate average ----
total = 0
for student in students:
    total = total + grades[student]

average = total / len(students)
print(f"\n📊 Class Average: {average:.1f}")

# ---- Find highest scorer ----
highest_name = ""
highest_score = 0
for student in students:
    if grades[student] > highest_score:
        highest_score = grades[student]
        highest_name = student

print(f"🏆 Top Student: {highest_name} ({highest_score})")

# ---- Add a new student ----
print("\n➕ Adding new student: Kamau (88)")
students.append("Kamau")
grades["Kamau"] = 88

print(f"📋 New class size: {len(students)} students")

# ---- Show updated list ----
print("\n📚 UPDATED GRADEBOOK")
for student in students:
    print(f"{student}: {grades[student]}")
