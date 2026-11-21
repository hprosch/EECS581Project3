"""
Name(s): Ian Ruebelmann
Creation Date: October 30th, 2026
Project: Project 2 - Wordle Game
File Description: This is the backend/gameplay function section. It is responsible for keeping a dictionary of used and unused characters,
                         aswell as validating and checking guesses to ensure they are valid guesses and sending them back the appropriate clues.
"""

# christopher brush update: safely selects a random answer for each new game
import random
from collections import Counter
import json
import re
from filecmp import DEFAULT_IGNORES

ANSWER_LIST = []
VALIDATION_LIST = []
WORD_DICTIONARY = {}

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


def GetEasyModeLetter(correct_answer: str, known_letters: set[str]) -> str | None:
    """Pick an answer letter the player has yet to learn."""
    # eden's easy-mode helper, using this game's clues instead of global state
    candidates = [letter for letter in correct_answer if letter not in known_letters]
    return random.choice(candidates) if candidates else None


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
        raise ValueError("Hard Mode validation requires the correct answer")

    if is_hardmode and not ValidateHardmode(guess, past_guesses, correct_answer):
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
    return HardModeError(guess, past_guesses, correct_answer) is None


def HardModeError(guess, past_guesses, correct_answer):
    """Explain the first clue violation using feedback from accepted guesses."""
    guess_counts = Counter(guess)
    for previous in past_guesses:
        clues = ScoreGuess(previous, correct_answer)
        for index, (letter, color) in enumerate(zip(previous, clues)):
            if color == 3 and guess[index] != letter:
                return f"Hard Mode: keep {letter.upper()} in position {index + 1}."

        # a green and a yellow for the same letter require two copies
        known_counts = Counter(letter for letter, color in zip(previous, clues) if color >= 2)
        for letter, count in known_counts.items():
            if guess_counts[letter] < count:
                label = letter.upper()
                if count == 1:
                    return f"Hard Mode: use {label} in your guess."
                return f"Hard Mode: use at least {count} copies of {label}."

    return None


"""
Function to compare guessed answer to correct answer, on the assumption that it is not the correct answer
inputs: user guess (string), correct_answer (string).
Output: Changed dictionary (CHARACTERS), along with a List of 1,2,3, corresponding to what color to show at each space 

(Forest Denton, 11/3/26)

Edited function to word with duplicate greens and yellows

(Ian Ruebelmann, 11/3/26)
"""


def Guess(guess, correct_answer):
    colors = ScoreGuess(guess, correct_answer)
    for letter, color in zip(guess, colors):
        CHARACTERS[letter] = max(CHARACTERS[letter], color)
    return colors


def ScoreGuess(guess, correct_answer):
    """Compute the same feedback used by the board without changing letter state."""
    colors = [1] * len(guess)
    remaining = Counter(correct_answer)

    for index, letter in enumerate(guess):
        if letter == correct_answer[index]:
            colors[index] = 3
            remaining[letter] -= 1

    for index, letter in enumerate(guess):
        if colors[index] == 1 and remaining[letter] > 0:
            colors[index] = 2
            remaining[letter] -= 1

    return colors


"""
BuildDictionary() takes in no arguments, and initiates a global variable containing all valid words and their definitions

The definition 
Hint() takes in the correct word and returns the definition of the word as a string 
(Forest Denton, 11/16/26) 
"""
def BuildDictionary():
    "Called at the beginning of game, converts a JSON file to python Dictionary"
    global WORD_DICTIONARY
    with open('dictionary.json') as file:
        WORD_DICTIONARY = json.load(file)


def Hint(correct_word):
    if not bool(WORD_DICTIONARY): # if the dictionary hasn't been built yet
        BuildDictionary()
    definition = ""
    try:
        definition = WORD_DICTIONARY[correct_word]
        return re.split(r'[\n"2"]',definition)[0]
    except KeyError:
        return "Sorry, no hint is available (No definition found)"
