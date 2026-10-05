# ============================================
# My first CONSCIOUS program
# Understanding every line
# ============================================

# ---- 1. DATA ----
name = input("What's your name? ")     # input() gets text from user
age = input("How old are you? ")        # also text
age = int(age)                          # convert text to number

# ---- 2. LOGIC ----
greeting = "Hello, " + name + "!"

if age >= 18:
    status = "adult"
else:
    status = "minor"

# ---- 3. OUTPUT ----
print(greeting)
print(f"You are {age} years old — an {status}.")

# Let's also do a small calculation
next_year_age = age + 1
print(f"Next year you'll be {next_year_age}.")
