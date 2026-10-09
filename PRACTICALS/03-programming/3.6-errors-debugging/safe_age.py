while True:
    try:
        age = int(input("Enter your age: "))
        # if we get here, input was valid -> break out of loop
        print(f"You are {age} years old.")
        print(f"In 10 years, you'll be {age + 10}.")
        break
    except ValueError:
        print("❌ That's not a number. Try again.")
        # loops back to ask again
