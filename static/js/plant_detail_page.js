
document.addEventListener("DOMContentLoaded", function () {
    const waterModal = document.getElementById("water-streak-modal");
    const closeBtn = document.getElementById("close-water-streak-modal");

    if (waterModal) {
        waterModal.classList.remove("hidden");

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
        


        closeBtn.addEventListener("click", () => {
            waterModal.classList.add("hidden");
        });

        window.addEventListener("click", (e) => {
            if (e.target === waterModal) {
                waterModal.classList.add("hidden");
            }
        });
    }
});
