from flask import Flask, render_template, jsonify, request
from uuid import uuid4
import game

# create flask application, and stores it to 'app' variable
app = Flask(__name__)

# store each game's answer and previous guesses on server
# browswer only recievs a game id, not the answer
games = {}

MAX_GUESSES = 6

#defines what happens when someone visits home page
@app.route("/")

#function represents home page
def home():
    # loads HTML file from templates/
    return render_template("index.html")

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

    # prevent guesses after the game has ended
    if current_game.get("finished", False):
        return jsonify({"valid": False, "message": "Game already finished"}), 400

    # use Eden's function to validate the guess
    if not game.ValidateGuess(guess, current_game["guesses"]):
        return jsonify({"valid": False, "message": "Invalid or repeated word"}), 400

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

    return jsonify(result)


@app.route("/api/start", methods=["POST"])
def start_game():
    # load game list once
    if not game.ANSWER_LIST:
        game.LoadLists()
    #  use existing random answer fuction from game.py
    answer = game.GetRandomAnswer()

    #  keep the answer and guess history on the server
    game_id = uuid4().hex
    games[game_id] = {
        "answer": answer,
        "guesses": []
    }
    # do not send answer to browswer
    return jsonify({"game_id": game_id, "message": "Game started"})

if __name__ == "__main__":
    # starts flask with development debugging enabled
    app.run(debug=True)
