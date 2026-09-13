const grid = document.querySelector('#product-grid');
const form = document.querySelector('#search-form');
const queryInput = document.querySelector('#query');
const categorySelect = document.querySelector('#category');
const summary = document.querySelector('#result-summary');
const count = document.querySelector('#result-count');

const artClasses = ['tone-0', 'tone-1', 'tone-2', 'tone-3'];

function money(value) {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value);
}

function card(product, index) {
  return `<article class="product-card">
    <div class="product-art ${artClasses[index % artClasses.length]}">
      <span class="match">${product.match_score ? `${product.match_score}% MATCH` : 'TOP RATED'}</span>
      <button class="bookmark" aria-label="Save ${product.name}">+</button>
      <div class="art-shape"></div>
    </div>
    <div class="product-meta">
      <h3>${product.name}</h3>
      <p>${product.brand} / ${product.category}</p>
      <div class="price-row"><span>${money(product.price)}</span><span class="rating">★ ${product.rating} · ${product.reviews.toLocaleString()}</span></div>
    </div>
  </article>`;
}

async function loadCategories() {
  const response = await fetch('/api/catalog');
  const data = await response.json();
  data.categories.forEach(category => {
    const option = document.createElement('option');
    option.value = category;
    option.textContent = category;
    categorySelect.append(option);
  });
}

async function loadRecommendations() {
  grid.innerHTML = '<div class="loading">Reading product signals...</div>';
  const params = new URLSearchParams({ q: queryInput.value, category: categorySelect.value, limit: 8 });
  const response = await fetch(`/api/recommendations?${params}`);
  const data = await response.json();
  grid.innerHTML = data.recommendations.map(card).join('');
  count.textContent = `${data.recommendations.length} FOUND`;
  summary.textContent = queryInput.value.trim()
    ? `Showing the closest matches for “${queryInput.value.trim()}”.`
    : 'A quiet starting point, based on the strongest product signals.';
}

form.addEventListener('submit', event => { event.preventDefault(); loadRecommendations(); });
categorySelect.addEventListener('change', loadRecommendations);
document.querySelectorAll('[data-query]').forEach(button => {
  button.addEventListener('click', () => { queryInput.value = button.dataset.query; loadRecommendations(); });
});

loadCategories().then(loadRecommendations).catch(() => {
  grid.innerHTML = '<p>Could not connect to the recommendation engine.</p>';
});
