/*
File Description: start.js opens and closes the Start dropdown without starting a Wordle game. - RPM 11.15
Inputs: mouse, touch, keyboard, focus, and page navigation events.
Outputs: updates the menu's visibility and the Start button's expanded state. - RPM 11.15

Generative Artificial Intelligence Usage Documentation and Listing:
1. How/Why AI: I used ChatGPT to make the Start dropdown work for mouse, touch, and keyboard input. - RPM 11.15
2. Prompts: "Treat the trigger and dropdown as one continuous hover area while the dropdown is open."
            "Escape closes the list and returns focus to Start." - RPM 11.15
3. Validation/Revision: Did browser checks of the hover path, keyboard navigation, and touch input.
                        After adding Multiplayer and Adventure, the narrow layout was adjusted and retested. - RPM 11.15
4. Challenges/Limitations: Moving the mouse from Start to Hard Mode could close the menu if the gap wasn't covered.
                           The dropdown also had to avoid covering Adventure when the buttons wrapped. - RPM 11.15
*/

const startControls = document.querySelector(".start-controls");
const startButton = document.querySelector("#start-button");
const modeOptions = document.querySelector("#mode-options");

// keep the menu and Start button in the same open or closed state - RPM 11.15
function set_modes_open(open) {
    modeOptions.hidden = !open; // hides the menu when open is false - RPM 11.15
    startButton.setAttribute("aria-expanded", String(open));
}

// close the menu and return focus to Start if it was on a mode option - RPM 11.15
function close_modes() {
    if (modeOptions.contains(document.activeElement)) {
        startButton.focus();
    }
    set_modes_open(false);
}

// open the dropdown when a mouse moves onto Start - RPM 11.15
startButton.addEventListener("pointerenter", (event) => {
    if (event.pointerType === "mouse") {
        set_modes_open(true);
    }
});

// close it after the mouse leaves Start and its dropdown together - RPM 11.15
startControls.addEventListener("pointerleave", (event) => {
    if (event.pointerType === "mouse") {
        close_modes();
    }
});

// let tapping Start toggle the dropdown while keyboard activation opens it - RPM 11.15
startButton.addEventListener("click", (event) => {
    const toggle = event.detail !== 0 && event.pointerType !== "mouse"; // distinguishes taps from mouse and keyboard clicks - RPM 11.15
    set_modes_open(!toggle || modeOptions.hidden);
});

// close when keyboard focus leaves the Start controls - RPM 11.15
startControls.addEventListener("focusout", (event) => {
    if (!startControls.contains(event.relatedTarget)) {
        set_modes_open(false);
    }
});

// clicking outside should dismiss the modes - RPM 11.15
document.addEventListener("pointerdown", (event) => {
    if (!startControls.contains(event.target)) {
        set_modes_open(false);
    }
});

// Escape closes the list and returns focus to Start - RPM 11.15
document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !modeOptions.hidden) {
        event.preventDefault();
        startButton.focus();
        set_modes_open(false);
    }
});

// reset the dropdown when returning to a cached page with Back - RPM 11.15
window.addEventListener("pageshow", (event) => {
    if (event.persisted) {
        close_modes();
    }
});