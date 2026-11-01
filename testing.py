"""
Name(s): Daniel Van Dalsem
Creation Date: November 1st, 2026
File Description: Tests python components
"""

import game
from game import ANSWER_LIST, VALIDATION_LIST, LoadLists, ValidateGuess


def main() -> None:
	# load in the lists
	LoadLists()
	# quick check
	try:
		cool = ANSWER_LIST[len(ANSWER_LIST) - 1]
	except IndexError:
		print("Attempted to index into ANSWER_LIST at " + str(len(ANSWER_LIST) - 1) + " and failed")
	pass


if __name__ == "__main__":
	main()
