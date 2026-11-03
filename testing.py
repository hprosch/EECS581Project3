"""
Name(s): Daniel Van Dalsem
Creation Date: November 1st, 2026
File Description: Tests python components
"""

import random

import game
from game import ANSWER_LIST, VALIDATION_LIST, LoadLists, ValidateGuess, StartGame


def main() -> None:
	StartGame()
	# load in the lists
	LoadLists()
	answerlist = True
	# quick check
	try:
		cool = ANSWER_LIST[len(ANSWER_LIST) - 1]
	except IndexError:
		print("Attempted to index into ANSWER_LIST at " + str(len(ANSWER_LIST) - 1) + " and failed")
		answerlist = False

	# next test validate guess
	validateguesspass = True
	for i in range(0, 5):
		past_guesses = [
			VALIDATION_LIST[random.randint(0, len(VALIDATION_LIST) - 1)] for _ in range(0, i)
		]
		# use a set so I can use union and stuff
		validset = set(VALIDATION_LIST)
		# add weird stuff to valid set to make sure that is handled right
		validset = validset.union({"aaaa", "bbbb", "cccc", "dddd", "gggggg", ";;;g"})
		for guess in validset:
			valid = guess not in past_guesses and guess in VALIDATION_LIST
			result = ValidateGuess(guess, past_guesses)
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

	if validateguesspass and answerlist:
		print("All tests passed!")


if __name__ == "__main__":
	main()
