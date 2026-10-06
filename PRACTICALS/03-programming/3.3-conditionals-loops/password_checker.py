print("======password checker=====")

while True:
    guess = int(input("Enter your password: "))
    if guess == 20:
        print("Access granted")
        break
    else:
        print("Wrong password. Try again!")
