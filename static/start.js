const startControls = document.querySelector(".start-controls");
const startButton = document.querySelector("#start-button");
const modeOptions = document.querySelector("#mode-options");

function set_modes_open(open) {
    modeOptions.hidden = !open;
    startButton.setAttribute("aria-expanded", String(open));
}

function close_modes() {
    if (modeOptions.contains(document.activeElement)) {
        startButton.focus();
    }
    set_modes_open(false);
}

startButton.addEventListener("pointerenter", (event) => {
    if (event.pointerType === "mouse") {
        set_modes_open(true);
    }
});

startControls.addEventListener("pointerleave", (event) => {
    if (event.pointerType === "mouse") {
        close_modes();
    }
});

startButton.addEventListener("click", (event) => {
    const toggle = event.detail !== 0 && event.pointerType !== "mouse";
    set_modes_open(!toggle || modeOptions.hidden);
});

startControls.addEventListener("focusout", (event) => {
    if (!startControls.contains(event.relatedTarget)) {
        set_modes_open(false);
    }
});

document.addEventListener("pointerdown", (event) => {
    if (!startControls.contains(event.target)) {
        set_modes_open(false);
    }
});

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !modeOptions.hidden) {
        event.preventDefault();
        startButton.focus();
        set_modes_open(false);
    }
});

window.addEventListener("pageshow", (event) => {
    if (event.persisted) {
        close_modes();
    }
});