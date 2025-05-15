const iconBtn = document.getElementById("info-icon");
const modal = document.getElementById("info-modal");
const closeBtn = document.getElementById("close-modal");

iconBtn.addEventListener("click", () => {
    modal.classList.remove("hidden");
});

closeBtn.addEventListener("click", () => {
    modal.classList.add("hidden");
});

window.addEventListener("click", (e) => {
    if (e.target === modal) {
        modal.classList.add("hidden");
    }
});