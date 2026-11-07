"""
Name(s): Daniel Van Dalsem
Creation Date: November 1st, 2026
File Description: Tests python components from game.py
"""

from typing import Any


import random

from game import ANSWER_LIST, VALIDATION_LIST, LoadLists, ValidateGuess, StartGame, Guess

"""
(Daniel Van Dalsem 11/4/2026)
Run guess with some hand computed inputs and outputs and checks if they are correct.
returns true if it passes false if it fails

"""


def GuessTest() -> bool:
	guesstest = True
	# make the test pairs
	testpairs: list[tuple[list[int], list[int]]] = [
		(Guess("abcde", "abcde"), [3, 3, 3, 3, 3]),
		(Guess("aaaaa", "abcde"), [3, 1, 1, 1, 1]),
		(Guess("abaaa", "aabbb"), [3, 2, 2, 1, 1]),
		(Guess("zzzzz", "aabbb"), [1, 1, 1, 1, 1]),
	]
	# for each pair
	for i, j in testpairs:
		# if the result is not the same as the expected result the test fails
		if i != j:
			guesstest = False
	if not guesstest:
		print("testing of guess function failed")
	else:
		print("testing of guess function passed")
	return guesstest


"""
(Daniel Van Dalsem 11/4/2026)
Checks to make sure that everything in answer list is also in validation list
True if passes, False if it fails
"""


def answerlist_is_subset_test() -> bool:
	answerlist_is_subset = True
	# for every anwser
	for i in ANSWER_LIST:
		# if its not the the validation list the test fails
		if i not in VALIDATION_LIST:
			answerlist_is_subset = False
	if not answerlist_is_subset:
		print(
			"The answer list is not a subset of the Validation list! Some Possible Answers are not valid words!"
		)
	if answerlist_is_subset:
		print("Answer list is subset of validation passed")

	return answerlist_is_subset


"""
(Daniel Van Dalsem 11/4/2026)
Takes a bund of random words from the validation list as well as some extra invalid inputs, and checks to make sure the ValidateGuess validates correctly
"""


def ValidateGuessTest() -> bool:
	validateguesspass = True
	for i in range(0, 5):
		past_guesses = [
			VALIDATION_LIST[random.randint(0, len(VALIDATION_LIST) - 1)] for _ in range(0, i)
		]
		# use a set so I can use union and stuff
		validset = set(VALIDATION_LIST)
		# add weird stuff to valid set to make sure that is handled right
		validset = validset.union({"aaaa", "bbbb", "cccc", "dddd", "gggggg", ";;;g"})
		# loop through the valid set
		for guess in validset:
			# if its not a pass guess and its in the valid set list its true
			valid = guess not in past_guesses and guess in VALIDATION_LIST
			# get the validate guess reponse
			result = ValidateGuess(guess, past_guesses)
			# if they do not make test fails
			if valid != result:
				validateguesspass = False
				print("Test failed!")
				print(
					"Validate guess returned "
					+ str(result)
					+ " with "
					+ str(past_guesses)
					+ " and "
					+ guess
					+ " as inputs"
				)
				print("Expected " + str(valid))
	if validateguesspass:
		print("ValidateGuess testing passed")

	return validateguesspass


"""
(Daniel Van Dalsem 11/4/2026)
Runs the tests and prints if they pass
"""


def main() -> None:
	# load in the lists
	LoadLists()
	answerlist = True
	# quick check
	try:
		cool = ANSWER_LIST[len(ANSWER_LIST) - 1]
	except IndexError:
		print("Attempted to index into ANSWER_LIST at " + str(len(ANSWER_LIST) - 1) + " and failed")
		answerlist = False

	# awnser list should be a subset of validation lists
	answerlist_is_subset = answerlist_is_subset_test()
	# next test validate guess
	validateguesspass = ValidateGuessTest()

	# test the guess function
	guesstest = GuessTest()
	if validateguesspass and answerlist and answerlist_is_subset and guesstest:
		print("All tests passed!")


if __name__ == "__main__":
	main()
