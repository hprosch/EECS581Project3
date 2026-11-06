/*
    author: christopher brush
    file description: connects the wordle board and keyboard to the flask game api
    added: starts games, submits guesses, displays feedback, and handles game over
*/

const tiles = document.querySelectorAll(".tile");
const buttons = document.querySelectorAll(".key");
const status = document.querySelector("#status");

let row = 0;
let column = 0;
let gameId = null;
let gameOver = false;
let submitting = false;

function set_status(message) {
    status.textContent = message;
}

function update_keyboard(guess, colors) {
    for (let index = 0; index < guess.length; index++) {
        const key = document.querySelector(`.key[data-letter="${guess[index]}"]`);
        if (!key) {
            continue;
        }

        const nextClass = colors[index] === 3 ? "correct"
            : colors[index] === 2 ? "present" : "absent";
        const currentClass = key.dataset.state;
        const priority = { absent: 1, present: 2, correct: 3 };
        if (!currentClass || priority[nextClass] > priority[currentClass]) {
            key.classList.remove("absent", "present", "correct");
            key.classList.add(nextClass);
            key.dataset.state = nextClass;
        }
    }
}

async function submit_guess() {
    if (column !== 5 || !gameId || gameOver || submitting) {
        return;
    }

    submitting = true;
    const guess = Array.from({ length: 5 }, (_, index) =>
        tiles[row * 5 + index].textContent.toLowerCase()).join("");

    try {
        const response = await fetch("/api/guess", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ game_id: gameId, guess: guess })
        });
        const result = await response.json();

        if (!response.ok || !result.valid) {
            set_status(result.message || "That word is not valid.");
            return;
        }

        for (let index = 0; index < result.colors.length; index++) {
            const tile = tiles[row * 5 + index];
            tile.classList.add(result.colors[index] === 3 ? "correct"
                : result.colors[index] === 2 ? "present" : "absent");
        }
        update_keyboard(guess, result.colors);

        if (result.won) {
            gameOver = true;
            set_status("You win!");
        } else if (result.game_over) {
            gameOver = true;
            set_status(`Game over. The answer was ${result.answer.toUpperCase()}.`);
        } else {
            row++;
            column = 0;
            set_status("");
        }
    } catch (error) {
        set_status("Unable to submit guess. Please try again.");
    } finally {
        submitting = false;
    }
}

function handle_key(key) {
    if (row >= 6 || gameOver || !gameId || submitting) {
        return;
    }

    if (key === "Backspace") {
        if (column > 0) {
            column--;
            const index = row * 5 + column;
            tiles[index].textContent = "";
        }
        return;
    }

    if (key === "Enter") {
        submit_guess();
        return;
    }

    const letter = key.toUpperCase();
    if ((letter.length === 1) && (letter >= "A") && (letter <= "Z") && (column < 5)) {
        const index = row * 5 + column;
        tiles[index].textContent = letter;
        column++;
    }
}

for (const button of buttons){
    button.addEventListener("click", function () {
        handle_key(button.textContent.trim());
    });
}

document.addEventListener("keydown", function (event) {
    if (["Enter", "Backspace", " "].includes(event.key)) {
        event.preventDefault();
    }
    handle_key(event.key);
});

async function start_game() {
    try {
        const response = await fetch("/api/start", { method: "POST" });
        const result = await response.json();
        if (!response.ok || !result.game_id) {
            throw new Error("game start failed");
        }
        gameId = result.game_id;
        set_status("Enter a five-letter word.");
    } catch (error) {
        set_status("Unable to start the game. Please refresh the page.");
    }
}

for (const button of buttons) {
    const label = button.textContent.trim().toLowerCase();
    if (label.length === 1) {
        button.dataset.letter = label;
    }
}

start_game();
