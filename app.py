from flask import Flask, abort, render_template, jsonify, request
from threading import Lock
from uuid import uuid4
import game

# create flask application, and stores it to 'app' variable
app = Flask(__name__)

# store each game's answer and previous guesses on server
# browswer only recievs a game id, not the answer
games = {}

MAX_GUESSES = 6
MAX_FREE_LETTERS = 5
GAME_MODES = {"classic": "Classic Mode", "easy": "Easy Mode", "hard": "Hard Mode"}

@app.route("/")
def home():
    return render_template("start.html")


@app.route("/play")
def play():
    mode = request.args.get("mode", "classic")
    if mode not in GAME_MODES:
        abort(400, description="Unknown game mode")
    return render_template("index.html", mode=mode, mode_label=GAME_MODES[mode])

#  create new game without changing existing front end
@app.route("/api/guess", methods=["POST"])
def submit_guess():
    # get game id and guessed word from the request
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"valid": False, "message": "Invalid Request"}), 400
    
    game_id =  data.get("game_id")
    guess = data.get("guess")

    # ensure game exists
    if not isinstance(game_id, str) or game_id not in games:
        return jsonify({"valid": False, "message": "Game not found"}), 400
    
    # make sure the guess contains five letters
    if not isinstance(guess, str) or len(guess) != 5 or not guess.isalpha():
        return jsonify({"valid": False, "message": "Enter a five-letter word"}), 400

    guess = guess.lower()
    current_game = games[game_id]
    with current_game["lock"]:
        return check_guess(guess, current_game)


def check_guess(guess, current_game):
    # prevent guesses after the game has ended
    if current_game.get("finished", False):
        return jsonify({"valid": False, "message": "Game already finished"}), 400

    # use Eden's function to validate the guess
    if not game.ValidateGuess(guess, current_game["guesses"]):
        return jsonify({"valid": False, "message": "Invalid or repeated word"}), 400

    if current_game.get("mode", "classic") == "hard":
        message = game.HardModeError(guess, current_game["guesses"], current_game["answer"])
        if message:
            return jsonify({"valid": False, "message": message}), 400

    colors = game.Guess(guess, current_game["answer"])
    current_game["guesses"].append(guess)

    # determine whether the player has won or lost
    won = guess == current_game["answer"]
    game_over = won or len(current_game["guesses"]) >= MAX_GUESSES

    if game_over:
        current_game["finished"] = True

    # return the results to the browser
    result = {
        "valid": True,
        "colors": colors,
        "won": won,
        "game_over": game_over
    }

    # only reveal the answer when the game is finished
    if game_over:
        result["answer"] = current_game["answer"]

    if current_game["mode"] == "easy":
        current_game["known_letters"].update(
            letter for letter, color in zip(guess, colors) if color >= 2
        )
        result["free_letters"] = free_letter_state(current_game)

    return jsonify(result)


@app.route("/api/start", methods=["POST"])
def start_game():
    data = request.get_json(silent=True) if request.is_json and request.get_data() else {}
    if not isinstance(data, dict):
        return jsonify({"valid": False, "message": "Invalid Request"}), 400

    mode = data.get("mode", "classic")
    if not isinstance(mode, str) or mode not in GAME_MODES:
        return jsonify({"valid": False, "message": "Unknown game mode"}), 400

    # load game list once
    if not game.ANSWER_LIST:
        game.LoadLists()
    #  use existing random answer fuction from game.py
    answer = game.GetRandomAnswer()

    #  keep the answer and guess history on the server
    game_id = uuid4().hex
    current_game = {
        "answer": answer,
        "guesses": [],
        "mode": mode,
        "lock": Lock(),
    }
    result = {"game_id": game_id, "mode": mode, "message": "Game started"}
    if mode == "easy":
        current_game["known_letters"] = set()
        current_game["revealed_letters"] = []
        result["free_letters"] = free_letter_state(current_game)
    games[game_id] = current_game
    return jsonify(result)


def free_letter_state(current_game):
    letters = current_game["revealed_letters"]
    used = len(letters)
    return {
        "letters": letters.copy(),
        "used": used,
        "limit": MAX_FREE_LETTERS,
        "available": (
            not current_game.get("finished", False)
            and used < MAX_FREE_LETTERS
            and not current_game["known_letters"].issuperset(current_game["answer"])
        ),
    }


@app.route("/api/free-letter", methods=["POST"])
def reveal_letter():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"valid": False, "message": "Invalid Request"}), 400

    game_id = data.get("game_id")
    if not isinstance(game_id, str) or game_id not in games:
        return jsonify({"valid": False, "message": "Game not found"}), 400

    current_game = games[game_id]
    if current_game["mode"] != "easy":
        return jsonify({"valid": False, "message": "Free Letter is only available in Easy Mode"}), 400

    with current_game["lock"]:
        state = free_letter_state(current_game)
        if not state["available"]:
            if current_game.get("finished", False):
                message = "Game already finished"
            elif state["used"] == state["limit"]:
                message = "Free Letter limit reached"
            else:
                message = "No new letters left to reveal"
            return jsonify({"valid": False, "message": message, "free_letters": state}), 400

        letter = game.GetEasyModeLetter(current_game["answer"], current_game["known_letters"])
        current_game["revealed_letters"].append(letter)
        current_game["known_letters"].add(letter)
        return jsonify({
            "valid": True,
            "letter": letter,
            "free_letters": free_letter_state(current_game),
        })

if __name__ == "__main__":
    # starts flask with development debugging enabled
    app.run(debug=True)
