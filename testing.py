"""
Name(s): Daniel Van Dalsem
Creation Date: November 1st, 2026
File Description: Tests python components from game.py
"""

import random
import unittest
from typing import Any
from unittest.mock import patch

from app import games
from game import (
	ANSWER_LIST,
	CHARACTERS,
	VALIDATION_LIST,
	GetEasyModeLetter,
	Guess,
	LoadLists,
	ValidateGuess,
)


def reset_characters() -> None:
	for key in CHARACTERS.keys():
		CHARACTERS[key] = 0


"""
(Daniel Van Dalsem 11/4/2026)
"""
BACKUP_ANSWER_LIST = ANSWER_LIST
BACKUP_VALIDATION_LIST = VALIDATION_LIST


class ModeTests(unittest.TestCase):
	# function taken from test_modes.py
	def setUp(self):
		ANSWER_LIST.clear()
		VALIDATION_LIST.clear()
		LoadLists()

		self.addCleanup(games.clear)
		self.addCleanup(reset_characters)

	def test_GetEasyModeLetter(self) -> None:
		answer = "abcde"
		for i in range(0, 20):
			reset_characters()
			letter1 = GetEasyModeLetter(answer)
			self.assertIn(letter1, answer)
		for i in range(0, 20):
			reset_characters()
			CHARACTERS["a"] = 2
			CHARACTERS["b"] = 2
			letter2 = GetEasyModeLetter(answer)
			self.assertIn(letter2, "cde")
		for i in range(0, 20):
			reset_characters()
			CHARACTERS["a"] = 3
			CHARACTERS["c"] = 1
			CHARACTERS["d"] = 2
			letter3 = GetEasyModeLetter(answer)
			self.assertIn(letter3, "bce")

		reset_characters()
		self.assertEqual(GetEasyModeLetter(""), False)

	"""
	(Daniel Van Dalsem 11/4/2026)
	Run guess with some hand computed inputs and outputs and checks if they are correct.
	returns true if it passes false if it fails

	"""

	def test_Guess(self) -> None:
		guesstest = True
		# make the test pairs
		testpairs: list[tuple[list[int], list[int]]] = [
			(Guess("crate", "later"), [1, 2, 2, 2, 2]),
			(Guess("crate", "trace"), [2, 3, 3, 2, 3]),
			(Guess("abcde", "abcde"), [3, 3, 3, 3, 3]),
			(Guess("aaaaa", "abcde"), [3, 1, 1, 1, 1]),
			(Guess("abaaa", "aabbb"), [3, 2, 2, 1, 1]),
			(Guess("zzzzz", "aabbb"), [1, 1, 1, 1, 1]),
		]
		# for each pair
		for i, j in testpairs:
			# if the result is not the same as the expected result the test fails
			self.assertEqual(i, j)

	"""
	(Daniel Van Dalsem 11/4/2026)
	Checks to make sure that everything in answer list is also in validation list
	True if passes, False if it fails
	"""

	def test_answerlist_is_subset(self) -> None:
		# for every anwser
		for i in ANSWER_LIST:
			# if its not the the validation list the test fails
			self.assertIn(i, VALIDATION_LIST)

	"""
	(Daniel Van Dalsem 11/4/2026)
	Takes a bund of random words from the validation list as well as some extra invalid inputs, and checks to make sure the ValidateGuess validates correctly
	"""

	def test_ValidateGuess(self) -> None:
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
				self.assertEqual(valid, result)


"""
(Daniel Van Dalsem 11/4/2026)
Runs the tests and prints if they pass
"""


if __name__ == "__main__":
	unittest.main()
