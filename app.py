from flask import Flask, render_template, jsonify
from uuid import uuid4
import game

# create flask application, and stores it to 'app' variable
app = Flask(__name__)

# store each game's answer and previous guesses on server
# browswer only recievs a game id, not the answer
games = {}

#defines what happens when someone visits home page
@app.route("/")

#function represents home page
def home():
    # loads HTML file from templates/
    return render_template("index.html")

#  create new game without changing existing front end
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
