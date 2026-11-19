"""
Name(s): Ian Ruebelmann
Creation Date: November 19th, 2026
Project: Project 2 - Wordle Game
File Description: This file is responsible for taking the current gamestate and returning the "best guess" for that gamestate
"""
import math
import random
from collections import Counter

from game import ANSWER_LIST, VALIDATION_LIST, LoadLists, ScoreGuess

STARTING_WORDS = [
    "arise",
    "crate",
    "irate",
    "orate",
    "raile",
    "raise",
    "reast",
    "roate",
    "salet",
    "slate",
    "soare",
    "stare",
    "trace",
]    


'''
    Function to take the current gamestate and return the best next guess

    Inputs:
        guesses: a list of the previous guesses that were made in the form of 5 letter strings
        answer: the final word answer (this is only needed to get the results of previous guesses)

    outputs:
        A 5 letter string representing the best next guess

    (Ian Ruebelmann, 11/19/26)
'''
def NextBest(guesses, answer, answer_list = ANSWER_LIST, word_list = VALIDATION_LIST):
    # The first guess is computationally really slow so we precompute a couple good ones and just randomly pick one
    if len(guesses) == 0:
        return random.choice(STARTING_WORDS)
    
    best_word = ""
    best = 0

    # prune answer list based on guesses
    answer_list = Prune(guesses, answer_list, answer)

    # If we only have one potential anwser left we found the answer
    if len(answer_list) == 1:
        return answer_list[0]

    # If not we test every potential guess to find the one that would give the highest information and return it
    for word in word_list:
        h = Information(word, answer_list)
        if h > best:
            best_word = word
            best = h
    return best_word

'''
    This function is how we are determining the fitness of a guess (how good it is). It finds the probablity distribution of each of the potential outputs for a guess and
    uses that to determine the total information that would be provided given that guess was entered.

    Inputs:
        guess: A potential 5 letter guess in the form of a string
        word_list: the list of the remaining words that could be an answer given the current game state

    ouput: a float indicating the total information of that guess
        
    (Ian Ruebelmann, 11/19/26)
'''
# Note: this could probably be faster if I did this in reverse (counting the word list per state instead of incrementing a state per word) but this was orginally for
#          something else that this ended up being a huge time save for, I can set up the reverse solution later if the computation time on this is truly a problem
def Information(guess, word_list):
    X = len(word_list)  # The length of our alphabet
    states = {} # A dictionary to count up the potential answers that are still possible given each state

    # Fill out our dictionary
    for word in word_list:
        state = ""
        clues = ScoreGuess(guess, word)
        
        for num in clues:
            state = state + str(num)
            
        if state not in states:
            states[state] = 0
        states[state] += 1

    # we calcuate the total entropy for our word
    h = 0

    for state in states:
        p = states[state] / X # probability of each state occuring is the % of words remaining after we see the state, as each word is eually likely to be the answer and only shows up once between all states
        h -= p * math.log(p,2)
    return h

'''
    A helper function to reduce a list of potential answers given the clues from a guess

    Inputs:
        guesses: previous guesses
        word_list: the list you want pruned
        answer: the final answer so that we can get our clues from our previous guesses

    output: A pruned word list containing only the words that are still possible given the results from the given guesses

    (Ian Ruebelmann, 11/19/26)
'''
def Prune(guesses, word_list, answer):
    words = word_list.copy()
    for guess in guesses:
        for word in words.copy():
            if not Validate(word,guess,ScoreGuess(guess, answer)):
                words.remove(word)
    return words

'''
    A helper function for Prune(), takes a word, a guess and the guess's info and determines if it's still possible for that word to be an answer to the puzzle

    Inputs:
        word: a potential answer
        guess: a potential guess
        info: the guess clues/information from ScoreGuess()

    outputs:
        True: the word is still a possible answer
        False: the word is not a possible answer

    (Ian Ruebelmann, 11/19/26)
'''
def Validate(word, guess, info):
    word = list(word)
    
    # Check Greens
    for i in range(5):
        if info[i] == 3:
            if guess[i] == word[i]:
                word[i] = "_"
            else:
                return False

    # Check yellows
    for i in range(5):
        if info[i] == 2:
            if guess[i] in word and guess[i] != word[i]:
                word[word.index(guess[i])] = "_"
            else:
                return False

    # Check greys
    for i in range(5):
        if info[i] == 1:
            if guess[i] in word:
                return False

    return True
