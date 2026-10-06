## 3.1 How Programming Works

### What programming is
Giving a computer precise instructions to solve a problem.
Three parts: Input → Process → Output

### The 2 big ideas (every program has these)
1. DATA  = the stuff (numbers, text, lists, objects) → stored in variables
2. LOGIC = what you do with data (if, loops, functions)

### Interpreted vs Compiled
- Interpreted (Python, JS): runs line by line, slower, easier to develop
- Compiled (C, Go, Rust): translated to binary before running, faster

### My first conscious program
Wrote hello_program.py:
- Asked for name and age (input)
- Converted age to number (int)
- Checked if adult (if age >= 18)
- Printed greeting (f-string)
- Did math (age + 1)

### Understood every line:
- input()   = waits for user to type, returns text
- int()     = converts text to number
- if        = checks a condition (true/false path)
- f"..."    = f-string, puts variables inside {}
- print()   = outputs to screen

### Key insight
Every program = input → process → output.
Just different scales.
## 3.2 Variables, Types, Operators

### Variables
- Named container for data: name = "Felix"
- Rules: start with letter/_, case-sensitive, no reserved words
- Convention: snake_case (my_name, not myName)

### 5 Basic Types
- int    : 5, 100, -3
- float  : 3.14, 0.5
- str    : "hello"
- bool   : True, False
- NoneType: None (nothing)

### Type conversion
- int("24")   → 24
- float("3.14") → 3.14
- str(24)     → "24"
- bool(0)     → False, bool(1) → True

### Arithmetic operators
+  add
-  subtract
*  multiply
/  divide (returns float: 10/3 = 3.33...)
// floor divide (returns int: 10//3 = 3)
%  modulus (remainder: 10%3 = 1)
** power (10**3 = 1000)

### Comparison
== equal, != not equal, > < >= <=

### Logical
and (both true), or (one true), not (opposite)

### Common trap
= assigns, == compares
age = 24 → sets age
age == 24 → asks "is age 24?"

### My calculator.py
- Takes 2 numbers
- Shows all operations
- Shows types
- Shows comparisons & logic
### 3.3 Conditionals & Loops — Phase B Drill
Wrote password_checker.py from memory.

v1: No loop, = instead of ==, 4 bugs
v2: Added loop but wrong structure
v3: 90% correct
v4: PERFECT ✅

### Key lessons learned:
- break must be INSIDE a loop
- = assigns, == compares
- input() must be INSIDE the loop to repeat
- Python is case-sensitive (True not true)
- Closing parens are critical
- Indentation matters

### Compare to 4 years ago:
Back then I would have quit.
Today I debugged 4 versions and succeeded.
