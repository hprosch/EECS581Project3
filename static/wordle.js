// stores the class' from CSS
const tiles = document.querySelectorAll(".tile");
const buttons = document.querySelectorAll(".key");

let row = 0;
let column = 0;

function handle_key(key) {
    // stop when all 6 rows have been used
    if (row >= 6) {
        return;
    }

    // reduces column count and makes the index of the column blank
    if (key === "Backspace") {
        if (column > 0) {
            column--;
            const index = row * 5 + column;
            tiles[index].textContent = "";
        }
        return
    }

    // checks if the column is at 5 total letters, increases row count and starts the collumn over
    if (key === "Enter") {
        if (column === 5) {
            row++;
            column = 0;
        }
        return;
    }

    // changes the letter to be capitalized
    const letter = key.toUpperCase();
    // checks if the length of letter is exactly 1, between A-Z, and if less than 5 letters
    if ((letter.length === 1) && (letter >= "A") && (letter <= "Z") && (column < 5)) {
        const index = row * 5 + column;
        // makes whatever the current index to be what letter it is
        tiles[index].textContent = letter;
        // then increases the collumn
        column++;
    }
}
//  makes each on screen button call the same function
for (const button of buttons){
    button.addEventListener("click", function () {
        handle_key(button.textContent.trim());
    });
}

//  allows letters , backspace, and enter on physical keybaord
document.addEventListener("keydown", function (event) {
    handle_key(event.key);
});