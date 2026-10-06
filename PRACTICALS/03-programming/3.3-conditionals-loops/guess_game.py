# ============================================
# Number Guessing Game
# Demonstrates: variables, conditionals, loops, break
# ============================================

import random

# Pick a random number between 1 and 100
secret = random.randint(1, 100)

print("🎯 GUESS THE NUMBER")
print("I'm thinking of a number between 1 and 100.")
print("You have unlimited tries. Let's go!\n")

attempts = 0

# Loop forever (until we break)
while True:
    guess_text = input("Your guess: ")
    guess = int(guess_text)
    attempts = attempts + 1

    if guess < secret:
        print(f"⬆️  Too low! Try higher.\n")
    elif guess > secret:
        print(f"⬇️  Too high! Try lower.\n")
    else:
        print(f"\n🎉 CORRECT! The number was {secret}.")
        print(f"You got it in {attempts} attempts.")
        break    # stop the loop

print("\nThanks for playing!")
