import random

ANSWER_LIST = []
VALIDATION_LIST = []

'''
    Dictionary to keep track of characters during a game
        0: unguessed
        1: guessed but not in final word (grey)
        2: guessed and somewhere in final word (yellow)
        3: guessed with known posistion in the final word (green)

        (Ian Ruebelmann, 10/30/26)
'''
CHARACTERS = {
    "a" : 0, "b" : 0, "c" : 0, "d" : 0, "e" : 0, "f" : 0, "g" : 0, "h" : 0,
    "i" : 0, "j" : 0, "k" : 0, "l" : 0, "m" : 0, "n" : 0, "o" : 0, "p" : 0, "q" : 0,
    "r" : 0, "s" : 0, "t" : 0, "u" : 0, "v" : 0, "w" : 0, "x" : 0, "y" : 0, "z" : 0
}
 

'''
    More of a template function for now on how a game should look, should be broken atm

    (Ian Ruebelmann, 10/30/26)
'''
def StartGame():
    if ANSWER_LIST.isEmpty():
        LoadLists()
        
    final_word = GetRandomAnswer()
    guess_count = 5

    for i in range(guess_count):
        valid_guess = false

        while valid_guess = false:
            # Guess needs to be accepted somehow
            guess =  ""
            valid_guess = VALIDATE_GUESS(guess)

        if guess == final_word:
            # Win Condition
            break

        #Update Character List

'''
    simple function to be called on startup, loads the word lists from file

    (Ian Ruebelmann, 10/30/26)
'''
def LoadLists():
    answer_template = open("templates/AnswerWordList.txt", "r")
    validation_template = open("templates/EnglishWordList.txt", "r")
    
    for line in answer_template:
        ANSWER_LIST.append(line.lower().strip())
    for line in validation_template:
        VALIDATION_LIST.append(line.lower().strip())

    answer_template.close()
    validation_template.close()

'''
    Helper function to get a random answer, to be called at the start of a game

    (Ian Ruebelmann, 10/30/26)
'''
def GetRandomAnswer():
    return ANSWER_LIST[random.randint(0, len(ANSWER_LIST))]


'''
    Function to use binary search to check if a guess is valid

    Inputs:
        A 5 letter lowercase word that we want to test if is in the VALIDATION_LIST

    Outputs:
        True: word is in the VALIDATION_LIST
        False: word is not in the VALIDATION_LIST

    (Ian Ruebelmann, 10/30/26)
'''
def ValidateGuess(guess):
    low = 0
    high = len(VALIDATION_LIST) - 1
    while low <= high:
        mid = low + (high - low) // 2
        if VALIDATION_LIST[mid] == guess:
            return True
        elif VALIDATION_LIST[mid] < guess:
            low = mid + 1
        else:
            high = mid - 1

    return False
