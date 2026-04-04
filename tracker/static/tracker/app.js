const tabButtons = document.querySelectorAll(".tab-button");
const walletPanel = document.getElementById("walletPanel");
const expensesPanel = document.getElementById("expensesPanel");
const swipeCards = document.querySelectorAll("[data-swipe-card]");
const swipeWidth = 112;
const cardDetailsModal = document.getElementById("cardDetailsModal");
const closeCardModal = document.getElementById("closeCardModal");
const revealCardId = document.getElementById("revealCardId");
const modalCardTitle = document.getElementById("modalCardTitle");
const balanceEditButton = document.getElementById("balanceEditButton");
const balanceEditForm = document.getElementById("balanceEditForm");

tabButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const isWallet = button.dataset.tab === "wallet";

    tabButtons.forEach((item) => {
      item.classList.toggle("active", item === button);
    });

    walletPanel.classList.toggle("active", isWallet);
    expensesPanel.classList.toggle("active", !isWallet);
  });
});

swipeCards.forEach((card) => {
  const surface = card.querySelector("[data-card-surface]");
  let startX = 0;
  let currentX = 0;
  let dragging = false;
  let moved = false;

  surface.addEventListener("pointerdown", (event) => {
    if (event.target.closest("button, form, a")) {
      return;
    }

    dragging = true;
    moved = false;
    startX = event.clientX;
    currentX = card.classList.contains("is-open") ? -swipeWidth : 0;
    surface.style.transition = "none";

    swipeCards.forEach((otherCard) => {
      if (otherCard !== card) {
        otherCard.classList.remove("is-open");
      }
    });
  });

  surface.addEventListener("pointermove", (event) => {
    if (!dragging) {
      return;
    }

    const deltaX = event.clientX - startX;
    if (Math.abs(deltaX) > 6) {
      moved = true;
    }
    const nextX = Math.max(-swipeWidth, Math.min(0, currentX + deltaX));
    surface.style.transform = `translateX(${nextX}px)`;
  });

  surface.addEventListener("pointerup", (event) => {
    finishSwipe(event.clientX);
  });

  surface.addEventListener("pointercancel", () => {
    finishSwipe(startX);
  });

  surface.addEventListener("click", (event) => {
    if (event.target.closest("[data-nfc-link]")) {
      return;
    }

    if (card.classList.contains("is-open")) {
      card.classList.remove("is-open");
      surface.style.transform = "";
      event.preventDefault();
      return;
    }

    if (!moved) {
      openCardModal(surface);
    }
  });

  function finishSwipe(endX) {
    if (!dragging) {
      return;
    }

    dragging = false;
    surface.style.transition = "";

    const movedBy = endX - startX;
    const shouldOpen = movedBy < -50 || currentX + movedBy < -70;
    card.classList.toggle("is-open", shouldOpen);
    surface.style.transform = "";
  }
});

function openCardModal(surface) {
  if (!cardDetailsModal) {
    return;
  }

  revealCardId.value = surface.dataset.cardId || "";
  modalCardTitle.textContent = `${surface.dataset.cardBank || "Card"} details`;
  cardDetailsModal.classList.add("visible");
}

if (closeCardModal) {
  closeCardModal.addEventListener("click", () => {
    cardDetailsModal.classList.remove("visible");
  });
}

if (cardDetailsModal) {
  cardDetailsModal.addEventListener("click", (event) => {
    if (event.target === cardDetailsModal) {
      cardDetailsModal.classList.remove("visible");
    }
  });
}

if (balanceEditButton && balanceEditForm) {
  balanceEditButton.addEventListener("click", () => {
    balanceEditForm.classList.toggle("hidden");
  });
}

document.addEventListener("pointerdown", (event) => {
  if (event.target.closest("[data-swipe-card]")) {
    return;
  }

  swipeCards.forEach((card) => {
    card.classList.remove("is-open");
    const surface = card.querySelector("[data-card-surface]");
    if (surface) {
      surface.style.transform = "";
    }
  });
});
