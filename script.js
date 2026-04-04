const STORAGE_KEYS = {
  cards: "expenseflow-cards",
  expenses: "expenseflow-expenses",
};

const cardThemes = {
  sunset: "card-theme-sunset",
  midnight: "card-theme-midnight",
  ocean: "card-theme-ocean",
  forest: "card-theme-forest",
};

const state = {
  cards: loadData(STORAGE_KEYS.cards),
  expenses: loadData(STORAGE_KEYS.expenses),
};

const tabButtons = document.querySelectorAll(".tab-button");
const walletPanel = document.getElementById("walletPanel");
const expensesPanel = document.getElementById("expensesPanel");
const cardForm = document.getElementById("cardForm");
const expenseForm = document.getElementById("expenseForm");
const cardStack = document.getElementById("cardStack");
const expenseList = document.getElementById("expenseList");
const categorySummary = document.getElementById("categorySummary");
const expenseCardSelect = document.getElementById("expenseCard");
const totalSpent = document.getElementById("totalSpent");
const topCategory = document.getElementById("topCategory");
const savedCards = document.getElementById("savedCards");
const clearExpensesButton = document.getElementById("clearExpenses");
const expenseDateInput = document.getElementById("expenseDate");

expenseDateInput.value = new Date().toISOString().split("T")[0];

tabButtons.forEach((button) => {
  button.addEventListener("click", () => switchTab(button.dataset.tab));
});

cardForm.addEventListener("submit", (event) => {
  event.preventDefault();

  const card = {
    id: crypto.randomUUID(),
    holder: document.getElementById("cardHolder").value.trim(),
    number: formatCardNumber(document.getElementById("cardNumber").value),
    expiry: document.getElementById("cardExpiry").value.trim(),
    theme: document.getElementById("cardTheme").value,
  };

  state.cards.unshift(card);
  saveData(STORAGE_KEYS.cards, state.cards);
  cardForm.reset();
  renderApp();
});

expenseForm.addEventListener("submit", (event) => {
  event.preventDefault();

  const expense = {
    id: crypto.randomUUID(),
    title: document.getElementById("expenseTitle").value.trim(),
    amount: Number(document.getElementById("expenseAmount").value),
    category: document.getElementById("expenseCategory").value,
    date: document.getElementById("expenseDate").value,
    cardId: expenseCardSelect.value,
  };

  state.expenses.unshift(expense);
  saveData(STORAGE_KEYS.expenses, state.expenses);
  expenseForm.reset();
  expenseDateInput.value = new Date().toISOString().split("T")[0];
  renderApp();
});

clearExpensesButton.addEventListener("click", () => {
  state.expenses = [];
  saveData(STORAGE_KEYS.expenses, state.expenses);
  renderApp();
});

renderApp();

function switchTab(tab) {
  const isWallet = tab === "wallet";

  tabButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.tab === tab);
  });

  walletPanel.classList.toggle("active", isWallet);
  expensesPanel.classList.toggle("active", !isWallet);
}

function renderApp() {
  renderCards();
  renderCardOptions();
  renderExpenses();
  renderSummary();
  renderSidebarStats();
}

function renderCards() {
  if (!state.cards.length) {
    cardStack.innerHTML = `
      <div class="empty-state">
        No cards saved yet. Add one to create your wallet stack.
      </div>
    `;
    return;
  }

  cardStack.innerHTML = state.cards
    .map(
      (card) => `
        <article class="payment-card ${cardThemes[card.theme] || cardThemes.sunset}">
          <div class="card-top">
            <div class="card-chip" aria-hidden="true"></div>
            <div class="card-brand">PAY</div>
          </div>
          <div class="card-number">${maskCardNumber(card.number)}</div>
          <div class="card-bottom">
            <div class="card-meta">
              <span>Card Holder</span>
              <strong>${escapeHtml(card.holder)}</strong>
            </div>
            <div class="card-meta">
              <span>Expires</span>
              <strong>${escapeHtml(card.expiry)}</strong>
            </div>
          </div>
        </article>
      `,
    )
    .join("");
}

function renderCardOptions() {
  const options = state.cards
    .map(
      (card) =>
        `<option value="${card.id}">${escapeHtml(card.holder)} - ${maskCardNumber(card.number)}</option>`,
    )
    .join("");

  expenseCardSelect.innerHTML = `<option value="">Cash / Other</option>${options}`;
}

function renderExpenses() {
  if (!state.expenses.length) {
    expenseList.innerHTML = `
      <div class="empty-state">
        No expenses yet. Add your first transaction to see calculations here.
      </div>
    `;
    return;
  }

  expenseList.innerHTML = state.expenses
    .map((expense) => {
      const cardLabel = getCardLabel(expense.cardId);
      return `
        <article class="expense-item">
          <div>
            <h4>${escapeHtml(expense.title)}</h4>
            <p>${escapeHtml(expense.category)} - ${formatDate(expense.date)} - ${escapeHtml(cardLabel)}</p>
          </div>
          <div class="expense-amount">${formatCurrency(expense.amount)}</div>
        </article>
      `;
    })
    .join("");
}

function renderSummary() {
  const grouped = state.expenses.reduce((accumulator, expense) => {
    accumulator[expense.category] = (accumulator[expense.category] || 0) + expense.amount;
    return accumulator;
  }, {});

  const entries = Object.entries(grouped).sort((a, b) => b[1] - a[1]);

  if (!entries.length) {
    categorySummary.innerHTML = `
      <div class="empty-state">
        Category totals will appear here after you add expenses.
      </div>
    `;
    return;
  }

  categorySummary.innerHTML = entries
    .map(
      ([category, amount]) => `
        <article class="summary-card">
          <h4>${escapeHtml(category)}</h4>
          <strong>${formatCurrency(amount)}</strong>
          <p>${percentageOfTotal(amount)} of your total spend</p>
        </article>
      `,
    )
    .join("");
}

function renderSidebarStats() {
  const total = state.expenses.reduce((sum, expense) => sum + expense.amount, 0);
  const categoryTotals = state.expenses.reduce((accumulator, expense) => {
    accumulator[expense.category] = (accumulator[expense.category] || 0) + expense.amount;
    return accumulator;
  }, {});
  const leadingCategory = Object.entries(categoryTotals).sort((a, b) => b[1] - a[1])[0];

  totalSpent.textContent = formatCurrency(total);
  topCategory.textContent = leadingCategory
    ? `${leadingCategory[0]} - ${formatCurrency(leadingCategory[1])}`
    : "No data yet";
  savedCards.textContent = `${state.cards.length} ${state.cards.length === 1 ? "card" : "cards"}`;
}

function getCardLabel(cardId) {
  const card = state.cards.find((item) => item.id === cardId);
  if (!card) {
    return "Cash / Other";
  }

  return `${card.holder} - ${maskCardNumber(card.number)}`;
}

function percentageOfTotal(amount) {
  const total = state.expenses.reduce((sum, expense) => sum + expense.amount, 0);
  if (!total) {
    return "0%";
  }

  return `${Math.round((amount / total) * 100)}%`;
}

function formatCurrency(value) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(value || 0);
}

function formatDate(value) {
  if (!value) {
    return "No date";
  }

  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(new Date(`${value}T00:00:00`));
}

function formatCardNumber(value) {
  return value
    .replace(/\D/g, "")
    .slice(0, 16)
    .replace(/(\d{4})(?=\d)/g, "$1 ")
    .trim();
}

function maskCardNumber(value) {
  const digits = value.replace(/\D/g, "");
  const lastFour = digits.slice(-4);
  return `**** ${lastFour}`;
}

function loadData(key) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : [];
  } catch (error) {
    return [];
  }
}

function saveData(key, data) {
  localStorage.setItem(key, JSON.stringify(data));
}

function escapeHtml(value) {
  return value.replace(/[&<>"']/g, (char) => {
    const entities = {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;",
    };
    return entities[char];
  });
}
