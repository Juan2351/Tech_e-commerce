/**
 * Amazon Tech Products - Frontend
 * Arquitectura desacoplada conectada a la API RESTful de la base de datos
 * Soporte dual: API REST (primario) con contingencia de carga local CSV
 */

const API_BASE = "/api/v1";
const USD_TO_COP = 4350;

// Estado de la aplicacion
const state = {
  mode: "api", // "api" | "fallback"
  allProductsFallback: [],
  currentProducts: [],
  total: 0,
  totalPages: 1,
  currentPage: 1,
  pageSize: 24,
  view: "grid", // "grid" | "table"
  searchQuery: "",
  brand: "",
  category: "",
  subcategory: "",
  minRating: 0,
  sortBy: "default",
};

// Referencias DOM
const $loading      = document.getElementById("loading");
const $gridView     = document.getElementById("grid-view");
const $tableView    = document.getElementById("table-view");
const $tableBody    = document.getElementById("table-body");
const $noResults    = document.getElementById("no-results");
const $pagination   = document.getElementById("pagination");
const $pageNumbers  = document.getElementById("page-numbers");
const $btnPrev      = document.getElementById("btn-prev");
const $btnNext      = document.getElementById("btn-next");
const $pageInfoText = document.getElementById("page-info-text");
const $resultsCount = document.getElementById("results-count");
const $searchInput  = document.getElementById("search-input");
const $filterBrand  = document.getElementById("filter-brand");
const $filterCat    = document.getElementById("filter-category");
const $filterSub    = document.getElementById("filter-subcategory");
const $filterRating = document.getElementById("filter-rating");
const $sortBy       = document.getElementById("sort-by");
const $btnReset     = document.getElementById("btn-reset");
const $btnClearNR   = document.getElementById("btn-clear-no-results");
const $btnGrid      = document.getElementById("btn-grid");
const $btnTable     = document.getElementById("btn-table");
const $pageSizeSel  = document.getElementById("page-size-select");
const $modal        = document.getElementById("product-modal");
const $modalClose   = document.getElementById("modal-close");
const $statTotal    = document.getElementById("stat-total");
const $statBrands   = document.getElementById("stat-brands");
const $statCats     = document.getElementById("stat-categories");
const $statAvgPrice = document.getElementById("stat-avg-price");
const $footerYear   = document.getElementById("footer-year");
const $dbBadge      = document.getElementById("db-status-badge");

// -------------------------------------------------------------
// Inicializacion
// -------------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
  if ($footerYear) {
    $footerYear.textContent = new Date().getFullYear();
  }
  bindEvents();
  inicializarAplicacion();
});

async function inicializarAplicacion() {
  mostrarCargando(true);
  try {
    // 1. Probar conexion con la API REST del backend
    const resSalud = await fetch(`${API_BASE}/salud`, { signal: AbortSignal.timeout(3000) });
    if (!resSalud.ok) throw new Error("API no respondio estado operativo");

    const datosSalud = await resSalud.json();
    state.mode = "api";
    actualizarBadge(true, datosSalud.base_de_datos?.motor || "SQL");

    // 2. Cargar filtros y estadisticas desde la base de datos
    await Promise.all([
      cargarMetadatosDesdeAPI(),
      cargarEstadisticasDesdeAPI(),
      cargarProductos()
    ]);
  } catch (err) {
    console.warn("API REST no disponible en http://localhost:5000. Activando contingencia CSV local.", err);
    state.mode = "fallback";
    actualizarBadge(false);
    await iniciarModoContingenciaCSV();
  } finally {
    mostrarCargando(false);
  }
}

function actualizarBadge(conectado, motor = "SQL") {
  if (!$dbBadge) return;
  if (conectado) {
    $dbBadge.textContent = `BD: Conectada (${motor})`;
    $dbBadge.className = "db-badge connected";
  } else {
    $dbBadge.textContent = "BD: Modo Local (CSV)";
    $dbBadge.className = "db-badge fallback";
  }
}

function mostrarCargando(activo) {
  if (!$loading) return;
  if (activo) {
    $loading.classList.remove("hidden");
  } else {
    $loading.classList.add("hidden");
  }
}

// -------------------------------------------------------------
// Carga de Datos desde API REST
// -------------------------------------------------------------
async function cargarMetadatosDesdeAPI() {
  try {
    const [resMarcas, resCats] = await Promise.all([
      fetch(`${API_BASE}/marcas`),
      fetch(`${API_BASE}/categorias`)
    ]);

    if (resMarcas.ok) {
      const marcas = await resMarcas.json();
      poblarSelectMarcas(marcas.map(m => m.nombre));
    }

    if (resCats.ok) {
      const cats = await resCats.json();
      poblarSelectCategorias(cats);
    }
  } catch (e) {
    console.error("Error al cargar metadatos de marcas y categorias:", e);
  }
}

async function cargarEstadisticasDesdeAPI() {
  try {
    const res = await fetch(`${API_BASE}/estadisticas`);
    if (!res.ok) return;
    const s = await res.json();
    $statTotal.textContent = formatearNumero(s.total_productos || 0);
    $statBrands.textContent = formatearNumero(s.total_marcas || 0);
    $statCats.textContent = formatearNumero(s.total_categorias || 0);
    const avgCop = Math.round((parseFloat(s.precio_promedio_usd) || 0) * USD_TO_COP);
    $statAvgPrice.textContent = `$ ${avgCop.toLocaleString("es-CO")}`;
  } catch (e) {
    console.error("Error al cargar estadisticas:", e);
  }
}

async function cargarProductos() {
  mostrarCargando(true);

  if (state.mode === "api") {
    try {
      const params = new URLSearchParams({
        page: state.currentPage,
        limit: state.pageSize,
        q: state.searchQuery,
        marca: state.brand,
        categoria: state.category,
        subcategoria: state.subcategory,
        min_rating: state.minRating,
        sort: state.sortBy
      });

      const res = await fetch(`${API_BASE}/productos?${params.toString()}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();
      state.currentProducts = data.data || [];
      state.total = data.total || 0;
      state.totalPages = data.totalPages || 1;

      renderizarResultados();
    } catch (e) {
      console.error("Error consultando productos de la API:", e);
      // Fallback si la API se cae durante la ejecucion
      state.mode = "fallback";
      actualizarBadge(false);
      await iniciarModoContingenciaCSV();
    } finally {
      mostrarCargando(false);
    }
  } else {
    filtrarLocalmenteCSV();
    mostrarCargando(false);
  }
}

// -------------------------------------------------------------
// Contingencia Local CSV
// -------------------------------------------------------------
async function iniciarModoContingenciaCSV() {
  try {
    const res = await fetch("/conjunto_datos/amazon_tech_products_ecommerceGKALI.csv");
    if (!res.ok) throw new Error("No se pudo leer el CSV");
    const text = await res.text();
    state.allProductsFallback = parsearCSV(text);

    // Poblar filtros
    const brands = [...new Set(state.allProductsFallback.map(p => p.brand_name).filter(Boolean))].sort();
    poblarSelectMarcas(brands);

    const catsUnicas = [...new Set(state.allProductsFallback.map(p => p.main_category).filter(Boolean))].sort();
    $filterCat.innerHTML = '<option value="">Todas</option>';
    catsUnicas.forEach(c => {
      const o = document.createElement("option");
      o.value = c;
      o.textContent = c;
      $filterCat.appendChild(o);
    });

    // Actualizar estadisticas
    const p = state.allProductsFallback;
    const brandsSet = new Set(p.map(x => x.brand_name)).size;
    const catsSet = new Set(p.map(x => x.main_category)).size;
    const avg = p.reduce((s, x) => s + (parseFloat(x.price_numeric) || 0), 0) / (p.length || 1);
    const avgCop = Math.round(avg * USD_TO_COP);

    $statTotal.textContent = formatearNumero(p.length);
    $statBrands.textContent = formatearNumero(brandsSet);
    $statCats.textContent = formatearNumero(catsSet);
    $statAvgPrice.textContent = `$ ${avgCop.toLocaleString("es-CO")}`;

    filtrarLocalmenteCSV();
  } catch (err) {
    $loading.innerHTML = `<p style="color:#d32f2f">No se pudo inicializar la fuente de datos: ${err.message}</p>`;
  }
}

function filtrarLocalmenteCSV() {
  const query = state.searchQuery.toLowerCase();
  let filtrados = state.allProductsFallback.filter(p => {
    if (state.brand && p.brand_name !== state.brand) return false;
    if (state.category && p.main_category !== state.category) return false;
    if (state.subcategory && p.subcategory !== state.subcategory) return false;
    if (state.minRating && (parseFloat(p.rating) || 0) < state.minRating) return false;
    if (query) {
      const texto = `${p.product_description} ${p.brand_name} ${p.subcategory}`.toLowerCase();
      if (!texto.includes(query)) return false;
    }
    return true;
  });

  // Ordenamiento local
  switch (state.sortBy) {
    case "price-asc":
      filtrados.sort((a, b) => (parseFloat(a.price_numeric) || 0) - (parseFloat(b.price_numeric) || 0));
      break;
    case "price-desc":
      filtrados.sort((a, b) => (parseFloat(b.price_numeric) || 0) - (parseFloat(a.price_numeric) || 0));
      break;
    case "rating-desc":
      filtrados.sort((a, b) => (parseFloat(b.rating) || 0) - (parseFloat(a.rating) || 0));
      break;
    case "reviews-desc":
      filtrados.sort((a, b) => (parseInt(b.reviews_count) || 0) - (parseInt(a.reviews_count) || 0));
      break;
    case "stock-desc":
      filtrados.sort((a, b) => (parseInt(b.stock) || 0) - (parseInt(a.stock) || 0));
      break;
  }

  state.total = filtrados.length;
  state.totalPages = Math.max(1, Math.ceil(state.total / state.pageSize));
  state.currentPage = Math.min(state.currentPage, state.totalPages);

  const inicio = (state.currentPage - 1) * state.pageSize;
  state.currentProducts = filtrados.slice(inicio, inicio + state.pageSize).map(p => ({
    id_producto: p.id,
    descripcion: p.product_description,
    marca: p.brand_name,
    categoria: p.main_category,
    subcategoria: p.subcategory,
    precio: parseFloat(p.price_numeric) || 0,
    rating: parseFloat(p.rating) || 0,
    reviews_count: parseInt(p.reviews_count) || 0,
    stock: parseInt(p.stock) || 0,
    url: p.url,
    image_url: p.image_url
  }));

  renderizarResultados();
}

// -------------------------------------------------------------
// Renderizado de Resultados
// -------------------------------------------------------------
function renderizarResultados() {
  const total = state.total;
  const start = total === 0 ? 0 : (state.currentPage - 1) * state.pageSize + 1;
  const end = Math.min(start + state.pageSize - 1, total);

  $resultsCount.textContent = `Mostrando ${start}-${end} de ${formatearNumero(total)} productos`;

  if (total === 0) {
    $noResults.classList.remove("hidden");
    $gridView.classList.add("hidden");
    $tableView.classList.add("hidden");
    $pagination.hidden = true;
    return;
  }

  $noResults.classList.add("hidden");

  if (state.view === "grid") {
    $gridView.classList.remove("hidden");
    $tableView.classList.add("hidden");
    renderizarCuadricula(state.currentProducts);
  } else {
    $tableView.classList.remove("hidden");
    $gridView.classList.add("hidden");
    renderizarTabla(state.currentProducts);
  }

  renderizarPaginacion(state.currentPage, state.totalPages);
  $pageInfoText.textContent = `Pagina ${state.currentPage} de ${state.totalPages}`;
  $pagination.hidden = state.totalPages <= 1;
}

function renderizarCuadricula(productos) {
  $gridView.innerHTML = productos.map((p, i) => {
    const sc = claseStock(p.stock);
    const cop = formatearPrecioCOP(p.precio);
    return `
      <article class="product-card" role="button" tabindex="0" data-id="${sanitizar(p.id_producto)}">
        <div class="card-img-wrapper">
          <img class="card-img" src="${sanitizar(p.image_url)}" alt="${sanitizar(p.marca)}" loading="lazy"
               onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%22120%22 height=%22120%22><rect width=%22120%22 height=%22120%22 fill=%22%23eee%22/><text x=%2260%22 y=%2265%22 text-anchor=%22middle%22 font-size=%2214%22 fill=%22%23888%22>Sin Imagen</text></svg>'" />
          <span class="card-badge">${sanitizar(p.subcategoria || p.categoria || "Tecnologia")}</span>
        </div>
        <div class="card-body">
          <span class="card-brand">${sanitizar(p.marca || "Generico")}</span>
          <p class="card-title">${sanitizar(p.descripcion)}</p>
          <div class="card-footer">
            <span class="card-price">${cop}</span>
            <span class="card-rating">
              <span>Rating: ${p.rating} / 5</span>
            </span>
          </div>
          <span class="card-stock ${sc}">Stock: ${p.stock}</span>
        </div>
      </article>
    `;
  }).join("");

  $gridView.querySelectorAll(".product-card").forEach(card => {
    const id = card.dataset.id;
    const abrir = () => abrirDetalleProducto(id);
    card.addEventListener("click", abrir);
    card.addEventListener("keydown", e => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        abrir();
      }
    });
  });
}

function renderizarTabla(productos) {
  $tableBody.innerHTML = productos.map(p => {
    const sc = claseStock(p.stock);
    const cop = formatearPrecioCOP(p.precio);
    return `
      <tr data-id="${sanitizar(p.id_producto)}" tabindex="0">
        <td>
          <img class="td-img" src="${sanitizar(p.image_url)}" alt="${sanitizar(p.marca)}" loading="lazy"
               onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%2260%22 height=%2250%22><rect width=%2260%22 height=%2250%22 fill=%22%23eee%22/><text x=%2230%22 y=%2230%22 text-anchor=%22middle%22 font-size=%2210%22 fill=%22%23888%22>N/A</text></svg>'" />
        </td>
        <td class="td-name"><span class="td-name-text">${sanitizar(p.descripcion)}</span></td>
        <td class="td-brand">${sanitizar(p.marca || "Generico")}</td>
        <td class="td-cat">${sanitizar(p.subcategoria || p.categoria)}</td>
        <td class="td-price">${cop}</td>
        <td class="td-rating">${p.rating} / 5</td>
        <td class="td-reviews">${formatearNumero(p.reviews_count)}</td>
        <td><span class="stock-badge ${sc}">${p.stock}</span></td>
        <td class="td-link">
          <a href="${sanitizar(p.url)}" target="_blank" rel="noopener noreferrer" title="Ver en Amazon" onclick="event.stopPropagation()">Ver</a>
        </td>
      </tr>
    `;
  }).join("");

  $tableBody.querySelectorAll("tr").forEach(row => {
    const id = row.dataset.id;
    const abrir = () => abrirDetalleProducto(id);
    row.addEventListener("click", abrir);
    row.addEventListener("keydown", e => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        abrir();
      }
    });
  });
}

function renderizarPaginacion(actual, total) {
  $btnPrev.disabled = actual <= 1;
  $btnNext.disabled = actual >= total;

  const botones = [];
  const rango = 2;

  for (let i = 1; i <= total; i++) {
    if (i === 1 || i === total || (i >= actual - rango && i <= actual + rango)) {
      botones.push(i);
    } else if (botones[botones.length - 1] !== "...") {
      botones.push("...");
    }
  }

  $pageNumbers.innerHTML = botones.map(n => {
    if (n === "...") return `<span class="page-num ellipsis" aria-hidden="true">...</span>`;
    return `<button class="page-num${n === actual ? " active" : ""}" data-page="${n}" type="button">${n}</button>`;
  }).join("");

  $pageNumbers.querySelectorAll(".page-num[data-page]").forEach(btn => {
    btn.addEventListener("click", () => {
      state.currentPage = parseInt(btn.dataset.page);
      cargarProductos();
      desplazarHaciaCatalogo();
    });
  });
}

// -------------------------------------------------------------
// Modal de Detalle de Producto
// -------------------------------------------------------------
async function abrirDetalleProducto(idProducto) {
  if (!idProducto) return;

  // Intentar consultar detalle actualizado desde la API
  let p = null;
  if (state.mode === "api") {
    try {
      const res = await fetch(`${API_BASE}/productos/${encodeURIComponent(idProducto)}`);
      if (res.ok) p = await res.json();
    } catch (e) {
      console.warn("Fallo al obtener detalle por API:", e);
    }
  }

  if (!p) {
    p = state.currentProducts.find(x => x.id_producto === idProducto);
  }
  if (!p) return;

  document.getElementById("modal-category").textContent = `${p.categoria || ""} > ${p.subcategoria || ""}`;
  document.getElementById("modal-title").textContent = p.descripcion;
  document.getElementById("modal-img").src = p.image_url || "";
  document.getElementById("modal-img").alt = p.marca || "Producto";
  document.getElementById("modal-link").href = p.url || "#";

  const cop = Math.round((parseFloat(p.precio) || 0) * USD_TO_COP);
  const usd = (parseFloat(p.precio) || 0).toFixed(2);
  document.getElementById("modal-price").innerHTML = `$ ${cop.toLocaleString("es-CO")} <small>(USD ${usd})</small>`;

  const ratingRow = document.getElementById("modal-rating-row");
  ratingRow.innerHTML = `<strong>Calificacion: ${p.rating} / 5.0</strong> <span>(${formatearNumero(p.reviews_count)} resenas verificadas)</span>`;

  const details = document.getElementById("modal-details");
  details.innerHTML = `
    <dt>Marca</dt><dd>${p.marca || "No especificada"}</dd>
    <dt>Categoria</dt><dd>${p.categoria || ""} - ${p.subcategoria || ""}</dd>
    <dt>Codigo de Producto</dt><dd>${p.id_producto}</dd>
    <dt>Disponibilidad</dt><dd>${p.stock} unidades en inventario</dd>
  `;

  $modal.showModal();
}

function cerrarModal() {
  $modal.close();
}

// -------------------------------------------------------------
// Utilidades de Datos y UI
// -------------------------------------------------------------
function poblarSelectMarcas(marcas) {
  $filterBrand.innerHTML = '<option value="">Todas las marcas</option>';
  marcas.forEach(b => {
    const o = document.createElement("option");
    o.value = b;
    o.textContent = b;
    $filterBrand.appendChild(o);
  });
}

function poblarSelectCategorias(categorias) {
  $filterCat.innerHTML = '<option value="">Todas</option>';
  $filterSub.innerHTML = '<option value="">Todas</option>';

  categorias.forEach(c => {
    const o = document.createElement("option");
    o.value = c.nombre;
    o.textContent = c.nombre;
    $filterCat.appendChild(o);
  });

  // Manejar cambio dinamico de subcategorias
  $filterCat.addEventListener("change", () => {
    const seleccionada = $filterCat.value;
    $filterSub.innerHTML = '<option value="">Todas</option>';
    if (!seleccionada) return;

    const catObj = categorias.find(c => c.nombre === seleccionada);
    if (catObj && catObj.subcategorias) {
      catObj.subcategorias.forEach(sub => {
        const o = document.createElement("option");
        o.value = sub.nombre;
        o.textContent = `${sub.nombre} (${sub.total_productos})`;
        $filterSub.appendChild(o);
      });
    }
  });
}

function claseStock(s) {
  const n = parseInt(s, 10);
  if (n >= 50) return "stock-high";
  if (n >= 20) return "stock-med";
  return "stock-low";
}

function formatearPrecioCOP(usdVal) {
  const num = parseFloat(usdVal);
  if (isNaN(num)) return "-";
  const cop = Math.round(num * USD_TO_COP);
  return "$ " + cop.toLocaleString("es-CO");
}

function formatearNumero(n) {
  return Number(n || 0).toLocaleString("es-CO");
}

function sanitizar(str) {
  if (!str) return "";
  const d = document.createElement("div");
  d.textContent = str;
  return d.innerHTML;
}

function desplazarHaciaCatalogo() {
  const el = document.getElementById("catalog");
  if (el) window.scrollTo({ top: el.offsetTop - 80, behavior: "smooth" });
}

function parsearCSV(text) {
  const lineas = [];
  let i = 0;
  const n = text.length;

  while (i < n) {
    const fila = [];
    while (i < n && text[i] !== "\n") {
      if (text[i] === '"') {
        let val = "";
        i++;
        while (i < n) {
          if (text[i] === '"' && text[i + 1] === '"') { val += '"'; i += 2; }
          else if (text[i] === '"') { i++; break; }
          else { val += text[i]; i++; }
        }
        fila.push(val);
        if (text[i] === ",") i++;
      } else {
        let val = "";
        while (i < n && text[i] !== "," && text[i] !== "\n") { val += text[i]; i++; }
        fila.push(val.trim());
        if (text[i] === ",") i++;
      }
    }
    if (text[i] === "\n") i++;
    if (fila.length > 1) lineas.push(fila);
  }

  if (lineas.length < 2) return [];
  const cabeceras = lineas[0].map(h => h.trim());
  return lineas.slice(1).map(fila => {
    const obj = {};
    cabeceras.forEach((h, idx) => { obj[h] = (fila[idx] || "").trim(); });
    return obj;
  });
}

// -------------------------------------------------------------
// Asignacion de Eventos
// -------------------------------------------------------------
function bindEvents() {
  let searchTimer;
  $searchInput.addEventListener("input", () => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
      state.searchQuery = $searchInput.value.trim();
      state.currentPage = 1;
      cargarProductos();
    }, 280);
  });

  $filterBrand.addEventListener("change", () => {
    state.brand = $filterBrand.value;
    state.currentPage = 1;
    cargarProductos();
  });

  $filterCat.addEventListener("change", () => {
    state.category = $filterCat.value;
    state.subcategory = "";
    state.currentPage = 1;
    cargarProductos();
  });

  $filterSub.addEventListener("change", () => {
    state.subcategory = $filterSub.value;
    state.currentPage = 1;
    cargarProductos();
  });

  $filterRating.addEventListener("change", () => {
    state.minRating = parseFloat($filterRating.value) || 0;
    state.currentPage = 1;
    cargarProductos();
  });

  $sortBy.addEventListener("change", () => {
    state.sortBy = $sortBy.value;
    state.currentPage = 1;
    cargarProductos();
  });

  const resetearFiltros = () => {
    $searchInput.value = "";
    $filterBrand.value = "";
    $filterCat.value = "";
    $filterSub.value = "";
    $filterRating.value = "0";
    $sortBy.value = "default";

    state.searchQuery = "";
    state.brand = "";
    state.category = "";
    state.subcategory = "";
    state.minRating = 0;
    state.sortBy = "default";
    state.currentPage = 1;

    cargarProductos();
  };

  $btnReset.addEventListener("click", resetearFiltros);
  $btnClearNR.addEventListener("click", resetearFiltros);

  $btnPrev.addEventListener("click", () => {
    if (state.currentPage > 1) {
      state.currentPage--;
      cargarProductos();
      desplazarHaciaCatalogo();
    }
  });

  $btnNext.addEventListener("click", () => {
    if (state.currentPage < state.totalPages) {
      state.currentPage++;
      cargarProductos();
      desplazarHaciaCatalogo();
    }
  });

  $pageSizeSel.addEventListener("change", () => {
    state.pageSize = parseInt($pageSizeSel.value);
    state.currentPage = 1;
    cargarProductos();
  });

  $btnGrid.addEventListener("click", () => {
    state.view = "grid";
    $btnGrid.classList.add("active");
    $btnGrid.setAttribute("aria-pressed", "true");
    $btnTable.classList.remove("active");
    $btnTable.setAttribute("aria-pressed", "false");
    renderizarResultados();
  });

  $btnTable.addEventListener("click", () => {
    state.view = "table";
    $btnTable.classList.add("active");
    $btnTable.setAttribute("aria-pressed", "true");
    $btnGrid.classList.remove("active");
    $btnGrid.setAttribute("aria-pressed", "false");
    renderizarResultados();
  });

  $modalClose.addEventListener("click", cerrarModal);
  $modal.addEventListener("click", e => { if (e.target === $modal) cerrarModal(); });
  document.addEventListener("keydown", e => { if (e.key === "Escape") cerrarModal(); });

  document.querySelectorAll(".sortable[data-sort]").forEach(th => {
    th.addEventListener("click", () => {
      const mapa = {
        price: "price-asc",
        rating: "rating-desc",
        reviews: "reviews-desc",
        stock: "stock-desc"
      };
      const clave = th.dataset.sort;
      if (mapa[clave]) {
        state.sortBy = mapa[clave];
        $sortBy.value = state.sortBy;
        state.currentPage = 1;
        cargarProductos();
      }
    });
  });
}
