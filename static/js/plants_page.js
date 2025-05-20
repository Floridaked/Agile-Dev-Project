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


document.addEventListener("DOMContentLoaded", function () {
const streakModal = document.getElementById("streak-modal");
const closeStreak = document.getElementById("close-streak-modal");

if (streakModal) {
    streakModal.classList.remove("hidden");

    for (let i = 0; i < 3; i++) {
        setTimeout(() => {
            confetti({
                particleCount: 200,
                angle: 90,
                spread: 100,
                startVelocity: 70,
                gravity: 0.6,
                ticks: 300,
                origin: { 
                    x: 0.45 + Math.random() * 0.1,
                    y: 0.5 
                },
                zIndex: 10000
            });
        }, i * 150);
    }

    closeStreak.addEventListener("click", () => {
        streakModal.classList.add("hidden");
    });

    window.addEventListener("click", (e) => {
        if (e.target === streakModal) {
            streakModal.classList.add("hidden");
        }
    });
}
});