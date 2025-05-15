const moodIcon = document.getElementById("mood-info-icon");
const moodModal = document.getElementById("mood-info-modal");
const closeMood = document.getElementById("close-mood-modal");

moodIcon.addEventListener("click", () => {
    moodModal.classList.remove("hidden");
});

closeMood.addEventListener("click", () => {
    moodModal.classList.add("hidden");
});

window.addEventListener("click", (e) => {
    if (e.target === moodModal) {
        moodModal.classList.add("hidden");
    }
});
