/*
    author: christopher brush
    file description: connects the wordle board and keyboard to the flask game api
    added: starts games, submits guesses, displays feedback, and handles game over
*/

const tiles = document.querySelectorAll(".tile");
const buttons = document.querySelectorAll(".key");
const status = document.querySelector("#status");
const mode = document.body.dataset.mode;
const restartButton = document.querySelector("#restart-button"); // find the restart button in the page
const hintButton = document.querySelector("#hint-button"); // find the hint button in the page
const freeLetterButton = document.querySelector("#free-letter-button");
const freeLetterStatus = document.querySelector("#free-letter-status");

let row = 0;
let column = 0;
let gameId = null;
let gameOver = false;
let submitting = false;
let freeLetters = null;
let revealing = false;

function set_status(message) {
    status.textContent = message;
}

function update_free_letter_button() {
    if (freeLetterButton) {
        const available = freeLetters?.available && !submitting && !revealing;
        freeLetterButton.setAttribute("aria-disabled", String(!available));
    }
}

function show_free_letters(state) {
    freeLetters = state;
    if (!freeLetterStatus) {
        return;
    }
    if (!state) {
        freeLetterStatus.textContent = "";
        update_free_letter_button();
        return;
    }

    const letters = state.letters.map(letter => letter.toUpperCase()).join(", ");
    const revealed = letters ? `Revealed letters: ${letters}. ` : "";
    const exhausted = !state.available && !gameOver && state.used < state.limit
        ? " No new letters left to reveal." : "";
    const message = `${revealed}Free letters used: ${state.used}/${state.limit}.${exhausted}`;
    if (freeLetterStatus.textContent !== message) {
        freeLetterStatus.textContent = message;
    }
    update_free_letter_button();
}

async function request_free_letter() {
    if (freeLetterButton.getAttribute("aria-disabled") === "true") {
        return;
    }
    const requestGameId = gameId;
    revealing = true;
    update_free_letter_button();
    try {
        const response = await fetch("/api/free-letter", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ game_id: requestGameId })
        });
        const result = await response.json();
        if (requestGameId !== gameId) {
            return;
        }
        if (result.free_letters) {
            show_free_letters(result.free_letters);
        } else {
            set_status(result.message || "Unable to reveal a letter. Please try again.");
        }
    } catch (error) {
        if (requestGameId === gameId) {
            set_status("Unable to reveal a letter. Please try again.");
        }
    } finally {
        if (requestGameId === gameId) {
            revealing = false;
            update_free_letter_button();
        }
    }
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
    if (column !== 5 || !gameId || gameOver || submitting || revealing) {
        return;
    }

    submitting = true;
    update_free_letter_button();
    const requestGameId = gameId; // remember which game this guess belongs to
    const guess = Array.from({ length: 5 }, (_, index) =>
        tiles[row * 5 + index].textContent.toLowerCase()).join("");

    try {
        const response = await fetch("/api/guess", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ game_id: requestGameId, guess: guess })
        });
        const result = await response.json();

        if (requestGameId !== gameId) { // ignore the response if the game was restarted meanwhile
            return; // do not draw old results on the new board
        } // end of stale response check

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
        if (result.free_letters) {
            show_free_letters(result.free_letters);
        }
    } catch (error) {
        if (requestGameId === gameId) {
            set_status("Unable to submit guess. Please try again.");
        }
    } finally {
        if (requestGameId === gameId) {
            submitting = false;
            update_free_letter_button();
        }
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
        if (document.activeElement === freeLetterButton) {
            freeLetterButton.blur();
        }
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
    if (event.key === "Enter" && event.target.closest(".controls a")) {
        return;
    }
    if (event.target === freeLetterButton && ["Enter", " "].includes(event.key)) {
        return;
    }
    if (["Enter", "Backspace", " "].includes(event.key)) {
        event.preventDefault();
    }
    handle_key(event.key);
});

async function start_game() {
    restartButton.disabled = true;
    try {
        const response = await fetch("/api/start", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ mode })
        });
        const result = await response.json();
        if (!response.ok || !result.game_id) {
            throw new Error("game start failed");
        }
        gameId = result.game_id;
        if (result.free_letters) {
            show_free_letters(result.free_letters);
        }
        set_status("Enter a five-letter word.");
    } catch (error) {
        set_status("Unable to start the game. Please refresh the page.");
    } finally {
        restartButton.disabled = false;
    }
}

for (const button of buttons) {
    const label = button.textContent.trim().toLowerCase();
    if (label.length === 1) {
        button.dataset.letter = label;
    }
}

function reset_board() { // clears the grid and keyboard back to their starting state
    for (const tile of tiles) { // loop over every tile on the board
        tile.textContent = ""; // remove the letter from the tile
        tile.classList.remove("absent", "present", "correct"); // remove the color feedback from the tile
    } // end of tile loop
    for (const button of buttons) { // loop over every keyboard button
        button.classList.remove("absent", "present", "correct"); // remove the color feedback from the key
        delete button.dataset.state; // forget the stored key state so colors can be set again
    } // end of keyboard loop
    row = 0; // go back to the first row
    column = 0; // go back to the first column
    gameId = null; // drop the old game id until a new one is created
    gameOver = false; // allow input again
    submitting = false; // clear any in-flight guess flag
    revealing = false;
    show_free_letters(null);
} // end of reset_board

async function restart_game() { // resets the grid and starts a brand new game
    reset_board(); // clear the board and keyboard
    set_status("Starting new game..."); // tell the player a new game is loading
    await start_game(); // ask the server for a new game and answer
} // end of restart_game

function show_hint() { // placeholder for the hint feature
    set_status("Hint coming soon!"); // tell the player the feature is not ready yet
} // end of show_hint

restartButton.addEventListener("click", function () { // run when the restart button is clicked
    restart_game(); // reset everything and start a new game
    restartButton.blur(); // remove focus so keyboard input goes to the game
}); // end of restart click listener

hintButton.addEventListener("click", function () { // run when the hint button is clicked
    show_hint(); // show the placeholder message
    hintButton.blur(); // remove focus so keyboard input goes to the game
}); // end of hint click listener

freeLetterButton?.addEventListener("click", event => {
    if (event.detail > 0) {
        freeLetterButton.blur();
    }
    request_free_letter();
});
start_game();