"""
Name(s): Ian Ruebelmann
Creation Date: October 30th, 2026
Project: Project 1 - Minesweeping Game
File Description: This is the backend/gameplay function section. It is responsible for building a grid and providing helper
functions to give proper responses to actions taken in gameplay, providing the corresponding gamestates.
"""

# christopher brush update: safely selects a random answer for each new game
import random

ANSWER_LIST = []
VALIDATION_LIST = []

"""
    Dictionary to keep track of characters during a game
        0: unguessed
        1: guessed but not in final word (grey)
        2: guessed and somewhere in final word (yellow)
        3: guessed with known posistion in the final word (green)

        (Ian Ruebelmann, 10/30/26)
"""
CHARACTERS = {
    "a": 0,
    "b": 0,
    "c": 0,
    "d": 0,
    "e": 0,
    "f": 0,
    "g": 0,
    "h": 0,
    "i": 0,
    "j": 0,
    "k": 0,
    "l": 0,
    "m": 0,
    "n": 0,
    "o": 0,
    "p": 0,
    "q": 0,
    "r": 0,
    "s": 0,
    "t": 0,
    "u": 0,
    "v": 0,
    "w": 0,
    "x": 0,
    "y": 0,
    "z": 0,
}


"""
    simple function to be called on startup, loads the word lists from file

    (Ian Ruebelmann, 10/30/26)
"""


def LoadLists():
    answer_template = open("templates/AnswerWordList.txt", "r")
    validation_template = open("templates/EnglishWordList.txt", "r")

    for line in answer_template:
        ANSWER_LIST.append(line.lower().strip())
    for line in validation_template:
        VALIDATION_LIST.append(line.lower().strip())

    answer_template.close()
    validation_template.close()


"""
    Helper function to get a random answer, to be called at the start of a game

    (Ian Ruebelmann, 10/30/26)
"""


def GetRandomAnswer():
    return random.choice(ANSWER_LIST)


"""
    Function to use binary search to check if a guess is valid

    Inputs:
        guess: A 5 letter lowercase word that we want to test if is in the VALIDATION_LIST
        past_guesses: a list of previous guesses
        is_hardmode: a boolean that indicates if the game is in hardmode
        correct_answer: a string representing the final word goal, is only needed if hardmode = True

    Outputs:
        True: word is in the VALIDATION_LIST and not already guessed
        False: word is not in the VALIDATION_LIST or already guessed

    (Ian Ruebelmann, 10/30/26)
"""


def ValidateGuess(guess, past_guesses, is_hardmode=False, correct_answer=""):
    if guess in past_guesses:
        return False

    if is_hardmode and correct_answer == "":
        raise ("ensure correct_answer is set to a value if is_hardmode = True")

    if is_hardmode and ValidateHardmode(guess, past_guesses, correct_answer) == False:
        return False

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


"""
    Helper function for the second part of ValidateGuess, used to check if the guess is valid in a hardmode context

    Inputs:
        guess: A 5 letter lowercase word we are checking if is valid
        past_guesses: a list of previous guesses that have been made
        correct_answer: the final answer

    Output:
        Boolean indicating if the guess is valid

    (Ian Ruebelmann, 11/3/26)
"""


def ValidateHardmode(guess, past_guesses, correct_answer):
    if len(guesses) == 0:
        return True
    clues = Guess(guesses[-1], correct_answer)  # replace check with forest's function

    # Check if all the greens are in the same spot as the previous guess
    for i in range(len(guess)):
        if clues[i] == 3:
            if guess[i] != guesses[-1][i]:
                return False
            guess[i] = (
                "_"  # This assumes we have been given a copy of guess, we dont want to change the original
            )

    # Check if all the yellows from the previous guess are used
    for i in range(len(guess)):
        if clues[i] == 2:
            for j in range(len(guess)):
                if guess[j] == guesses[-1][i]:
                    guess[j] = "_"
                    break  # This break is ment to break out of the j loop, make sure it does
                if j == 4:
                    return False

    # If we get here we are good
    return True

'''
    Provides a random letter the player has no information about

    Inputs:
        correct_answer: Final correct answer for the current game

    Outputs:
        False: the player has information on every letter
        Random Letter: if the player dosen't have information on every letter it will return a random letter from the final word that the player does not have information on

    note: This does not account for double letters when the user has guessed one but not the other, it will just see that as the user having info on both letters
             I do not want to fix this, I vote we call it a feature.

    (Ian Ruebelmann, 11/10/2026
'''

def GetEasyModeLetter(correct_answer):
    
    answer = list(correct_answer)

    # Remove every letter the player has info on
    for letter in CHARACTERS:
        if CHARACTERS[letter] > 1:
            while letter in answer:
                answer.remove(letter)

    if len(answer) == 0:
        return False

    out = random.choice(answer) # Get a random letter that the player has no info on
    CHARACTERS[out] = 2 # We gave the letter so set the global dictionary to recognize it as yellow
    return out


"""
Function to compare guessed answer to correct answer, on the assumption that it is not the correct answer
inputs: user guess (string), correct_answer (string).
Output: Changed dictionary (CHARACTERS), along with a List of 1,2,3, corresponding to what color to show at each space 

(Forest Denton, 11/3/26)

Edited function to word with duplicate greens and yellows

(Ian Ruebelmann, 11/3/26)
"""


def Guess(guess, correct_answer):

    return_colors = ["_", "_", "_", "_", "_"]  # our output array

    # Split out strings into lists to support item assignment
    guess = list(guess)
    correct_answer = list(correct_answer)

    # check for greens
    for index in range(len(guess)):
        if guess[index] == correct_answer[index]:
            return_colors[index] = 3  # Color for the letter being in the right position
            correct_answer[index] = (
                "_"  # Mark the letter off so that it can't be counted more than once
            )
            guess[index] = "-"
            CHARACTERS[guess[index]] = 3  # Updating the global dictionary

    # check for yellows
    for index in range(len(guess)):
        if guess[index] in correct_answer:
            return_colors[index] = 2  # Color for the letter being in the final word
            correct_answer[correct_answer.index(guess[index])] = "_"
            guess[index] = "-"
            if CHARACTERS[guess[index]] < 2:
                CHARACTERS[guess[index]] = (
                    2  # Updating the global dictionary only if the global dictionary doesn't already have it marked as green
                )

    # mark the rest as grey
    for index in range(len(guess)):
        if guess[index] != "-":  # if the letter isn't in the correct answer
            return_colors[index] = 1  # Color for the letter not being in the final word
            if CHARACTERS[guess[index]] < 1:
                CHARACTERS[guess[index]] = (
                    1  # Updating the global dictionary only if the global dictionary doesn't already have it marked as green or yellow
                )

    return return_colors
