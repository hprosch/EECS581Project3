import game
import autoGuess
import json
from pathlib import Path

TIMES = 10

# Daniel Van Dalsem 11/25/2026


def getWordDifficullty(i: str) -> float:
    gameawnser = ""
    x = 0
    guesses = []
    while gameawnser != i:
        gameawnser = autoGuess.NextBest(
            guesses, i, game.ANSWER_LIST, game.VALIDATION_LIST
        )
        guesses.append(gameawnser)
        x += 1
    return x


# Daniel Van Dalsem 11/25/2026
def calcDifficulty(anwsers: list[tuple[str, float]], onlyexisting: bool):
    existing = [x[0] for x in anwsers]
    for i in game.ANSWER_LIST:
        if i not in existing and not onlyexisting:
            print("calcing " + str(i))
            x = 0
            for _ in range(0, TIMES):
                x += getWordDifficullty(i)
            print((i, x / TIMES))
            anwsers.append((i, x / TIMES))
        else:
            print("skipping " + str(i))
    anwsers.sort(key=lambda tup: tup[1])
    return anwsers


CACHE_FILE = Path("./adventure_results.json")

# Daniel Van Dalsem 11/25/2026
# I looked up the json dumping and loading


def getDiffecullty(
    start: list[tuple[str, float]], onlyexisting=False
) -> list[tuple[str, float]]:

    results: list[tuple[str, float]] = start
    try:
        calcDifficulty(results, onlyexisting)
        CACHE_FILE.write_text(json.dumps(results))
    except KeyboardInterrupt:
        CACHE_FILE.write_text(json.dumps(results))
    results.sort(key=lambda tup: tup[1])
    return results


# this is just to make running it nicer
if __name__ == "__main__":
    game.LoadLists()
    if CACHE_FILE.exists():
        getDiffecullty(json.loads(CACHE_FILE.read_text()))
    else:
        getDiffecullty([])
