def main():
    low = 0
    high = 1001

    count = 1

    while count < 11:
        middle = (low + high) // 2
        input_message = "My guess #{0} is {1} \n".format(count, middle)
        input_message += "L, H or C? "

        user_input = input(input_message)

        if user_input == 'L':
            low = middle
        elif user_input == 'H':
            high = middle
        elif user_input == 'C':
            break
        count += 1


if __name__ == "__main__":
    main()
