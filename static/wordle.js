/*
authors: christopher brush, ruben pino-martinez
file description: connects the wordle board and keyboard to the flask game api
added: starts games, submits guesses, displays feedback, and handles game over
Inputs: keyboard events, game button clicks, the selected mode, and JSON responses from Flask.
Outputs: updated tiles, guess feedback, messages, and Easy Mode letter status.

Generative Artificial Intelligence Usage Documentation and Listing:
1. How/Why AI: RPM used ChatGPT to connect the mode selection and Free Letter button to the existing game,
               without replacing Chris's New Game controls or the team's guess logic. - RPM 11.16
2. Prompts: "Preserve the grid, keyboard, guess submission, colored feedback, and win/loss messages." - RPM 11.16
3. Validation/Revision: Tested Main Menu after guesses and completed games.
4. Challenges/Limitations: Easy Mode can run out of distinct unknown letters before 5/5. I followed up on the
                           3/5 and 4/5 cases to understand why a reveal was no longer available. - RPM 11.16
*/

const tiles = document.querySelectorAll(".tile");
const buttons = document.querySelectorAll(".key");
const status = document.querySelector("#status");
const mode = document.body.dataset.mode; // reads Classic, Easy, or Hard from the page - RPM 11.16
const restartButton = document.querySelector("#restart-button"); // find the restart button in the page
const hintButton = document.querySelector("#hint-button"); // find the hint button in the page
const freeLetterButton = document.querySelector("#free-letter-button"); // finds the button only shown in Easy Mode - RPM 11.16
const freeLetterStatus = document.querySelector("#free-letter-status"); // where the revealed letters and count appear - RPM 11.16
const hintStatus = document.querySelector("#hint-notification")
let row = 0;
let column = 0;
let gameId = null;
let gameOver = false;
let submitting = false;
let freeLetters = null; // keeps the Free Letter state returned by Flask - RPM 11.16
let revealing = false; // blocks overlapping Free Letter requests - RPM 11.16

function set_status(message) {
    status.textContent = message;
}
function set_hint(message){
    hintStatus.textContent = message;
}
// update whether Free Letter can be used right now - RPM 11.16
function update_free_letter_button() {
    if (freeLetterButton) {
        const available = freeLetters?.available && !submitting && !revealing; // checks the server limit and current requests - RPM 11.16
        freeLetterButton.setAttribute("aria-disabled", String(!available));
    }
}

// show how many free letters were used and which letters were learned - RPM 11.16
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

    const letters = state.letters.map(letter => letter.toUpperCase()).join(", "); // shows letters without their positions - RPM 11.16
    const revealed = letters ? `Revealed letters: ${letters}. ` : "";
    const exhausted = !state.available && !gameOver && state.used < state.limit
        ? " No new letters left to reveal." : "";
    const message = `${revealed}Free letters used: ${state.used}/${state.limit}.${exhausted}`;
    if (freeLetterStatus.textContent !== message) {
        freeLetterStatus.textContent = message;
    }
    update_free_letter_button();
}

// ask Flask for one new answer letter, without using a guess - RPM 11.16
async function request_free_letter() {
    if (freeLetterButton.getAttribute("aria-disabled") === "true") {
        return;
    }
    const requestGameId = gameId;
    revealing = true;
    update_free_letter_button();
    try {
        const response = await fetch("/api/free-letter", { // sends the current game ID to the Free Letter route - RPM 11.16
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ game_id: requestGameId })
        });
        const result = await response.json();
        if (requestGameId !== gameId) { // ignores a reveal from a game that was restarted - RPM 11.16
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
// Daniel Van Dalsem (11/20/2026)
// This is mostly just taken from request_free_letter with modifications
// shows the hint
async function get_hint(){
        const requestGameId = gameId;
    revealing = true;

    try {
        const response = await fetch("/api/get-hint", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ game_id: requestGameId })
        });
        const result = await response.json();
        if (requestGameId !== gameId) {
            return;
        }
        if (result.hint) {
            set_hint(result.hint || "Unable to show a hint. Please try again.")

        } else {
            set_status(result.message || "Unable to show a hint. Please try again.");
        }
    } catch (error) {
        if (requestGameId === gameId) {
            set_status("Unable to show a hint. Please try again.");
        }
    } finally {
        if (requestGameId === gameId) {
            revealing = false;
        }
    }}
async function submit_guess() {
    if (column !== 5 || !gameId || gameOver || submitting || revealing) { // also waits while a letter reveal is running - RPM 11.16
        return;
    }

    submitting = true;
    update_free_letter_button(); // disables Free Letter while submitting a guess - RPM 11.16
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
            set_hint("");
        } else if (result.game_over) {
            gameOver = true;
            set_status(`Game over. The answer was ${result.answer.toUpperCase()}.`);
            set_hint("");
        } else {
            row++;
            column = 0;
            set_status("");
            set_hint("");
        }
        if (result.free_letters) { // reads updated Free Letter state after a valid guess - RPM 11.16
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
        if (document.activeElement === freeLetterButton) { // moves focus off Free Letter when typing a guess - RPM 11.16
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
    if (event.key === "Enter" && event.target.closest(".controls a")) { // lets Enter follow the Main Menu link - RPM 11.15
        return;
    }
    if (event.target === freeLetterButton && ["Enter", " "].includes(event.key)) { // lets the button handle its own keyboard click - RPM 11.16
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
            body: JSON.stringify({ mode }) // sends the selected mode when starting a session - RPM 11.16
        });
        const result = await response.json();
        if (!response.ok || !result.game_id) {
            throw new Error("game start failed");
        }
        gameId = result.game_id;
        if (result.free_letters) { // starts Easy Mode with the server-provided reveal count - RPM 11.16
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
    revealing = false; // clears any ongoing Free Letter request - RPM 11.16
    show_free_letters(null); // resets the reveal display for a new game - RPM 11.16
} // end of reset_board

async function restart_game() { // resets the grid and starts a brand new game
    reset_board(); // clear the board and keyboard
    set_status("Starting new game..."); // tell the player a new game is loading
    await start_game(); // ask the server for a new game and answer
} // end of restart_game

async function show_hint() { // placeholder for the hint feature
    await get_hint()
} // end of show_hint

restartButton.addEventListener("click", function () { // run when the restart button is clicked
    restart_game(); // reset everything and start a new game
    restartButton.blur(); // remove focus so keyboard input goes to the game
}); // end of restart click listener

hintButton.addEventListener("click", function () { // run when the hint button is clicked
    show_hint(); // show the placeholder message
    hintButton.blur(); // remove focus so keyboard input goes to the game
}); // end of hint click listener

// connect the Easy Mode button to its Flask request - RPM 11.16
freeLetterButton?.addEventListener("click", event => {
    if (event.detail > 0) {
        freeLetterButton.blur();
    }
    request_free_letter();
});
start_game();