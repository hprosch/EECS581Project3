import unittest
from unittest.mock import patch

import game
from app import app, games


class ModeTests(unittest.TestCase):
    def setUp(self):
        games.clear()
        self.addCleanup(games.clear)
        self.http = app.test_client()
        answer = patch("app.game.GetRandomAnswer", return_value="crane")
        answer.start()
        self.addCleanup(answer.stop)

    def start(self, mode):
        response = self.http.post("/api/start", json={"mode": mode})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["mode"], mode)
        self.assertNotIn("answer", response.json)
        return response.json["game_id"]

    def guess(self, game_id, word, **extra):
        return self.http.post("/api/guess", json={"game_id": game_id, "guess": word, **extra})

    def reveal(self, game_id):
        return self.http.post("/api/free-letter", json={"game_id": game_id})

    def test_easy_session_and_five_reveal_limit(self):
        self.assertIn(b'/play?mode=easy', self.http.get("/").data)
        for mode in ("classic", "hard", "easy"):
            page = self.http.get(f"/play?mode={mode}")
            self.assertEqual(page.status_code, 200)
            self.assertEqual(b'id="free-letter-button"' in page.data, mode == "easy")
        self.assertFalse(games)

        start = self.http.post("/api/start", json={"mode": "easy"}).json
        game_id = start["game_id"]
        self.assertEqual(start["mode"], "easy")
        self.assertNotIn("answer", start)
        self.assertNotIn("letter", start)
        self.assertEqual(start["free_letters"], {
            "letters": [], "used": 0, "limit": 5, "available": True,
        })

        letters = []
        for used in range(1, 6):
            response = self.reveal(game_id)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(set(response.json), {"valid", "letter", "free_letters"})
            letters.append(response.json["letter"])
            self.assertEqual(response.json["free_letters"], {
                "letters": letters, "used": used, "limit": 5, "available": used < 5,
            })
        self.assertCountEqual(letters, "crane")
        exhausted = self.reveal(game_id)
        self.assertEqual(exhausted.status_code, 400)
        self.assertEqual(exhausted.json["message"], "Free Letter limit reached")
        self.assertEqual(games[game_id]["guesses"], [])

        restarted_id = self.start("easy")
        self.assertNotEqual(game_id, restarted_id)
        self.assertEqual(self.reveal(restarted_id).json["free_letters"]["used"], 1)
        self.assertEqual(self.reveal(game_id).json["free_letters"]["used"], 5)

    def test_easy_exhausts_distinct_letters_and_skips_learned_clues(self):
        with patch("app.game.GetRandomAnswer", return_value="apple"):
            game_id = self.start("easy")
            other_id = self.start("easy")

        letters = [self.reveal(game_id).json["letter"] for _ in range(4)]
        self.assertCountEqual(letters, "aple")
        exhausted = self.reveal(game_id)
        self.assertEqual(exhausted.json["message"], "No new letters left to reveal")
        self.assertEqual(exhausted.json["free_letters"]["used"], 4)

        # P is green, and A and L are yellow. Only E is still unknown.
        guess = self.guess(other_id, "papal").json
        self.assertEqual(guess["colors"], [2, 2, 3, 1, 2])
        self.assertTrue(guess["free_letters"]["available"])
        reveal = self.reveal(other_id).json
        self.assertEqual(reveal["letter"], "e")
        self.assertEqual(reveal["free_letters"], {
            "letters": ["e"], "used": 1, "limit": 5, "available": False,
        })
        self.assertEqual(games[other_id]["guesses"], ["papal"])
        self.assertTrue(self.guess(other_id, "apple").json["won"])
        self.assertEqual(self.reveal(other_id).json["message"], "Game already finished")

    def test_free_letter_rejects_other_modes_and_unknown_games(self):
        for mode in ("classic", "hard"):
            response = self.reveal(self.start(mode))
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json["message"], "Free Letter is only available in Easy Mode")
        self.assertEqual(self.reveal("unknown").status_code, 400)

    def test_landing_and_validated_mode_selection(self):
        landing = self.http.get("/")
        self.assertIn(b'/play?mode=hard', landing.data)
        self.assertIn(b'data-mode="classic"', self.http.get("/play").data)
        self.assertIn(b'data-mode="hard"', self.http.get("/play?mode=hard").data)
        self.assertEqual(self.http.get("/play?mode=unknown").status_code, 400)
        for value in ("unknown", "", None, [], 7):
            with self.subTest(mode=value):
                response = self.http.post("/api/start", json={"mode": value})
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json["message"], "Unknown game mode")
        self.assertFalse(games)
        self.assertEqual(self.http.post("/api/start").json["mode"], "classic")
        self.assertEqual(self.http.post("/api/start", json={}).json["mode"], "classic")
        no_body = self.http.post("/api/start", content_type="application/json")
        self.assertEqual(no_body.json["mode"], "classic")
        malformed = self.http.post("/api/start", data="{", content_type="application/json")
        self.assertEqual(malformed.status_code, 400)

    def test_hard_rejection_uses_stored_mode_and_preserves_attempt(self):
        hard_id = self.start("hard")
        self.assertEqual(self.guess(hard_id, "crate").json["colors"], [3, 3, 3, 1, 3])
        rejected = self.guess(hard_id, "blimp", mode="classic")
        self.assertEqual(rejected.status_code, 400)
        self.assertEqual(rejected.json["message"], "Hard Mode: keep C in position 1.")
        self.assertEqual(games[hard_id]["guesses"], ["crate"])
        self.assertTrue(self.guess(hard_id, "crane").json["won"])

        classic_id = self.start("classic")
        self.assertTrue(self.guess(classic_id, "crate").json["valid"])
        self.assertTrue(self.guess(classic_id, "blimp", mode="hard").json["valid"])
        restarted_id = self.start("hard")
        self.assertNotEqual(hard_id, restarted_id)
        self.assertTrue(self.guess(restarted_id, "blimp").json["valid"])

    def test_hard_yellows_and_duplicate_letters(self):
        with patch("app.game.GetRandomAnswer", return_value="later"):
            game_id = self.start("hard")
        self.assertEqual(self.guess(game_id, "crate").json["colors"], [1, 2, 2, 2, 2])
        rejected = self.guess(game_id, "blimp")
        self.assertEqual(rejected.status_code, 400)
        self.assertEqual(rejected.json["message"], "Hard Mode: use R in your guess.")
        self.assertEqual(games[game_id]["guesses"], ["crate"])
        self.assertTrue(self.guess(game_id, "stare").json["valid"])

        self.assertEqual(game.ScoreGuess("papal", "apple"), [2, 2, 3, 1, 2])
        self.assertEqual(
            game.HardModeError("ample", ["papal"], "apple"),
            "Hard Mode: use at least 2 copies of P.",
        )
        self.assertTrue(game.ValidateGuess("apply", ["papal"], True, "apple"))


if __name__ == "__main__":
    unittest.main()