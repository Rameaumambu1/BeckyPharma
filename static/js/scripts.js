// scripts.js
let cart = {};

function addToCart(id, nom, prix, quantite) {
  if (cart[id]) {
    cart[id].quantite += quantite;
  } else {
    cart[id] = { nom, prix, quantite };
  }
  updateCartCount();
  renderCartModal();
}

function updateCartCount() {
  const badge = document.querySelector('.btn-outline-primary .badge');
  badge.textContent = Object.keys(cart).length;
}

function renderCartModal() {
  const tbody = document.querySelector('#cartModal tbody');
  tbody.innerHTML = '';

  Object.entries(cart).forEach(([id, produit]) => {
    const tr = document.createElement('tr');
    tr.setAttribute("data-id", id);
    tr.innerHTML = `
      <td>${produit.nom}</td>
      <td>${produit.prix.toLocaleString()} FC</td>
      <td>
        <div class="input-group input-group-sm" style="max-width: 120px;">
          <button class="btn btn-outline-secondary" onclick="changeQuantity('${id}', -1)">–</button>
          <input type="number" class="form-control text-center quantite-input" value="${produit.quantite}" min="1" onchange="updateCart('${id}', this.value)">
          <button class="btn btn-outline-secondary" onclick="changeQuantity('${id}', 1)">+</button>
        </div>
      </td>
      <td>${(produit.prix * produit.quantite).toLocaleString()} FC</td>
      <td>
        <button class="btn btn-sm btn-danger" onclick="removeFromCart('${id}')"><i class="bi bi-trash"></i></button>
      </td>
    `;
    tbody.appendChild(tr);
  });

  updateTotal();
}

function updateCart(id, quantite) {
  quantite = parseInt(quantite);
  if (isNaN(quantite) || quantite < 1) {
    quantite = 1;
  }
  if (cart[id]) {
    cart[id].quantite = quantite;
  }
  updateCartCount();
  renderCartModal();
}

function changeQuantity(id, delta) {
  if (!cart[id]) return;
  cart[id].quantite += delta;
  if (cart[id].quantite < 1) delete cart[id];
  updateCartCount();
  renderCartModal();
}

function removeFromCart(id) {
  delete cart[id];
  updateCartCount();
  renderCartModal();
}

function updateTotal() {
  const total = Object.values(cart).reduce((sum, p) => sum + p.prix * p.quantite, 0);
  document.getElementById('cartTotal').textContent = total.toLocaleString() + ' FC';
}

function increaseQuantity(btn) {
  const input = btn.parentElement.querySelector("input");
  input.value = parseInt(input.value) + 1;
}

function decreaseQuantity(btn) {
  const input = btn.parentElement.querySelector("input");
  if (parseInt(input.value) > 1) {
    input.value = parseInt(input.value) - 1;
  }
}

document.querySelectorAll('.btn-add-to-cart').forEach(btn => {
  btn.addEventListener('click', (e) => {
    e.preventDefault();
    const id = btn.getAttribute('data-id');
    const nom = btn.getAttribute('data-nom');
    const prix = parseFloat(btn.getAttribute('data-prix'));
    const quantite = parseInt(btn.closest('.card-body').querySelector('input[type=number]').value);
    addToCart(id, nom, prix, quantite);
  });
});

// RECHERCHE + FILTRE COMBINÉS
const searchInput = document.querySelector('.search-box input[type="search"]');
const productCards = document.querySelectorAll('.card');
const noResultsMsg = document.getElementById('no-results-message');
let currentCategory = 'all';

searchInput.addEventListener('input', filterProducts);

function filterByCategory(category) {
  currentCategory = category;
  filterProducts();

  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.classList.remove('btn-primary');
    btn.classList.add('btn-outline-secondary');
  });

  const activeBtn = Array.from(document.querySelectorAll('.filter-btn')).find(
    btn => btn.textContent.trim().toLowerCase() === getCategoryLabel(category)
  );
  if (activeBtn) {
    activeBtn.classList.remove('btn-outline-secondary');
    activeBtn.classList.add('btn-primary');
  }
}

function getCategoryLabel(cat) {
  switch (cat) {
    case 'all': return 'tous';
    case 'antalgique': return 'antalgiques';
    case 'vitamine': return 'vitamines';
    case 'antibiotique': return 'antibiotiques';
    default: return '';
  }
}

function filterProducts() {
  const keyword = searchInput.value.toLowerCase().trim();
  let found = false;

  productCards.forEach(card => {
    const title = card.querySelector('.card-title').textContent.toLowerCase();
    const category = card.getAttribute('data-category');

    const matchCategory = currentCategory === 'all' || category === currentCategory;
    const matchKeyword = title.includes(keyword);

    const visible = matchCategory && matchKeyword;
    card.parentElement.style.display = visible ? 'block' : 'none';
    if (visible) found = true;
  });

  noResultsMsg.style.display = found ? 'none' : 'block';
}

updateCartCount();

// dark theme
const toggleBtn = document.getElementById('themeToggle');
const themeIcon = document.getElementById('themeIcon');

if (localStorage.getItem('theme') === 'dark') {
  document.body.classList.add('dark-mode');
  themeIcon.classList.replace('bi-moon-fill', 'bi-sun-fill');
}

toggleBtn.addEventListener('click', () => {
  document.body.classList.toggle('dark-mode');
  const isDark = document.body.classList.contains('dark-mode');
  localStorage.setItem('theme', isDark ? 'dark' : 'light');
  themeIcon.classList.toggle('bi-moon-fill', !isDark);
  themeIcon.classList.toggle('bi-sun-fill', isDark);
});

function validerCommande() {
  const lignes = document.querySelectorAll("#cartModal tbody tr");
  const items = [];

  lignes.forEach(ligne => {
    const id = ligne.dataset.id;
    const quantite = parseInt(ligne.querySelector(".quantite-input").value);
    items.push({ id, quantite });
  });

  if (items.length === 0) {
    alert("Le panier est vide.");
    return;
  }

  fetch("/valider-commande/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken")
    },
    body: JSON.stringify({ panier: items })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      // ✅ Mettre à jour les stocks dans les cartes produits
      if (data.stocks) {
        mettreAJourStocks(data.stocks);
      }

      // ✅ Réinitialiser le panier
      cart = {};
      updateCartCount();
      renderCartModal();

      // ✅ Afficher le toast de succès
      const toastElement = document.getElementById("successToast");
      const toast = new bootstrap.Toast(toastElement);
      toast.show();

    } else {
      alert("Erreur : " + data.error);
    }
  })
  .catch(err => {
    alert("Erreur réseau : " + err);
  });
}




function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
