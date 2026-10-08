#1. List of students
students = ["Felix", "Wanjiku", "Otieno"]

# 2. Dictionary for attendance
attendance = {
    "Felix": 0,
    "Wanjiku": 0,
    "Otieno": 0
}

# 3. Loop through students
for name in students:
    answer = input(f"Was {name} present? (y/n): ")

# 4. Print the report
print("📊 ATTENDANCE REPORT")# 1. List of students
students = ["Felix", "Wanjiku", "Otieno"]

# 2. Dictionary for attendance
attendance = {
    "Felix": 0,
    "Wanjiku": 0,
    "Otieno": 0
}

# 3. Loop through students
for name in students:
    answer = input(f"Was {name} present? (y/n): ")
    if answer == "y":
        attendance[name] = 1

# 4. Print the report
print()
print("📊 ATTENDANCE REPORT")

present_count = 0

for name in students:
    if attendance[name] == 1:
        print(f"{name}: ✅ present")
        present_count = present_count + 1
    else:
        print(f"{name}: ❌ absent")

print()
print(f"Total present: {present_count} out of {len(students)}")
