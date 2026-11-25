import game
import autoGuess
import json
from pathlib import Path


# Daniel Van Dalsem 11/25/2026
def calcDifficulty(anwsers: list[tuple[str, int]]):
    for i in game.ANSWER_LIST:
        gameawnser = ""
        x = 0
        guesses = []
        while gameawnser != i:
            gameawnser = autoGuess.NextBest(
                guesses, i, game.ANSWER_LIST, game.VALIDATION_LIST
            )
            guesses.append(gameawnser)
            x += 1
        anwsers.append((i, x))
        print((i, x))
    anwsers.sort(key=lambda tup: tup[1])
    return anwsers


CACHE_FILE = Path("./adventure_results.json")

# Daniel Van Dalsem 11/25/2026
# I looked up the json dumping and loading


def getDiffecullty() -> list[tuple[str, int]]:
    if CACHE_FILE.exists():
        results = json.loads(CACHE_FILE.read_text())
        results.sort(key=lambda tup: tup[1])
        return results
    else:
        results: list[tuple[str, int]] = []
        try:
            calcDifficulty(results)
        except KeyboardInterrupt:
            CACHE_FILE.write_text(json.dumps(results))
        results.sort(key=lambda tup: tup[1])
        return results


# this is just to make running it nicer
if __name__ == "__main__":
    game.LoadLists()

    getDiffecullty()
