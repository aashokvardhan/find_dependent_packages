def main():
    low = 0
    high = 1001

    count = 1
    choices = ['l', 'h', 'c']

    while count < 11:
        middle = (low + high) // 2
        input_message = "Is my guess {} correct:\n 1. L\n 2. H\n 3. C\n Your choice:".format(middle)

        user_input = ''
        retry = 1
        while user_input not in choices and retry < 5:
            user_input = input(input_message).lower()
            retry += 1

        if user_input == 'l':
            low = middle
        elif user_input == 'h':
            high = middle
        else:
            print("Successfully guessed it in {} guesses.".format(count))
        count += 1

    if count == 12:
        print("Failed to guess in 10 guesses.")


if __name__ == "__main__":
    main()