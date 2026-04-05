const tabButtons = document.querySelectorAll(".tab-button");
const panels = document.querySelectorAll(".panel");
const swipeCards = document.querySelectorAll("[data-swipe-card]");
const swipeWidth = 112;
const cardDetailsModal = document.getElementById("cardDetailsModal");
const closeCardModal = document.getElementById("closeCardModal");
const revealCardId = document.getElementById("revealCardId");
const modalCardTitle = document.getElementById("modalCardTitle");
const revealCardForm = document.getElementById("revealCardForm");
const revealedCardPanel = document.getElementById("revealedCardPanel");
const accountPassword = document.getElementById("accountPassword");
const documentDetailsModal = document.getElementById("documentDetailsModal");
const closeDocumentModal = document.getElementById("closeDocumentModal");
const revealDocumentId = document.getElementById("revealDocumentId");
const modalDocumentTitle = document.getElementById("modalDocumentTitle");
const revealDocumentForm = document.getElementById("revealDocumentForm");
const revealedDocumentPanel = document.getElementById("revealedDocumentPanel");
const documentAccountPassword = document.getElementById("documentAccountPassword");
const balanceEditButton = document.getElementById("balanceEditButton");
const balanceEditForm = document.getElementById("balanceEditForm");
const nfcLinks = document.querySelectorAll("[data-nfc-link]");
const documentForm = document.querySelector("[data-document-form]");
const documentTypeField = documentForm?.querySelector('select[name="document_type"]');
const documentFieldGroups = documentForm?.querySelectorAll("[data-document-fields]");

tabButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const activeTab = button.dataset.tab;

    tabButtons.forEach((item) => {
      item.classList.toggle("active", item === button);
    });

    panels.forEach((panel) => {
      panel.classList.toggle("active", panel.id === `${activeTab}Panel`);
    });
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
      if (surface.dataset.openModal === "document") {
        openDocumentModal(surface);
      } else if (surface.dataset.openModal === "card") {
        openCardModal(surface);
      }
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
  if (revealCardForm) {
    revealCardForm.classList.remove("hidden");
  }
  if (revealedCardPanel) {
    revealedCardPanel.classList.add("hidden");
  }
  if (balanceEditForm) {
    balanceEditForm.classList.add("hidden");
  }
  if (accountPassword) {
    accountPassword.value = "";
  }
  cardDetailsModal.classList.add("visible");
}

function openDocumentModal(surface) {
  if (!documentDetailsModal) {
    return;
  }

  revealDocumentId.value = surface.dataset.documentId || "";
  modalDocumentTitle.textContent = `${surface.dataset.documentTitle || "Document"} details`;
  if (revealDocumentForm) {
    revealDocumentForm.classList.remove("hidden");
  }
  if (revealedDocumentPanel) {
    revealedDocumentPanel.classList.add("hidden");
  }
  if (documentAccountPassword) {
    documentAccountPassword.value = "";
  }
  documentDetailsModal.classList.add("visible");
}

if (closeCardModal) {
  closeCardModal.addEventListener("click", () => {
    cardDetailsModal.classList.remove("visible");
  });
}

if (closeDocumentModal) {
  closeDocumentModal.addEventListener("click", () => {
    documentDetailsModal.classList.remove("visible");
  });
}

if (cardDetailsModal) {
  cardDetailsModal.addEventListener("click", (event) => {
    if (event.target === cardDetailsModal) {
      cardDetailsModal.classList.remove("visible");
    }
  });
}

if (documentDetailsModal) {
  documentDetailsModal.addEventListener("click", (event) => {
    if (event.target === documentDetailsModal) {
      documentDetailsModal.classList.remove("visible");
    }
  });
}

if (balanceEditButton && balanceEditForm) {
  balanceEditButton.addEventListener("click", () => {
    balanceEditForm.classList.toggle("hidden");
  });
}

nfcLinks.forEach((link) => {
  link.addEventListener("click", (event) => {
    const storeUrl = link.dataset.storeUrl || link.href;
    const appIntent = link.dataset.appIntent;
    const iosAppUrl = link.dataset.iosAppUrl;
    const iosStoreUrl = link.dataset.iosStoreUrl || storeUrl;
    const isAndroid = /Android/i.test(window.navigator.userAgent);
    const isIOS = /iPhone|iPad|iPod/i.test(window.navigator.userAgent);

    if (!isAndroid && !isIOS) {
      return;
    }

    event.preventDefault();

    let fallbackTriggered = false;
    const fallbackTimer = window.setTimeout(() => {
      fallbackTriggered = true;
      window.location.href = isIOS ? iosStoreUrl : storeUrl;
    }, 1400);

    const cancelFallback = () => {
      if (document.hidden && !fallbackTriggered) {
        window.clearTimeout(fallbackTimer);
      }
    };

    document.addEventListener("visibilitychange", cancelFallback, { once: true });
    window.location.href = isIOS ? iosAppUrl || iosStoreUrl : appIntent;
  });
});

if (documentTypeField && documentFieldGroups) {
  const syncDocumentFields = () => {
    const activeType = documentTypeField.value;

    documentFieldGroups.forEach((group) => {
      group.classList.toggle("active", group.dataset.documentFields === activeType);
    });
  };

  documentTypeField.addEventListener("change", syncDocumentFields);
  syncDocumentFields();
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
