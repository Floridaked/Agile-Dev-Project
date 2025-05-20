document.addEventListener("DOMContentLoaded", function () {
    // Handle water streak modal (with confetti)
    const waterModal = document.getElementById("water-streak-modal");
    const closeWaterBtn = document.getElementById("close-water-streak-modal");

    if (waterModal) {
        waterModal.classList.remove("hidden");

        // Trigger confetti animation
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

        closeWaterBtn.addEventListener("click", () => {
            waterModal.classList.add("hidden");
        });

        window.addEventListener("click", (e) => {
            if (e.target === waterModal) {
                waterModal.classList.add("hidden");
            }
        });
    }

    // Handle info or warning modal (no confetti)
    const infoWarningModal = document.getElementById("info-warning-modal");
    const closeInfoWarningBtn = document.getElementById("close-info-warning-modal");

    if (infoWarningModal) {
        infoWarningModal.classList.remove("hidden");

        closeInfoWarningBtn.addEventListener("click", () => {
            infoWarningModal.classList.add("hidden");
        });

        window.addEventListener("click", (e) => {
            if (e.target === infoWarningModal) {
                infoWarningModal.classList.add("hidden");
            }
        });
    }
});