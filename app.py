# Prolouge
"""
app.py runs the Flask side of Wordle. Ruben Pino-Martinez worked on the menu route, game route, and mode route. - RPM 11.15
The page routes take browser requests and return the menu or game page. - RPM 11.15
The game API takes a mode, game ID, or guess and returns JSON for the browser. - RPM 11.4
The game routes combine our Flask code with Eden's validation and Hard Mode logic, - RPM 11.16
scoring by Forest and Eden, and Eden's GetEasyModeLetter() from easy-mode commit 6ff86f3. - RPM 11.16

Generative ARtificial Intelligence Usage Documentation and Listing:
1. How/Why AI: I used ChatGPT to help connect Flask to the existing game.py functions - RPM 11.4
2. Prompts: "lay out and make easy to understand, not trying anything clever or out of the ordinary, on how I can implement flask foundatoin for game.py".
            "Verify both implementations succeeding in the sense that im setting myself up for success in the project". - RPM 11.16
3. Validation/Revision: I tested the Flask routes in PowerShell, questioned an unexpected "Invalid Request" response, and shared my app.py to troubleshoot it.
                        I also chose the newer Sprint 2 requirements, specifically "players request letters with a Free Letter button", instead of having letters revealed automatically. - RPM 11.16
4. Challenges/Limitations: The Flask routes were initially assigned to the wrong functions, which caused request errors. I also investigated why Easy Mode stopped at
                            3/5 or 4/5 reveals and learned that previously known letters and repeated letters could reduce the number of available reveals. - RPM 11.16
"""

from flask import Flask, abort, render_template, jsonify, request
from threading import Lock
from uuid import uuid4
from adventure import calcDifficulty, getDiffecullty
import game
import autoGuess

# set up the Flask app so it can handle browser requests - RPM 11.3
app = Flask(__name__)

# keep the answer and game history on the server between requests - RPM 11.3
# send the browser a game ID at the start, then send the answer when the game ends - RPM 11.3
games = {}

MAX_GUESSES = 6  # caps the game at six accepted guesses - RPM 11.4
MAX_FREE_LETTERS = 5  # caps Easy Mode at five successful reveals - RPM 11.16
GAME_MODES = {
    "classic": "Classic Mode",
    "adventure": "Adventure Mode",
    "easy": "Easy Mode",
    "hard": "Hard Mode",
}  # maps mode keys to labels - RPM 11.16


# show the start menu when the player first opens Wordle - RPM 11.15
@app.route("/")
def home():  # renders the Jinja menu template - RPM 11.15
    return render_template("start.html")


# open the game board in the mode the player picked - RPM 11.15
@app.route("/play")
def play():  # returns the game template or a 400 error - RPM 11.15
    mode = request.args.get(
        "mode",
        "classic",
    )  # reads the mode query parameter, defaults to Classic - RPM 11.16
    if mode not in GAME_MODES:
        abort(400, description="Unknown game mode")
    return render_template("index.html", mode=mode, mode_label=GAME_MODES[mode])


# check the word the player just submitted - RPM 11.4
@app.route("/api/guess", methods=["POST"])
def submit_guess():  # takes JSON game ID and guess, returns JSON feedback or a 400 - RPM 11.4
    # get the game ID and word the player sent - RPM 11.4
    data = request.get_json(
        silent=True
    )  # parses JSON and returns None when parsing fails - RPM 11.4

    # send back an error if the request didn't give us a JSON object - RPM 11.4
    if not isinstance(data, dict):
        return jsonify({"valid": False, "message": "Invalid Request"}), 400

    game_id = data.get("game_id")
    guess = data.get("guess")

    # check that this ID belongs to a game we started - RPM 11.4
    if not isinstance(game_id, str) or game_id not in games:
        return jsonify({"valid": False, "message": "Game not found"}), 400

    # make sure they gave us a five-letter word to check - RPM 11.4
    if not isinstance(guess, str) or len(guess) != 5 or not guess.isalpha():
        return jsonify({"valid": False, "message": "Enter a five-letter word"}), 400

    # put the guess in the same case as the words in the lists - RPM 11.4
    guess = guess.lower()  # normalizes the word before validation - RPM 11.4
    current_game = games[game_id]
    with current_game["lock"]:
        return check_guess(guess, current_game)


# use the submitted word and saved game to score a guess or explain why it was rejected - RPM 11.16
def check_guess(
    guess, current_game
):  # updates the game state and returns JSON - RPM 11.16
    # stop here if the player already finished the game - RPM 11.4
    if current_game.get("finished", False):
        return jsonify({"valid": False, "message": "Game already finished"}), 400

    # reuse Eden's word check for the dictionary and past guesses - RPM 11.4
    if not game.ValidateGuess(
        guess, current_game["guesses"]
    ):  # passes in the word and guess history - RPM 11.4
        return jsonify({"valid": False, "message": "Invalid or repeated word"}), 400

    # make the player use earlier clues when their game is in Hard Mode - RPM 11.16
    if (
        current_game.get("mode", "classic") == "hard"
    ):  # applies clue checks using the saved mode - RPM 11.16
        message = game.HardModeError(
            guess, current_game["guesses"], current_game["answer"]
        )
        if message:
            return jsonify(
                {"valid": False, "message": message}
            ), 400  # sends the clue violation back as a 400 - RPM 11.16

    # score the accepted word with the team's game code and save it as one try - RPM 11.4
    colors = game.Guess(
        guess, current_game["answer"]
    )  # gets a feedback value for each of the five letters - RPM 11.4
    current_game["guesses"].append(
        guess
    )  # adds the word to the accepted guesses - RPM 11.4

    # see if they got the word or ran out of guesses - RPM 11.4
    won = guess == current_game["answer"]
    game_over = (
        won or len(current_game["guesses"]) >= MAX_GUESSES
    )  # checks for a win or the guess limit - RPM 11.4

    if game_over:
        current_game["finished"] = True  # sets the flag later requests check - RPM 11.4

    # put together what the browser needs to show the result - RPM 11.4
    result = {"valid": True, "colors": colors, "won": won, "game_over": game_over}

    # give the player the answer once their game is over - RPM 11.4
    if game_over:
        result["answer"] = current_game["answer"]

    # remember the green and yellow letters so Free Letter won't give them out again - RPM 11.16
    if current_game["mode"] == "easy":
        current_game["known_letters"].update(
            letter
            for letter, color in zip(guess, colors)
            if color >= 2  # 2 = yellow, 3 = green - RPM 11.16
        )
        result["free_letters"] = free_letter_state(current_game)

    return jsonify(result)  # returns the feedback and game status as JSON - RPM 11.4


# start a fresh game in the requested mode and send the browser its game ID - RPM 11.16
@app.route("/api/start", methods=["POST"])
def start_game():  # takes an optional JSON mode, returns the new game info or a 400 - RPM 11.16
    # allow a start request without a JSON body so it can still open a Classic game - RPM 11.16
    data = (
        request.get_json(silent=True) if request.is_json and request.get_data() else {}
    )
    if not isinstance(data, dict):
        return jsonify({"valid": False, "message": "Invalid Request"}), 400

    # make sure the requested mode is one we support - RPM 11.16
    mode = data.get(
        "mode", "classic"
    )  # uses Classic when the mode key is missing - RPM 11.16
    if not isinstance(mode, str) or mode not in GAME_MODES:
        return jsonify({"valid": False, "message": "Unknown game mode"}), 400

    # load the word lists the first time a game needs them - RPM 11.3
    if not game.ANSWER_LIST:  # checks whether the answer list is empty - RPM 11.3
        game.LoadLists()
    # use the random answer picker we already have in game.py - RPM 11.3
    answer = game.GetRandomAnswer()
    # Daniel Van Dalsem 11/25/2026
    print(mode)
    if mode == "adventure":
        result = getDiffecullty()
        print(result)
        answer = getDiffecullty()[0][0]
        print(answer)
    # give this game its own ID and keep its details on the server - RPM 11.3
    game_id = uuid4().hex  # turns a new UUID into a hex string - RPM 11.3
    current_game = {
        "answer": answer,
        "guesses": [],
        "mode": mode,
        "lock": Lock(),
    }
    result = {"game_id": game_id, "mode": mode, "message": "Game started"}
    # start Easy Mode with no known letters and no free letters used yet - RPM 11.16
    if mode == "easy":
        current_game["known_letters"] = (
            set()
        )  # stores distinct letters learned from clues or reveals - RPM 11.16
        current_game[
            "revealed_letters"
        ] = []  # stores letters given out by the Free Letter button - RPM 11.16
        result["free_letters"] = free_letter_state(current_game)
    games[game_id] = current_game  # stores the new session under its game ID - RPM 11.3
    return jsonify(result)


# use the saved Easy Mode game to tell the browser what was revealed and if more is available - RPM 11.16
def free_letter_state(current_game):  # returns the reveal info as a dict - RPM 11.16
    letters = current_game["revealed_letters"]
    used = len(letters)  # counts successful reveals from the saved list - RPM 11.16
    return {
        "letters": letters.copy(),  # copies the list for the response - RPM 11.16
        "used": used,
        "limit": MAX_FREE_LETTERS,
        # stop offering letters after the game ends, the cap is reached, or every answer letter is known - RPM 11.16
        "available": (
            not current_game.get("finished", False)
            and used < MAX_FREE_LETTERS
            and not current_game["known_letters"].issuperset(current_game["answer"])
        ),
    }


# use the game ID to try a Free Letter and send back the letter or the reason it's unavailable - RPM 11.16
@app.route("/api/free-letter", methods=["POST"])
def reveal_letter():  # takes a JSON game ID and returns a JSON result - RPM 11.16
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"valid": False, "message": "Invalid Request"}), 400

    # find the game and make sure it's in Easy Mode before giving out a letter - RPM 11.16
    game_id = data.get("game_id")
    if not isinstance(game_id, str) or game_id not in games:
        return jsonify({"valid": False, "message": "Game not found"}), 400

    current_game = games[game_id]
    if current_game["mode"] != "easy":
        return jsonify(
            {"valid": False, "message": "Free Letter is only available in Easy Mode"}
        ), 400

    with current_game["lock"]:
        # check if a reveal is still available and tell the player why if it isn't - RPM 11.16
        state = free_letter_state(current_game)
        if not state["available"]:
            if current_game.get("finished", False):
                message = "Game already finished"
            elif state["used"] == state["limit"]:
                message = "Free Letter limit reached"
            else:
                message = "No new letters left to reveal"
            return jsonify(
                {"valid": False, "message": message, "free_letters": state}
            ), 400

        # pick a letter they haven't learned yet using Eden's helper - RPM 11.16
        letter = game.GetEasyModeLetter(
            current_game["answer"], current_game["known_letters"]
        )
        # save the reveal so it counts toward the limit and can't come up again - RPM 11.16
        current_game["revealed_letters"].append(
            letter
        )  # adds one successful reveal to the count - RPM 11.16
        current_game["known_letters"].add(
            letter
        )  # adds the letter to the set excluded from future reveals - RPM 11.16
        return jsonify(
            {
                "valid": True,
                "letter": letter,
                "free_letters": free_letter_state(current_game),
            }
        )


# Daniel Van Dalsem (11/20/2026)
# route for the hints, gets the hint and returns it
@app.route("/api/get-hint", methods=["POST"])
def get_hint():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"valid": False, "message": "Invalid Request"}), 400

    game_id = data.get("game_id")
    if not isinstance(game_id, str) or game_id not in games:
        return jsonify({"valid": False, "message": "Game not found"}), 400

    current_game = games[game_id]

    with current_game["lock"]:
        state: bool = current_game.get("finished", False)
        if state:
            return jsonify(
                {"valid": False, "message": "Game already finished", "hint": False}
            ), 400

        hint = game.Hint(current_game["answer"])

        return jsonify({"valid": True, "hint": hint})


if __name__ == "__main__":
    # starts flask with development debugging enabled
    app.run(debug=True)
