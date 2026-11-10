def can_vote(age):
    # 1. Check if it's actually a number (int or float)
    if not isinstance(age, (int, float)):
        raise TypeError("Age must be a number")
    
    # 2. Check if it's realistic
    if age < 0 or age > 120:
        raise ValueError("Age must be between 0 and 120")
    
    # 3. The actual logic
    return age >= 18
