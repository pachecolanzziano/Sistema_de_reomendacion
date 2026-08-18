async function buscarRecomendaciones() {
  const input = document.getElementById('customerInput');
  const btn = document.getElementById('searchBtn');
  const customerId = input.value.trim();
  const statusMsg = document.getElementById('statusMsg');
  const alsSection = document.getElementById('alsSection');
  const crossSellSection = document.getElementById('crossSellSection');

  crossSellSection.style.display = 'none';
  alsSection.style.display = 'none';
  statusMsg.innerHTML = '';

  if (!customerId) {
    statusMsg.innerHTML = '<div class="status error">Escribe un Customer ID.</div>';
    return;
  }

  btn.disabled = true;
  statusMsg.innerHTML = '<div class="status">Buscando recomendaciones...</div>';

  try {
    const res = await fetch(`/api/recommendations/${encodeURIComponent(customerId)}`);
    if (!res.ok) throw new Error('Error de servidor');

    const data = await res.json();

    // 🔥 Limpiar mensajes anteriores
    statusMsg.innerHTML = '';

    // 🔥 Mostrar mensaje según el status
    if (data.status && data.message) {
      const msgDiv = document.createElement('div');
      msgDiv.className = `status ${data.status === 'existing' ? 'success' : 'info'}`;
      msgDiv.textContent = data.status === 'existing' 
        ? `👤 Usuario registrado. ${data.message}` 
        : `🆕 Usuario nuevo. ${data.message}`;
      statusMsg.appendChild(msgDiv);
    }

    // 🔥 Renderizar productos (usando data.recommendations o data si es array)
    const productos = data.recommendations || data;
    if (Array.isArray(productos)) {
    renderAlsGrid(productos);
    alsSection.style.display = 'block';
    } else {
      throw new Error('La respuesta no contiene productos');
    }
  } catch (err) {
    statusMsg.innerHTML = '<div class="status error">Algo salió mal al buscar las recomendaciones. Intenta de nuevo.</div>';
  } finally {
    btn.disabled = false;
  }
}

function renderAlsGrid(productos) {
  const grid = document.getElementById('alsGrid');
  grid.innerHTML = '';
  productos.forEach(p => {
    const card = document.createElement('div');
    card.className = 'product-card clickable';
    card.textContent = p.description;
    card.onclick = () => seleccionarProducto(p, card);
    grid.appendChild(card);
  });
}

async function seleccionarProducto(producto, cardEl) {
  document.querySelectorAll('#alsGrid .product-card').forEach(c => c.classList.remove('selected'));
  cardEl.classList.add('selected');

  const crossSellSection = document.getElementById('crossSellSection');
  const crumb = document.getElementById('crossSellCrumb');
  const grid = document.getElementById('crossSellGrid');

  crumb.textContent = producto.description;
  grid.innerHTML = '<div class="status">Buscando productos relacionados...</div>';
  crossSellSection.style.display = 'block';
  crossSellSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

  try {
    const res = await fetch(`/api/products/${encodeURIComponent(producto.stock_code)}/cross-sell`);
    if (!res.ok) throw new Error('Error de servidor');
    const relacionados = await res.json();

    if (relacionados.length === 0) {
      grid.innerHTML = '<div class="status">Todavía no hay suficientes datos de co-compra para este producto.</div>';
      return;
    }

    grid.innerHTML = '';
    relacionados.forEach(p => {
      const card = document.createElement('div');
      card.className = 'product-card cross-sell-card';
      card.textContent = p.description;
      grid.appendChild(card);
    });
  } catch (err) {
    grid.innerHTML = '<div class="status error">Algo salió mal al buscar productos relacionados.</div>';
  }
}

document.getElementById('customerInput').addEventListener('keydown', e => {
  if (e.key === 'Enter') buscarRecomendaciones();
});

document.getElementById('searchBtn').addEventListener('click', buscarRecomendaciones);
